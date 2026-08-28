import { ShoppingBag, Coffee, Car, Wifi, ShieldCheck, HelpCircle } from "lucide-react";
import GlassCard from "./GlassCard";

const services = [
  {
    id: "dutyfree",
    title: "Duty Free & Boutiques",
    desc: "Produits locaux marocains, cosmétiques, parfums et souvenirs artisanaux.",
    icon: ShoppingBag,
    color: "#f59e0b",
    query: "Quelles sont les boutiques Duty Free disponibles à l'aéroport d'Agadir ?",
  },
  {
    id: "lounge",
    title: "Salons VIP & Restauration",
    desc: "Salons de détente privatifs, cafés ONDA et espaces snack.",
    icon: Coffee,
    color: "#f43f5e",
    query: "Où se situent les salons VIP et espaces de restauration à AGA ?",
  },
  {
    id: "transport",
    title: "Taxis & Location de voitures",
    desc: "Station de taxis officiels 24/7 à la sortie Arrivées et agences de location.",
    icon: Car,
    color: "#eab308",
    query: "Quels sont les tarifs et l'emplacement des taxis et locations de voiture ?",
  },
  {
    id: "wifi",
    title: "Wi-Fi Gratuit & Connectivité",
    desc: "Réseau Wi-Fi haut débit ONDA_WIFI accessible dans tout l'aérogare.",
    icon: Wifi,
    color: "#22d3ee",
    query: "Comment me connecter au réseau Wi-Fi gratuit de l'aéroport ?",
  },
  {
    id: "customs",
    title: "Douane & Formalités",
    desc: "Réglementations devises, franchise bagage et contrôle passeport.",
    icon: ShieldCheck,
    color: "#22c55e",
    query: "Quelles sont les règles douanières et de devises à l'arrivée au Maroc ?",
  },
  {
    id: "assistance",
    title: "Assistance PMR & Informations",
    desc: "Accompagnement mobilité réduite et comptoir d'information voyageur.",
    icon: HelpCircle,
    color: "#60a5fa",
    query: "Comment bénéficier de l'assistance PMR ou contacter le comptoir d'information ?",
  },
];

export default function AirportServices({ onAskService }) {
  return (
    <div className="airport-services">
      <div className="services-header">
        <span className="section-eyebrow">AIRPORT SERVICES</span>
        <h2>Services & Équipements</h2>
        <p>Découvrez les installations et commodités de l&apos;Aéroport Agadir Al Massira</p>
      </div>

      <div className="services-grid">
        {services.map((srv) => {
          const Icon = srv.icon;
          return (
            <GlassCard
              key={srv.id}
              className="service-card"
              onClick={() => onAskService?.(srv.query)}
            >
              <div
                className="service-icon"
                style={{ color: srv.color, background: `${srv.color}18` }}
              >
                <Icon size={24} />
              </div>
              <div className="service-content">
                <h4>{srv.title}</h4>
                <p>{srv.desc}</p>
              </div>
              <div className="service-action">
                <span>Poser une question</span>
                <span>→</span>
              </div>
            </GlassCard>
          );
        })}
      </div>
    </div>
  );
}
