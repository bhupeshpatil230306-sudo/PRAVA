import { useState } from "react";
import { Link } from "react-router-dom";

function DiseaseDiagnosis() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFile = (e) => {
    const selected = e.target.files[0];

    if (!selected) return;

    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setResult(null);
  };

  const diagnoseDisease = async () => {
    if (!file) {
      alert("Please select a crop image.");
      return;
    }

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/disease-diagnosis",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      try {
        setResult(JSON.parse(data.diagnosis));
      } catch {
        setResult({
          crop: "Unknown",
          condition: "Unclear",
          symptoms: data.diagnosis,
          action_1: "Consult a local agricultural expert.",
          action_2: "Try uploading a clearer leaf image.",
        });
      }
    } catch {
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
        <p className="tag">🦠 AI CROP HEALTH</p>

        <h1>Crop Disease Diagnosis</h1>

        <p>
          Analyze crop images with AI-powered vision and get practical
          farming guidance.
        </p>
      </section>

      {/* AI CAPABILITIES */}
      <section className="intelligence-strip">

        <div className="intel-card">
          <span>📸</span>
          <div>
            <strong>Image Analysis</strong>
            <small>Crop & leaf image</small>
          </div>
        </div>

        <div className="intel-card">
          <span>👁️</span>
          <div>
            <strong>AI Vision</strong>
            <small>Gemini multimodal AI</small>
          </div>
        </div>

        <div className="intel-card">
          <span>🦠</span>
          <div>
            <strong>Condition Detection</strong>
            <small>Possible disease</small>
          </div>
        </div>

        <div className="intel-card">
          <span>🌾</span>
          <div>
            <strong>Action Guidance</strong>
            <small>Practical next steps</small>
          </div>
        </div>

      </section>

      <section className="form-section">

        <div className="form-card disease-upload-card">

          <p className="card-label">📸 AI HEALTH SCANNER</p>

          {!preview ? (
            <label className="upload-zone">

              <div className="upload-icon">📷</div>

              <h3>Upload Crop Image</h3>

              <p>
                Select a clear photo of the crop or affected leaf
              </p>

              <span className="upload-button">
                Choose Image
              </span>

              <input
                type="file"
                accept="image/*"
                onChange={handleFile}
              />

            </label>
          ) : (
            <div className="image-preview-container">

              <img
                src={preview}
                alt="Selected crop"
                className="crop-preview"
              />

              <label className="change-image">
                Change Image
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFile}
                />
              </label>

            </div>
          )}

          <button
            onClick={diagnoseDisease}
            disabled={loading}
          >
            {loading
              ? "🤖 Analyzing Crop..."
              : "🔍 Analyze with PRAVA AI →"}
          </button>

        </div>

        {/* RESULT */}
        {result && (
          <div className="ai-result disease-result">

            <p className="card-label">🤖 PRAVA AI HEALTH REPORT</p>

            <div className="disease-header">

              <div className="health-icon">🌿</div>

              <div>
                <small>ANALYZED CROP</small>
                <h2>{result.crop}</h2>
              </div>

            </div>

            <div className="condition-box">

              <small>POSSIBLE CONDITION</small>

              <h2>🦠 {result.condition}</h2>

            </div>

            <div className="reason-box">

              <h3>🔎 Observed Symptoms</h3>

              <p>{result.symptoms}</p>

            </div>

            <div className="tips-grid">

              <div>
                <span>🌱</span>
                <strong>Recommended Action</strong>
                <p>{result.action_1}</p>
              </div>

              <div>
                <span>🛡️</span>
                <strong>Prevention / Next Step</strong>
                <p>{result.action_2}</p>
              </div>

            </div>

            <p className="ai-disclaimer">
              AI-generated assessment. For serious crop damage,
              consult a qualified agricultural expert.
            </p>

          </div>
        )}

      </section>

    </div>
  );
}

export default DiseaseDiagnosis;