import { useState } from "react";
import { Menu, MessageCircle, Plane, X } from "lucide-react";

export default function AirportHeader({ onAssistantClick, onFlightsClick }) {
  const [menuOpen, setMenuOpen] = useState(false);

  const closeMenu = () => setMenuOpen(false);

  const handleAssistant = () => {
    closeMenu();
    onAssistantClick?.();
  };

  const handleFlights = () => {
    closeMenu();
    onFlightsClick?.();
  };

  return (
    <header className="airport-header">
      <div className="header-container">
        {/* Logo */}
        <button
          className="airport-brand"
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
        >
          <div className="brand-icon">
            <Plane size={22} />
          </div>
          <div className="brand-text">
            <strong>AGA</strong>
            <span>Airport Assistant</span>
          </div>
        </button>

        {/* Desktop navigation */}
        <nav className="desktop-nav">
          <button onClick={handleAssistant}>Assistant</button>
          <button onClick={handleFlights}>Flights</button>
          <button
            onClick={() =>
              document
                .getElementById("services")
                ?.scrollIntoView({ behavior: "smooth" })
            }
          >
            Services
          </button>
        </nav>

        {/* CTA */}
        <button className="header-assistant-button" onClick={handleAssistant}>
          <MessageCircle size={17} />
          <span>Ask Assistant</span>
        </button>

        {/* Mobile menu toggle */}
        <button
          className="mobile-menu-button"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Open navigation"
        >
          {menuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile navigation */}
      {menuOpen && (
        <div className="mobile-nav">
          <button onClick={handleAssistant}>
            <MessageCircle size={18} />
            Assistant
          </button>
          <button onClick={handleFlights}>
            <Plane size={18} />
            Flights
          </button>
          <button
            onClick={() => {
              closeMenu();
              document
                .getElementById("services")
                ?.scrollIntoView({ behavior: "smooth" });
            }}
          >
            Services
          </button>
        </div>
      )}
    </header>
  );
}
