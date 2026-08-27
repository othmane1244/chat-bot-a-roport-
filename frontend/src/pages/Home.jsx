import { useState } from "react";
import AirportHeader from "../components/AirportHeader";
import AirportBackground from "../components/AirportBackground";
import ChatAssistant from "../components/ChatAssistant";
import FlightCard from "../components/FlightCard";
import DeparturesBoard from "../components/DeparturesBoard";
import WeatherWidget from "../components/WeatherWidget";
import QuickActions from "../components/QuickActions";
import { useWeather } from "../hooks/useWeather";
import { useChat } from "../hooks/useChat";

export default function Home() {
  const [currentLang, setLang] = useState("fr");
  const [heroInput, setHeroInput] = useState("");
  const { weather } = useWeather();
  const { send } = useChat();

  const handleHeroSubmit = (e) => {
    e.preventDefault();
    if (!heroInput.trim()) return;
    send(heroInput, currentLang);
    setHeroInput("");
    // Scroll down smoothly to chat assistant
    const el = document.getElementById("assistant-card");
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  const handleQuickActionClick = (promptText) => {
    send(promptText, currentLang);
    const el = document.getElementById("assistant-card");
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <main className="app">
      <AirportBackground />

      <div className="content">
        {/* En-tête AGA */}
        <AirportHeader 
          temp={weather?.temp} 
          currentLang={currentLang} 
          onSelectLang={setLang} 
        />

        {/* Section Hero avec Titre, QuickActions, SearchBar à gauche et WeatherWidget à droite */}
        <section className="hero-dashboard-section">
          <div className="hero-left-content">
            <span className="airport-tag">AGA AIRPORT</span>
            <h1 className="hero-greeting">Good afternoon 👋</h1>
            <h2 className="hero-main-title">How can I help you today?</h2>

            <QuickActions onAction={handleQuickActionClick} />

            <form className="hero-search-bar" onSubmit={handleHeroSubmit}>
              <input
                type="text"
                value={heroInput}
                onChange={(e) => setHeroInput(e.target.value)}
                placeholder="Ask anything about Agadir Airport..."
              />
              <button type="submit" className="hero-send-btn">
                ➤
              </button>
            </form>
          </div>

          <div className="hero-right-widget">
            <WeatherWidget weather={weather} />
          </div>
        </section>

        {/* Tableau de bord 3 colonnes : AI Assistant, Your Flight, Live Departures */}
        <section className="dashboard-3col-grid" id="assistant-card">
          <ChatAssistant currentLang={currentLang} />
          <FlightCard flightNumber="AT5432" />
          <DeparturesBoard />
        </section>
      </div>
    </main>
  );
}
