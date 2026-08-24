import urllib.request
import json
import sys
import io

# Forcer l'encodage de la sortie standard en UTF-8 pour Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

URL = "http://127.0.0.1:8000/chat"

test_cases = [
    {"message": "Comment obtenir un e-Visa pour le Maroc ?", "lang": "fr"},
    {"message": "Quels sont les services CIP proposés aux passagers ?", "lang": "fr"},
    {"message": "ما هي الخدمات المتوفرة في المطار؟", "lang": "ar"},
    {"message": "Quel est le statut du vol AT780 ?", "lang": "fr"},
    {"message": "Racontes-moi une histoire de recettes de cuisine à Paris", "lang": "fr"}
]

print("=== TEST COMPLET DE L'ENDPOINT /chat (RAG + INTENT + LLM) ===\n")

for tc in test_cases:
    print(f"--------------------------------------------------")
    print(f"MESSAGE USER: {tc['message']} (Langue: {tc['lang']})")
    
    data = json.dumps(tc).encode('utf-8')
    req = urllib.request.Request(URL, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            res_json = json.loads(res_body)
            print(f"\nREPONSE DU BOT:\n{res_json.get('reply')}\n")
            print(f"LANGUE REPONSE: {res_json.get('lang')}")
            print(f"SOURCES UTILISEES: {res_json.get('sources')}")
    except Exception as e:
        print(f"ERREUR: {e}")
    print()
