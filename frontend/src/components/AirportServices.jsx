import React from 'react';
import { ShoppingBag, Coffee, Car, Wifi, ShieldCheck, HelpCircle } from 'lucide-react';
import GlassCard from './GlassCard';

/**
 * Section d'information et services de l'aéroport Agadir Al Massira
 */
export default function AirportServices({ onAskService }) {
  const services = [
    {
      id: 'dutyfree',
      title: 'Duty Free & Boutiques',
      desc: 'Produits locaux marocains, cosmétiques, parfums et souvenirs artisanaux.',
      icon: <ShoppingBag className="w-6 h-6 text-amber-400" />,
      query: 'Quelles sont les boutiques Duty Free disponibles à l\'aéroport d\'Agadir ?',
    },
    {
      id: 'lounge',
      title: 'Salons VIP & Restauration',
      desc: 'Salons de détente privatifs, cafés ONDA et espaces snack.',
      icon: <Coffee className="w-6 h-6 text-rose-400" />,
      query: 'Où se situent les salons VIP et espaces de restauration à AGA ?',
    },
    {
      id: 'transport',
      title: 'Taxis & Location de voitures',
      desc: 'Station de taxis officiels 24/7 à la sortie Arrivées et agences de location.',
      icon: <Car className="w-6 h-6 text-yellow-400" />,
      query: 'Quels sont les tarifs et l\'emplacement des taxis et locations de voiture ?',
    },
    {
      id: 'wifi',
      title: 'Wi-Fi Gratuit & Connectivité',
      desc: 'Réseau Wi-Fi haut débit ONDA_WIFI accessible dans tout l\'aérogare.',
      icon: <Wifi className="w-6 h-6 text-cyan-400" />,
      query: 'Comment me connecter au réseau Wi-Fi gratuit de l\'aéroport ?',
    },
    {
      id: 'customs',
      title: 'Douane & Formalités',
      desc: 'Réglementations devises, franchise bagage et contrôle passeport.',
      icon: <ShieldCheck className="w-6 h-6 text-emerald-400" />,
      query: 'Quelles sont les règles douanières et de devises à l\'arrivée au Maroc ?',
    },
    {
      id: 'assistance',
      title: 'Assistance PMR & Informations',
      desc: 'Accompagnement mobilité réduite et comptoir d\'information voyageur.',
      icon: <HelpCircle className="w-6 h-6 text-blue-400" />,
      query: 'Comment bénéficier de l\'assistance PMR ou contacter le comptoir d\'information ?',
    },
  ];

  return (
    <section id="services" className="w-full max-w-5xl mx-auto my-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl md:text-3xl font-black text-white tracking-tight">
          SERVICES & ÉQUIPEMENTS AÉROPORTUAIRES
        </h2>
        <p className="text-sm text-white/60 mt-1">
          Découvrez les installations et commodités de l'Aéroport Agadir Al Massira
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {services.map((srv) => (
          <GlassCard
            key={srv.id}
            hoverEffect
            onClick={() => onAskService && onAskService(srv.query)}
            className="p-5 flex flex-col justify-between cursor-pointer group border-white/10"
          >
            <div>
              <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                {srv.icon}
              </div>
              <h4 className="font-extrabold text-base text-white group-hover:text-blue-400 transition-colors">
                {srv.title}
              </h4>
              <p className="text-xs text-white/60 mt-2 leading-relaxed">{srv.desc}</p>
            </div>

            <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-xs font-bold text-blue-400 opacity-80 group-hover:opacity-100 transition-opacity">
              <span>Poser une question</span>
              <span>→</span>
            </div>
          </GlassCard>
        ))}
      </div>
    </section>
  );
}
