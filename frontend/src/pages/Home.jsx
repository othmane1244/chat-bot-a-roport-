import { useMemo, useRef, useState } from "react";
import { Car, Coffee, Luggage, Plane, Search, ShieldCheck } from "lucide-react";

import AirportHeader from "../components/AirportHeader";
import AirportBackground from "../components/AirportBackground";
import AirportToday from "../components/AirportToday";
import ChatAssistant from "../components/ChatAssistant";
import DeparturesBoard from "../components/DeparturesBoard";
import FlightCard from "../components/FlightCard";
import AirportServices from "../components/AirportServices";
import WeatherWidget from "../components/WeatherWidget";

import { useChat } from "../hooks/useChat";
import { useWeather } from "../hooks/useWeather";

const quickActions = [
  {
    icon: Plane,
    title: "Flight status",
    description: "Check your flight",
    prompt: "I want to check my flight status",
  },
  {
    icon: Luggage,
    title: "Baggage",
    description: "Baggage information",
    prompt: "Where can I find baggage information?",
  },
  {
    icon: Car,
    title: "Transport",
    description: "Taxi and transport",
    prompt: "How can I travel from Agadir airport?",
  },
  {
    icon: ShieldCheck,
    title: "Security",
    description: "Security procedures",
    prompt: "What are the airport security procedures?",
  },
  {
    icon: Coffee,
    title: "Services",
    description: "Airport facilities",
    prompt: "What services are available at the airport?",
  },
];

export default function Home() {
  const assistantRef = useRef(null);
  const flightsRef = useRef(null);

  const [selectedFlight, setSelectedFlight] = useState(null);

  const { messages, loading: chatLoading, send } = useChat();

  const { weather, loading: weatherLoading, error: weatherError } = useWeather();

  const atmosphere = useMemo(() => weather?.atmosphere || "sunny", [weather]);

  const scrollToAssistant = () => {
    assistantRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const scrollToFlights = () => {
    flightsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const handleSend = async (text) => {
    const response = await send(text);
    if (response?.flight) {
      setSelectedFlight(response.flight);
    }
    return response;
  };

  const handleQuickAction = (action) => {
    scrollToAssistant();
    setTimeout(() => handleSend(action.prompt), 500);
  };

  return (
    <main className="airport-app">
      <AirportHeader
        onAssistantClick={scrollToAssistant}
        onFlightsClick={scrollToFlights}
      />

      {/* ======================================================
          HERO
      ====================================================== */}
      <section className={`hero-section atmosphere-${atmosphere}`}>
        <AirportBackground atmosphere={atmosphere} />

        <div className="hero-container">
          <div className="hero-content">
            <div className="hero-badge">
              <span className="hero-status-dot" />
              AGADIR AL MASSIRA AIRPORT
            </div>

            <h1>
              Your journey starts
              <span> with clarity.</span>
            </h1>

            <p>
              Your intelligent airport assistant for flights, services, baggage,
              transport and everything you need at AGA Airport.
            </p>

            <div className="hero-search">
              <Search size={21} />
              <button type="button" onClick={scrollToAssistant}>
                Ask anything about the airport...
              </button>
              <button
                type="button"
                className="hero-search-button"
                onClick={scrollToAssistant}
                aria-label="Open assistant"
              >
                <Plane size={18} />
              </button>
            </div>

            <div className="hero-trust">
              <span>✦ AI Powered</span>
              <span>✦ Airport Information</span>
              <span>✦ Flight Assistance</span>
            </div>
          </div>

          <div className="hero-side-content">
            <WeatherWidget weather={weather} loading={weatherLoading} />
            <AirportToday
              weather={weather}
              loading={weatherLoading}
              error={weatherError}
            />
          </div>
        </div>
      </section>

      {/* ======================================================
          QUICK ACTIONS
      ====================================================== */}
      <section className="quick-actions-section">
        <div className="section-container">
          <div className="section-heading">
            <span className="section-eyebrow">QUICK ACCESS</span>
            <h2>How can we help you?</h2>
            <p>Choose a topic or ask the assistant anything about your journey.</p>
          </div>

          <div className="quick-actions-grid">
            {quickActions.map((action) => {
              const Icon = action.icon;
              return (
                <button
                  key={action.title}
                  type="button"
                  className="quick-action-card"
                  onClick={() => handleQuickAction(action)}
                >
                  <div className="quick-action-icon">
                    <Icon size={22} />
                  </div>
                  <div>
                    <strong>{action.title}</strong>
                    <span>{action.description}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </section>

      {/* ======================================================
          AI ASSISTANT
      ====================================================== */}
      <section ref={assistantRef} id="assistant" className="assistant-section">
        <div className="section-container">
          <div className="content-section-heading">
            <span className="section-eyebrow">AI ASSISTANT</span>
            <h2>Ask AGA anything</h2>
            <p>Get intelligent answers about the airport and your journey.</p>
          </div>

          <div className="assistant-layout">
            <ChatAssistant
              messages={messages}
              loading={chatLoading}
              onSend={handleSend}
            />
          </div>
        </div>
      </section>

      {/* ======================================================
          FLIGHT INFORMATION
      ====================================================== */}
      <section ref={flightsRef} id="flights" className="flights-section">
        <div className="section-container">
          <div className="content-section-heading">
            <span className="section-eyebrow">FLIGHT INFORMATION</span>
            <h2>Stay informed</h2>
            <p>Check available flight information and live departures.</p>
          </div>

          <div className="flight-information-layout">
            <FlightCard flight={selectedFlight} />
            <DeparturesBoard />
          </div>
        </div>
      </section>

      {/* ======================================================
          SERVICES
      ====================================================== */}
      <section id="services" className="services-section">
        <div className="section-container">
          <AirportServices onAskService={handleSend} />
        </div>
      </section>

      {/* ======================================================
          FOOTER
      ====================================================== */}
      <footer className="airport-footer">
        <div className="section-container footer-content">
          <div>
            <strong>AGA Airport Assistant</strong>
            <p>Your digital airport companion.</p>
          </div>
          <div className="footer-note">
            © {new Date().getFullYear()} AGA Airport Assistant
          </div>
        </div>
      </footer>
    </main>
  );
}
