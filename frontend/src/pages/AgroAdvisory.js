import { useState } from "react";
import { Link } from "react-router-dom";

function AgroAdvisory() {
  const [crop, setCrop] = useState("");
  const [location, setLocation] = useState("");
  const [weather, setWeather] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const getAdvice = async () => {
    if (!crop || !location) {
      alert("Please enter crop and location.");
      return;
    }

    setLoading(true);
    setWeather(null);
    setResult(null);

    try {
      const weatherResponse = await fetch(
        `http://127.0.0.1:8000/weather?location=${encodeURIComponent(location)}`
      );

      const weatherData = await weatherResponse.json();

      if (weatherData.error) {
        alert("Location not found.");
        setLoading(false);
        return;
      }

      setWeather(weatherData);

      const advisoryResponse = await fetch(
        "http://127.0.0.1:8000/agro-advisory",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            crop,
            location,
            temperature: weatherData.temperature,
            humidity: weatherData.humidity,
            rainfall: weatherData.rainfall,
          }),
        }
      );

      const advisoryData = await advisoryResponse.json();

      try {
  const parsedAdvice =
    typeof advisoryData.advisory === "string"
      ? JSON.parse(advisoryData.advisory)
      : advisoryData.advisory;

  setResult(parsedAdvice);
} catch (error) {
  console.error("Advisory parsing error:", error);
  console.log("Backend response:", advisoryData);

  alert("AI returned an invalid advisory response.");
}
    } catch (error) {
  console.error("PRAVA Advisory Error:", error);
  alert("Unable to generate farm advisory. Check browser console.");
}

    setLoading(false);
  };

  return (
    <div className="app">

      <nav>
        <h2>🌾 PRAVA</h2>

        <div className="nav-links">
          <Link to="/">Home</Link>
          <Link to="/crop-recommendation">Crop</Link>
          <Link to="/disease-diagnosis">Disease</Link>
          <Link to="/agro-advisory">Advisory</Link>
        </div>
      </nav>

      <section className="hero">
        <p className="tag">🌦️ SMART AGRO ADVISORY</p>

        <h1>Personalized Farming Advice</h1>

        <p>
          Combine live weather data with AI to understand what your farm
          needs today.
        </p>
      </section>

      {/* INTELLIGENCE STRIP */}
      <section className="intelligence-strip">

        <div className="intel-card">
          <span>📍</span>
          <div>
            <strong>Farm Location</strong>
            <small>Localized intelligence</small>
          </div>
        </div>

        <div className="intel-card">
          <span>🌡️</span>
          <div>
            <strong>Live Weather</strong>
            <small>Real-time conditions</small>
          </div>
        </div>

        <div className="intel-card">
          <span>🤖</span>
          <div>
            <strong>AI Analysis</strong>
            <small>Gemini-powered advice</small>
          </div>
        </div>

        <div className="intel-card">
          <span>⚠️</span>
          <div>
            <strong>Farm Alerts</strong>
            <small>Actionable warnings</small>
          </div>
        </div>

      </section>

      <section className="form-section">

        <div className="form-card advisory-card">

          <p className="card-label">🌱 FARM PROFILE</p>

          <h2>Tell PRAVA about your farm</h2>

          <div className="advisory-inputs">

            <div>
              <label>🌾 Crop</label>
              <input
                type="text"
                placeholder="e.g. Potato"
                value={crop}
                onChange={(e) => setCrop(e.target.value)}
              />
            </div>

            <div>
              <label>📍 Location</label>
              <input
                type="text"
                placeholder="e.g. Sangli, Maharashtra"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              />
            </div>

          </div>

          <button onClick={getAdvice} disabled={loading}>
            {loading ? "🤖 Analyzing Farm..." : "Get AI Farm Advice →"}
          </button>

        </div>

        {/* WEATHER */}
        {weather && (
          <div className="weather-dashboard">

            <div className="weather-heading">
              <div>
                <p className="card-label">🌦️ LIVE FARM CONDITIONS</p>
                <h2>{weather.location}</h2>
              </div>

              <span>LIVE</span>
            </div>

            <div className="weather-grid">

              <div className="weather-card">
                <span>🌡️</span>
                <small>Temperature</small>
                <strong>{weather.temperature}°C</strong>
              </div>

              <div className="weather-card">
                <span>💧</span>
                <small>Humidity</small>
                <strong>{weather.humidity}%</strong>
              </div>

              <div className="weather-card">
                <span>🌧️</span>
                <small>Rainfall</small>
                <strong>{weather.rainfall} mm</strong>
              </div>

            </div>

          </div>
        )}

        {/* AI ADVISORY */}
        {result && (
          <div className="ai-result advisory-result">

            <p className="card-label">🤖 PRAVA AI FARM ADVISORY</p>

            <div className="advisory-status">
              <span>🌱</span>

              <div>
                <small>CURRENT FARM CONDITION</small>
                <h2>{result.status}</h2>
              </div>
            </div>

            <div className="advice-grid">

              <div>
                <span>🌾</span>
                <strong>Action 01</strong>
                <p>{result.advice_1}</p>
              </div>

              <div>
                <span>💧</span>
                <strong>Action 02</strong>
                <p>{result.advice_2}</p>
              </div>

            </div>

            <div className="warning-box">
              <span>⚠️</span>
              <div>
                <strong>Important Warning</strong>
                <p>{result.warning}</p>
              </div>
            </div>

          </div>
        )}

      </section>

    </div>
  );
}

export default AgroAdvisory;