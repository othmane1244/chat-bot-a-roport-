import { useState, useEffect } from "react";
import { AVIONIO_CONFIG } from "../config/avionio";

export default function DeparturesBoard() {
  const [loading, setLoading] = useState(() => Boolean(AVIONIO_CONFIG.enabled));
  const [error, setError] = useState(() => !AVIONIO_CONFIG.enabled);
  const [iframeKey, setIframeKey] = useState(0);

  useEffect(() => {
    if (!AVIONIO_CONFIG.enabled) return;

    // Timeout de 10 secondes si l'iframe est bloqué ou ne charge pas
    const timeout = setTimeout(() => {
      setLoading((isLoading) => {
        if (isLoading) {
          setError(true);
        }
        return false;
      });
    }, 10000);

    return () => {
      clearTimeout(timeout);
    };
  }, [iframeKey]);

  const handleLoad = () => {
    setLoading(false);
    setError(false);
  };

  const handleError = () => {
    setLoading(false);
    setError(true);
  };

  const reloadBoard = () => {
    setLoading(true);
    setError(false);
    setIframeKey((previous) => previous + 1);
  };

  if (!AVIONIO_CONFIG.enabled) {
    return (
      <section id="departures" className="departures-section">
        <div className="departures-header">
          <div>
            <span className="section-label">LIVE INFORMATION</span>
            <h2>Live Departures</h2>
          </div>
          <span className="live-status">● LIVE</span>
        </div>

        <div className="departures-unavailable">
          <div className="unavailable-icon">✈</div>
          <h3>Live departures unavailable</h3>
          <p>The live flight board is not configured yet.</p>
        </div>
      </section>
    );
  }

  return (
    <section id="departures" className="departures-section">
      {/* HEADER */}
      <div className="departures-header">
        <div>
          <span className="section-label">LIVE INFORMATION</span>
          <h2>Live Departures</h2>
          <p>Real-time departure information</p>
        </div>

        <div className="departures-actions">
          <span className="live-status">● LIVE</span>
          <button
            type="button"
            className="reload-button"
            onClick={reloadBoard}
            aria-label="Reload departures"
          >
            ↻
          </button>
        </div>
      </div>

      {/* BOARD */}
      <div className="avionio-container">
        {loading && (
          <div className="avionio-loading">
            <div className="airport-loader">
              <span className="loader-plane">✈</span>
            </div>
            <p>Loading live departures...</p>
          </div>
        )}

        {error && (
          <div className="avionio-error">
            <div className="error-icon">⚠️</div>
            <h3>Unable to load live departures</h3>
            <p>Please check your connection and try again.</p>
            <button type="button" onClick={reloadBoard}>
              Try again
            </button>
          </div>
        )}

        {!error && (
          <iframe
            key={iframeKey}
            src={AVIONIO_CONFIG.iframeUrl}
            title="Agadir Airport Live Departures"
            className="avionio-iframe"
            onLoad={handleLoad}
            onError={handleError}
            loading="lazy"
            allowFullScreen
          />
        )}
      </div>

      <p className="departures-note">
        Live flight information is provided through the airport flight information service.
      </p>
    </section>
  );
}
