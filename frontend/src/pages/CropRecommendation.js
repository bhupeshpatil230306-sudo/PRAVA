import { useState } from "react";
import { Link } from "react-router-dom";

function CropRecommendation() {
  const [form, setForm] = useState({
    N: "",
    P: "",
    K: "",
    temperature: "",
    humidity: "",
    ph: "",
    rainfall: "",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const getRecommendation = async () => {
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(
        "https://prava-ntpx.onrender.com/crop-recommendation",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            N: Number(form.N),
            P: Number(form.P),
            K: Number(form.K),
            temperature: Number(form.temperature),
            humidity: Number(form.humidity),
            ph: Number(form.ph),
            rainfall: Number(form.rainfall),
          }),
        }
      );

      const data = await response.json();

      let advice = {};

      try {
        advice = JSON.parse(data.ai_advice);
      } catch {
        advice = {
          why_recommended: data.ai_advice,
          tip_1: "Monitor soil moisture regularly.",
          tip_2: "Follow local agricultural recommendations.",
        };
      }

      setResult({
        crop: data.recommended_crop,
        ...advice,
      });
    } catch (error) {
      alert("Unable to connect to PRAVA AI.");
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
        <p className="tag">🌱 CROP INTELLIGENCE</p>

        <h1>Find the right crop.</h1>

        <p>
          AI-powered crop selection using soil and climate conditions.
        </p>
      </section>

      {/* INTELLIGENCE STRIP */}
      <section className="intelligence-strip">

        <div className="intel-card">
          <span>🧪</span>
          <div>
            <strong>Soil Analysis</strong>
            <small>N • P • K • pH</small>
          </div>
        </div>

        <div className="intel-card">
          <span>🌦️</span>
          <div>
            <strong>Climate Data</strong>
            <small>Temperature • Rainfall</small>
          </div>
        </div>

        <div className="intel-card">
          <span>🤖</span>
          <div>
            <strong>ML Prediction</strong>
            <small>Crop intelligence</small>
          </div>
        </div>

        <div className="intel-card">
          <span>💡</span>
          <div>
            <strong>AI Reasoning</strong>
            <small>Why this crop?</small>
          </div>
        </div>

      </section>

      <section className="form-section">

        <div className="form-card">

          <p className="card-label">🌱 FARM CONDITION ANALYSIS</p>

          <div className="form-grid">

            <div>
              <label>Nitrogen (N)</label>
              <input
                name="N"
                placeholder="e.g. 90"
                value={form.N}
                onChange={handleChange}
              />
            </div>

            <div>
              <label>Phosphorus (P)</label>
              <input
                name="P"
                placeholder="e.g. 42"
                value={form.P}
                onChange={handleChange}
              />
            </div>

            <div>
              <label>Potassium (K)</label>
              <input
                name="K"
                placeholder="e.g. 43"
                value={form.K}
                onChange={handleChange}
              />
            </div>

            <div>
              <label>Soil pH</label>
              <input
                name="ph"
                placeholder="e.g. 6.5"
                value={form.ph}
                onChange={handleChange}
              />
            </div>

            <div>
              <label>Temperature (°C)</label>
              <input
                name="temperature"
                placeholder="e.g. 25"
                value={form.temperature}
                onChange={handleChange}
              />
            </div>

            <div>
              <label>Humidity (%)</label>
              <input
                name="humidity"
                placeholder="e.g. 80"
                value={form.humidity}
                onChange={handleChange}
              />
            </div>

            <div className="full-field">
              <label>Rainfall (mm)</label>
              <input
                name="rainfall"
                placeholder="e.g. 200"
                value={form.rainfall}
                onChange={handleChange}
              />
            </div>

          </div>

          <button onClick={getRecommendation}>
            {loading ? "🤖 Analyzing..." : "Get AI Recommendation →"}
          </button>

        </div>

        {/* AI RESULT */}
        {result && (
          <div className="ai-result">

            <p className="card-label">🤖 PRAVA AI RESULT</p>

            <div className="crop-result-header">
              <div className="crop-icon">🌾</div>

              <div>
                <small>RECOMMENDED CROP</small>
                <h2>{result.crop}</h2>
              </div>

              <div className="score-badge">
                AI MATCH
              </div>
            </div>

            <div className="reason-box">
              <h3>💡 Why PRAVA recommends this</h3>
              <p>{result.why_recommended}</p>
            </div>

            <div className="tips-grid">

              <div>
                <span>🌱</span>
                <strong>Farming Tip</strong>
                <p>{result.tip_1}</p>
              </div>

              <div>
                <span>💧</span>
                <strong>PRAVA Insight</strong>
                <p>{result.tip_2}</p>
              </div>

            </div>

          </div>
        )}

      </section>

    </div>
  );
}

export default CropRecommendation;