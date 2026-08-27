export default function AirportHeader({ temp = "24", currentLang = "fr", onSelectLang }) {
  return (
    <header className="airport-header">
      <div className="logo">
        <div className="logo-title">AGA ✈</div>
        <div className="logo-subtitle">Agadir Al Massira Airport</div>
      </div>

      <nav className="navigation">
        <a href="#assistant" className="nav-item active">Assistant</a>
        <a href="#departures" className="nav-item">Departures</a>
        <a href="#guide" className="nav-item">Airport Guide</a>
      </nav>

      <div className="header-right">
        <div className="temperature-pill">
          {temp}°C ☀️
        </div>

        <div className="languages">
          <span 
            className={`lang-option ${currentLang === 'fr' ? 'active' : ''}`}
            onClick={() => onSelectLang && onSelectLang('fr')}
          >
            FR
          </span>
          <span className="lang-sep">|</span>
          <span 
            className={`lang-option ${currentLang === 'en' ? 'active' : ''}`}
            onClick={() => onSelectLang && onSelectLang('en')}
          >
            EN
          </span>
          <span className="lang-sep">|</span>
          <span 
            className={`lang-option ${currentLang === 'ar' ? 'active' : ''}`}
            onClick={() => onSelectLang && onSelectLang('ar')}
          >
            العربية
          </span>
        </div>
      </div>
    </header>
  );
}
