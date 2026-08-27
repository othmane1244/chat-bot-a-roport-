import { useState } from "react";

import AirportHeader from "../components/AirportHeader";
import AirportBackground from "../components/AirportBackground";

import ChatAssistant from "../components/ChatAssistant";
import QuickActions from "../components/QuickActions";

import FlightCard from "../components/FlightCard";
import DeparturesBoard from "../components/DeparturesBoard";

import WeatherWidget from "../components/WeatherWidget";

import { useChat } from "../hooks/useChat";
import { useWeather } from "../hooks/useWeather";
import { getOperationalData } from "../data/simulatedOperationalData";

export default function Home() {
  const [heroInput, setHeroInput] = useState("");
  const [currentLang, setLang] = useState("fr");
  const [selectedFlight, setSelectedFlight] = useState(null);

  const { weather } = useWeather();

  // ✅ UNE SEULE INSTANCE DU CHAT POUR TOUT L'APP
  const {
    messages,
    loading,
    send,
  } = useChat();

  const handleSend = async (messageText) => {
    if (!messageText?.trim() || loading) return;

    const response = await send(messageText, currentLang);

    // Détection automatique de vol dans la réponse backend ou le message
    if (response?.flight) {
      setSelectedFlight(response.flight);
    } else {
      const match = messageText.match(/\b([A-Z]{2,3}\s*\d{2,4})\b/i);
      if (match) {
        const flightNum = match[1].replace(/\s+/, "").toUpperCase();
        const flightData = getOperationalData(flightNum);
        if (flightData) {
          setSelectedFlight(flightData);
        }
      }
    }

    return response;
  };

  const handleHeroSubmit = async (event) => {
    event.preventDefault();

    if (!heroInput.trim()) return;

    await handleSend(heroInput);

    setHeroInput("");

    // Scroll automatique vers le chat
    document
      .getElementById("assistant")
      ?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
  };

  const handleQuickAction = async (prompt) => {
    await handleSend(prompt);

    // Scroll automatique vers le chat
    document
      .getElementById("assistant")
      ?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
  };

  return (
    <main className="app">
      <AirportBackground />

      <div className="content">
        <AirportHeader 
          temp={weather?.temp} 
          currentLang={currentLang} 
          onSelectLang={setLang} 
        />

        {/* HERO */}
        <section className="hero-dashboard-section">
          <div className="hero-left-content">
            <span className="airport-tag">
              AGA AIRPORT
            </span>

            <h1 className="hero-greeting">
              Your Digital Airport Assistant
            </h1>

            <h2 className="hero-main-title">
              Ask anything about Agadir Al Massira Airport.
            </h2>

            {/* HERO INPUT */}
            <form
              className="hero-search-bar"
              onSubmit={handleHeroSubmit}
            >
              <input
                value={heroInput}
                onChange={(event) =>
                  setHeroInput(event.target.value)
                }
                placeholder="How can I help you today?"
                disabled={loading}
              />

              <button
                type="submit"
                className="hero-send-btn"
                disabled={loading}
              >
                {loading ? "..." : "→"}
              </button>
            </form>
          </div>

          <div className="hero-right-widget">
            <WeatherWidget weather={weather} />
          </div>
        </section>

        {/* QUICK ACTIONS */}
        <QuickActions
          onAction={handleQuickAction}
        />

        {/* DASHBOARD GRID: CHAT, FLIGHT CARD, LIVE DEPARTURES */}
        <section className="dashboard-3col-grid" id="assistant">
          <ChatAssistant
            messages={messages}
            loading={loading}
            onSend={handleSend}
          />

          <FlightCard
            flight={selectedFlight}
          />

          <DeparturesBoard />
        </section>
      </div>
    </main>
  );
}
