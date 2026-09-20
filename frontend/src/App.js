import { BrowserRouter, Routes, Route, Link, NavLink } from "react-router-dom";
import CropRecommendation from "./pages/CropRecommendation";
import "./App.css";
import DiseaseDiagnosis from "./pages/DiseaseDiagnosis";
import AgroAdvisory from "./pages/AgroAdvisory";
import farmBg from "./farm-bg.png";

function Home() {
  return (
    <div
  className="app home-page"
  style={{
    backgroundImage: `url(${farmBg})`,
backgroundRepeat: "no-repeat",
backgroundSize: "cover",
    backgroundPosition: "center top"
  }}
>
      <nav>
        <h2>🌾 PRAVA</h2>

        <div className="nav-links">
  <NavLink to="/" end>Home</NavLink>
  <NavLink to="/crop-recommendation">Crop</NavLink>
  <NavLink to="/disease-diagnosis">Disease</NavLink>
  <NavLink to="/agro-advisory">Advisory</NavLink>

  <button className="language-btn">हिंदी</button>
</div>
      </nav>

      <section className="hero home-hero">
        <div className="hero-content">
          <p className="tag">SMART FARMING • SMARTER FUTURE</p>

          <h1>
            Better decisions.
            <br />
            <span>Better farming.</span>
          </h1>

          <p>
            PRAVA combines AI, soil, weather and crop intelligence
            to help Indian farmers make smarter decisions.
          </p>

          <div className="hero-actions">
            <Link to="/crop-recommendation">
              <button>Start with Crop AI →</button>
            </Link>

            <Link to="/agro-advisory" className="secondary-btn">
              Get Agro Advice
            </Link>
          </div>
        </div>

        <div className="hero-visual">
          <div className="visual-card">
            <div className="visual-icon">🌾</div>
            <h3>PRAVA Intelligence</h3>
            <p>AI-powered agricultural decisions</p>

            <div className="intelligence-row">
              <span>🌱 Soil</span>
              <span>🌦️ Weather</span>
            </div>

            <div className="intelligence-row">
              <span>🛰️ Data</span>
              <span>🤖 AI</span>
            </div>
          </div>
        </div>
      </section>

      <section className="features">
        <div className="card">
          <div className="icon">🌱</div>
          <h3>Crop Recommendation</h3>
          <p>
            Find suitable crops using soil and environmental conditions.
          </p>
          <Link to="/crop-recommendation">
            <button>Explore →</button>
          </Link>
        </div>

        <div className="card">
          <div className="icon">📸</div>
          <h3>Disease Diagnosis</h3>
          <p>
            Upload a crop image and let AI identify possible crop diseases.
          </p>
          <Link to="/disease-diagnosis">
            <button>Diagnose →</button>
          </Link>
        </div>

        <div className="card">
          <div className="icon">🌦️</div>
          <h3>Agro Advisory</h3>
          <p>
            Get localized farming advice using real-time weather data.
          </p>
          <Link to="/agro-advisory">
            <button>Get Advice →</button>
          </Link>
        </div>
      </section>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div
        className="site-background"
        style={{
          backgroundImage: `url(${farmBg})`
        }}
      >
        <Routes>
          <Route path="/agro-advisory" element={<AgroAdvisory />} />
          <Route path="/disease-diagnosis" element={<DiseaseDiagnosis />} />
          <Route path="/" element={<Home />} />
          <Route
            path="/crop-recommendation"
            element={<CropRecommendation />}
          />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;

