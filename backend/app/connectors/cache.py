"""
Cache TTL (durée de vie limitée) pour les connecteurs API live.

Pourquoi un cache ici :
Les API gratuites (AeroDataBox : 600 unités/mois, OpenWeatherMap :
~60 appels/min) ont des quotas serrés. Sans cache, chaque question
d'un voyageur sur son vol ferait un appel API — avec plusieurs
voyageurs posant la même question sur le même vol, on grillerait le
quota en quelques heures. Le §5.2 du cahier des charges recommande un
cache Redis de 3-5 minutes : assez court pour rester "temps réel" du
point de vue du voyageur, assez long pour économiser le quota.

Deux implémentations, même interface (.get/.set) :
- RedisCache    : la vraie prod, connectée à settings.redis_url
- InMemoryCache : repli automatique si Redis n'est pas joignable (ex:
                  ce sandbox de dev, ou un poste local sans Redis
                  installé) — pratique pour développer/tester sans
                  monter toute l'infra tout de suite.

Limite du repli mémoire : non partagé entre plusieurs processus/workers
(chaque worker aurait son propre cache) et perdu au redémarrage. Bon
pour dev/test, PAS suffisant pour la prod avec plusieurs workers
Uvicorn — Redis devient alors nécessaire pour de vrai.
"""

import json
import time
from typing import Any, Optional, Protocol

from app.config import settings


class Cache(Protocol):
    def get(self, key: str) -> Optional[Any]: ...
    def set(self, key: str, value: Any, ttl_seconds: int) -> None: ...


class InMemoryCache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._store[key] = (time.time() + ttl_seconds, value)


class RedisCache:
    def __init__(self, redis_url: str) -> None:
        import redis  # import local : pas de dépendance dure si Redis n'est pas utilisé

        self._client = redis.from_url(redis_url, socket_connect_timeout=1)
        self._client.ping()  # lève une exception si Redis n'est pas joignable

    def get(self, key: str) -> Optional[Any]:
        raw = self._client.get(key)
        return json.loads(raw) if raw is not None else None

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._client.setex(key, ttl_seconds, json.dumps(value))


def get_cache(prefer_redis: bool = True) -> Cache:
    """Essaie Redis, se replie automatiquement sur le cache mémoire si
    indisponible (Redis non installé, non démarré, ou package `redis`
    non installé). Le repli est silencieux mais loggé une fois.

    IMPORTANT : le cache mémoire est un singleton au niveau du module
    (_MEMORY_CACHE_SINGLETON) — si on instanciait un InMemoryCache() neuf
    à chaque appel de get_cache(), il serait vide à chaque fois et ne
    servirait jamais à rien. C'est une erreur que j'ai commise puis
    corrigée pendant les tests de ce module (voir tests dans le README)."""
    if prefer_redis:
        try:
            return RedisCache(settings.redis_url)
        except Exception as e:
            print(f"[cache] Redis indisponible ({e}) — repli sur cache mémoire (dev/test uniquement).")
    return _MEMORY_CACHE_SINGLETON


_MEMORY_CACHE_SINGLETON = InMemoryCache()
