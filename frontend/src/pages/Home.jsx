import { useState } from "react";

import AirportHeader from "../components/AirportHeader";
import AirportBackground from "../components/AirportBackground";
import WeatherWidget from "../components/WeatherWidget";
import ChatAssistant from "../components/ChatAssistant";
import QuickActions from "../components/QuickActions";
import FlightCard from "../components/FlightCard";
import DeparturesBoard from "../components/DeparturesBoard";

import { useChat } from "../hooks/useChat";
import { useWeather } from "../hooks/useWeather";

export default function Home() {
  const [heroInput, setHeroInput] = useState("");
  const [currentLang, setLang] = useState("fr");
  const [selectedFlight, setSelectedFlight] = useState(null);

  const { messages, loading: chatLoading, send } = useChat();
  const { weather, loading: weatherLoading } = useWeather();

  const handleSend = async (message) => {
    const response = await send(message, currentLang);
    if (response?.flight) {
      setSelectedFlight(response.flight);
    }
    return response;
  };

  const handleHeroSubmit = async (event) => {
    event.preventDefault();
    if (!heroInput.trim()) return;

    await handleSend(heroInput);
    setHeroInput("");

    document.getElementById("assistant")?.scrollIntoView({
      behavior: "smooth",
    });
  };

  return (
    <main className="app">
      <AirportBackground atmosphere={weather?.atmosphere || "sunny"} />

      <div className="content">
        <AirportHeader
          temp={weather?.temperature}
          currentLang={currentLang}
          onSelectLang={setLang}
        />

        {/* HERO */}
        <section className="hero-dashboard-section hero-section">
          <div className="hero-left-content hero-content">
            <span className="airport-tag airport-label animate-fade-up">
              AGA AIRPORT
            </span>

            <h1 className="hero-greeting hero-title">
              Your Digital Airport Assistant
            </h1>

            <p className="hero-main-title hero-description">
              Everything you need for your journey at Agadir Al Massira Airport.
            </p>

            <form className="hero-search-bar hero-search" onSubmit={handleHeroSubmit}>
              <input
                value={heroInput}
                onChange={(event) => setHeroInput(event.target.value)}
                placeholder="How can I help you today?"
                disabled={chatLoading}
              />

              <button type="submit" className="hero-send-btn" disabled={chatLoading}>
                {chatLoading ? "..." : "➜"}
              </button>
            </form>
          </div>

          <div className="hero-right-widget">
            <WeatherWidget weather={weather} loading={weatherLoading} />
          </div>
        </section>

        {/* QUICK ACTIONS */}
        <QuickActions onAction={handleSend} />

        {/* DASHBOARD GRID: CHAT, FLIGHT CARD, LIVE DEPARTURES */}
        <section className="dashboard-3col-grid" id="assistant">
          <ChatAssistant
            messages={messages}
            loading={chatLoading}
            onSend={handleSend}
          />

          <FlightCard flight={selectedFlight} />

          <DeparturesBoard />
        </section>
      </div>
    </main>
  );
}
