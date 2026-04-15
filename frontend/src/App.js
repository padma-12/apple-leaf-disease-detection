import React, { useState, useEffect } from "react";
import UploadWithCamera from "./UploadWithCamera";
import "./App.css";

function App() {
  const [result, setResult] = useState(null);
  const [results, setResults] = useState(() => {
    // Load results from localStorage
    const saved = localStorage.getItem('appleDiseaseResults');
    return saved ? JSON.parse(saved) : [];
  });
  const [language, setLanguage] = useState("en");
  const [isDarkMode, setIsDarkMode] = useState(() => {
    return localStorage.getItem('darkMode') === 'true';
  });
  const [showHistory, setShowHistory] = useState(false);
  const [showEncyclopedia, setShowEncyclopedia] = useState(false);
  const [selectedDisease, setSelectedDisease] = useState(null);

  
  useEffect(() => {
    localStorage.setItem('appleDiseaseResults', JSON.stringify(results));
  }, [results]);

  // Save dark mode preference
  useEffect(() => {
    localStorage.setItem('darkMode', isDarkMode);
    document.body.classList.toggle('dark-mode', isDarkMode);
  }, [isDarkMode]);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'n' && result) {
        e.preventDefault();
        setResult(null);
        window.location.reload();
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 'd' && result) {
        e.preventDefault();
        const downloadBtn = document.querySelector('.download-report-btn');
        if (downloadBtn) downloadBtn.click();
      }
     
      if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
        e.preventDefault();
        setShowHistory(!showHistory);
      }
      // Ctrl/Cmd + M for dark mode
      if ((e.ctrlKey || e.metaKey) && e.key === 'm') {
        e.preventDefault();
        setIsDarkMode(!isDarkMode);
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [result, showHistory, isDarkMode]);

  const handleNewResult = (newResult) => {
    setResult(newResult);
    // Add to results history
    const resultWithTimestamp = {
      ...newResult,
      timestamp: new Date().toISOString(),
      id: Date.now()
    };
    setResults(prev => [resultWithTimestamp, ...prev.slice(0, 49)]); // Keep last 50 results
  };

  const deleteResult = (id) => {
    setResults(prev => prev.filter(r => r.id !== id));
  };

  const shareResult = (result) => {
    const shareText = `Apple Disease Detected: ${result.disease}\nSeverity: ${result.severity}\nConfidence: ${result.confidence}%\n\nAnalyzed with Apple Disease Detection App`;
    const shareUrl = window.location.href;

    if (navigator.share) {
      navigator.share({
        title: 'Apple Disease Analysis Result',
        text: shareText,
        url: shareUrl
      });
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(`${shareText}\n\n${shareUrl}`);
      alert('Result copied to clipboard!');
    }
  };

  const diseaseEncyclopedia = {
    "Apple Scab": {
      description: "A common fungal disease caused by Venturia inaequalis. It appears as dark, scabby lesions on leaves, fruit, and twigs.",
      symptoms: ["Dark, olive-green spots on leaves", "Scabby lesions on fruit", "Premature leaf drop"],
      causes: ["Fungal spores from infected plant material", "Wet weather conditions", "Poor air circulation"],
      prevention: ["Plant resistant varieties", "Prune infected branches", "Apply fungicides preventively", "Ensure good air circulation"]
    },
    "Powdery Mildew": {
      description: "A fungal disease that appears as white, powdery coating on leaves and shoots.",
      symptoms: ["White, powdery coating on leaves", "Distorted leaves", "Stunted growth"],
      causes: ["High humidity", "Poor air circulation", "Fungal spores"],
      prevention: ["Improve air circulation", "Avoid overhead watering", "Apply sulfur-based fungicides", "Remove infected plant parts"]
    },
    "Fire Blight": {
      description: "A bacterial disease that causes rapid wilting and blackening of blossoms and shoots.",
      symptoms: ["Blackened, wilted blossoms", "Shepherd's crook appearance", "Bacterial ooze"],
      causes: ["Bacteria entering through wounds", "Insects", "Pruning tools"],
      prevention: ["Prune infected branches 12 inches below symptoms", "Disinfect pruning tools", "Avoid nitrogen-rich fertilizers", "Plant resistant varieties"]
    },
    "Cedar Apple Rust": {
      description: "A fungal disease that requires both apple and cedar trees to complete its life cycle.",
      symptoms: ["Yellow-orange spots on leaves", "Hairy growth on undersides", "Galls on cedar trees"],
      causes: ["Spores from nearby cedar trees", "Wet spring weather"],
      prevention: ["Remove nearby cedar trees", "Apply fungicides during spore release", "Plant resistant varieties"]
    }
  };

  return (
    <div className={`app-container ${isDarkMode ? 'dark-mode' : ''}`}>
      <div className="aurora"></div>
      <div className="geometric-pattern"></div>
      <div className="particles">
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
      </div>

      {/* Skip to main content for accessibility */}
      <a href="#main-content" className="skip-link">Skip to main content</a>

      <header className="app-header">
        <h1 className="app-title">🍎 Apple Leaf Disease Detection</h1>
        <div className="header-controls">
          <div className="header-actions">

            <button
              className="header-btn dark-mode-toggle"
              onClick={() => setIsDarkMode(!isDarkMode)}
              title="Toggle Dark Mode (Ctrl+M)"
            >
              {isDarkMode ? '☀️' : '🌙'}
            </button>
          </div>
          <div className="language-section">
            <label htmlFor="language-select" className="language-label">Language:</label>
            <select
              id="language-select"
              className="language-selector"
              onChange={(e) => setLanguage(e.target.value)}
              value={language}
              aria-label="Select language for analysis results"
            >
              <option value="en">🇺🇸 English</option>
              <option value="hi">🇮🇳 Hindi</option>
              <option value="ta">🇮🇳 Tamil</option>
              <option value="te">🇮🇳 Telugu</option>
            </select>
          </div>
        </div>
      </header>

      {/* History Modal */}
      {showHistory && (
        <div className="modal-overlay" onClick={() => setShowHistory(false)}>
          <div className="modal-content history-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📚 Analysis History</h2>
              <button className="modal-close" onClick={() => setShowHistory(false)}>×</button>
            </div>
            <div className="history-list">
              {results.length === 0 ? (
                <p className="no-history">No analysis history yet. Start by analyzing some apple leaves!</p>
              ) : (
                results.map((result) => (
                  <div key={result.id} className="history-item">
                    <div className="history-info">
                      <div className="history-disease">{result.disease}</div>
                      <div className="history-details">
                        <span className={`severity-badge history-severity`} data-severity={result.severity.toLowerCase()}>
                          {result.severity}
                        </span>
                        <span className="history-confidence">{result.confidence}% confidence</span>
                        <span className="history-date">
                          {new Date(result.timestamp).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                    <div className="history-actions">
                      <button
                        className="history-btn view-btn"
                        onClick={() => {
                          setResult(result);
                          setShowHistory(false);
                        }}
                      >
                        👁️ View
                      </button>
                      <button
                        className="history-btn share-btn"
                        onClick={() => shareResult(result)}
                      >
                        📤 Share
                      </button>
                      <button
                        className="history-btn delete-btn"
                        onClick={() => deleteResult(result.id)}
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Encyclopedia Modal */}
      {showEncyclopedia && (
        <div className="modal-overlay" onClick={() => setShowEncyclopedia(false)}>
          <div className="modal-content encyclopedia-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📖 Apple Disease Encyclopedia</h2>
              <button className="modal-close" onClick={() => setShowEncyclopedia(false)}>×</button>
            </div>
            <div className="encyclopedia-content">
              {selectedDisease ? (
                <div className="disease-detail">
                  <button
                    className="back-btn"
                    onClick={() => setSelectedDisease(null)}
                  >
                    ← Back to Encyclopedia
                  </button>
                  <h3>{selectedDisease}</h3>
                  <div className="disease-info">
                    <div className="info-section">
                      <h4>Description</h4>
                      <p>{diseaseEncyclopedia[selectedDisease].description}</p>
                    </div>
                    <div className="info-section">
                      <h4>Symptoms</h4>
                      <ul>
                        {diseaseEncyclopedia[selectedDisease].symptoms.map((symptom, i) => (
                          <li key={i}>{symptom}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="info-section">
                      <h4>Causes</h4>
                      <ul>
                        {diseaseEncyclopedia[selectedDisease].causes.map((cause, i) => (
                          <li key={i}>{cause}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="info-section">
                      <h4>Prevention</h4>
                      <ul>
                        {diseaseEncyclopedia[selectedDisease].prevention.map((prevent, i) => (
                          <li key={i}>{prevent}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="disease-list">
                  <p className="encyclopedia-intro">
                    Learn about common apple diseases, their symptoms, causes, and prevention methods.
                  </p>
                  {Object.keys(diseaseEncyclopedia).map((disease) => (
                    <div
                      key={disease}
                      className="disease-card encyclopedia-card"
                      onClick={() => setSelectedDisease(disease)}
                    >
                      <h4>{disease}</h4>
                      <p>{diseaseEncyclopedia[disease].description.substring(0, 100)}...</p>
                      <span className="learn-more">Learn more →</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <main id="main-content" className={`main-content ${result ? 'has-result' : ''}`} role="main">
        {!result && (
          <div className="welcome-banner">
            <h2>Keep Your Apple Trees Healthy 🍎</h2>
            <p>
              We are here to help! Our smart tool instantly checks your apple leaves for diseases.
              <strong> Just take a picture or upload a photo below. </strong>
              We'll tell you exactly what's wrong and give you easy steps to fix it. Protect your harvest and grow happy trees!
            </p>
          </div>
        )}

        {!result && (
          <section className="upload-section" aria-labelledby="upload-heading">
            <UploadWithCamera setResult={handleNewResult} language={language} />
          </section>
        )}

        {result && (
          <>
            <section className="image-display-section">
              <h2>📸 Analyzed Image</h2>
              <div className="image-preview-container">
                <img
                  src={`http://127.0.0.1:5000${result.boxed_image_url || result.image_url}`}
                  alt="Analyzed Apple Leaf"
                  className="result-preview-image"
                />
              </div>
              {result.audio_url && (
                <div className="result-card audio-card" style={{ marginTop: '20px', width: '100%' }}>
                  <div className="card-header">
                    <span className="card-icon">🔊</span>
                    <h3>Audio Guidance</h3>
                  </div>
                  <div className="audio-controls">
                    <audio className="audio-player" controls style={{ width: '100%' }}>
                      <source src={`http://127.0.0.1:5000${result.audio_url}`} />
                      Your browser does not support the audio element.
                    </audio>
                    <p className="audio-description" style={{ textAlign: 'center', marginTop: '10px' }}>
                      Listen to detailed audio instructions
                    </p>
                  </div>
                </div>
              )}
            </section>

            <section className="result-section">
              <div className="result-header">
                <h2>🔍 Analysis Complete</h2>
                <div className="result-actions">
                  <button
                    className="new-analysis-btn"
                    onClick={() => {
                      setResult(null);
                    }}
                  >
                    🔄 New Analysis
                  </button>
                  <button
                    className="download-report-btn"
                    onClick={() => {
                      // Create a simple report
                      const report = `
Apple Disease Detection Report
===============================

Disease: ${result.disease}
Severity: ${result.severity}
Confidence: ${result.confidence}%

Description:
${result.description}

Treatment:
${result.treatment.map(t => `• ${t}`).join('\n')}

Prevention:
${result.prevention.map(p => `• ${p}`).join('\n')}

Generated on: ${new Date().toLocaleString()}
                    `.trim();

                      const blob = new Blob([report], { type: 'text/plain' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `apple-disease-report-${Date.now()}.txt`;
                      document.body.appendChild(a);
                      a.click();
                      document.body.removeChild(a);
                      URL.revokeObjectURL(url);
                    }}
                  >
                    📄 Download Report
                  </button>
                  <button
                    className="share-result-btn"
                    onClick={() => shareResult(result)}
                    title="Share this analysis result"
                  >
                    📤 Share Result
                  </button>
                </div>
              </div>

              <div className="result-summary">
                <div className="result-card disease-card">
                  <div className="card-header">
                    <span className="card-icon">🌿</span>
                    <h3>Disease Detected</h3>
                  </div>
                  <div className="disease-info">
                    <div className="disease-name">{result.disease}</div>
                    <div className="disease-details">
                      <span className="severity-badge" data-severity={result.severity.toLowerCase()}>
                        {result.severity}
                      </span>
                      <span className="confidence-score">
                        {result.confidence}% confidence
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="result-details">
                <div className="result-card">
                  <div className="card-header">
                    <span className="card-icon">📋</span>
                    <h3>Description</h3>
                  </div>
                  <p className="result-text description-text">{result.description}</p>
                </div>

                <div className="result-card">
                  <div className="card-header">
                    <span className="card-icon">💊</span>
                    <h3>Treatment Recommendations</h3>
                  </div>
                  <div className="treatment-list">
                    {result.treatment.map((t, i) => (
                      <div key={i} className="treatment-item">
                        <span className="treatment-number">{i + 1}</span>
                        <span className="treatment-text">{t}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="result-card">
                  <div className="card-header">
                    <span className="card-icon">🛡️</span>
                    <h3>Prevention Measures</h3>
                  </div>
                  <div className="prevention-list">
                    {result.prevention.map((p, i) => (
                      <div key={i} className="prevention-item">
                        <span className="prevention-icon">✓</span>
                        <span className="prevention-text">{p}</span>
                      </div>
                    ))}
                  </div>
                </div>


              </div>

              <div className="result-footer">
                <div className="disclaimer">
                  <span className="disclaimer-icon">ℹ️</span>
                  <p>
                    This analysis is for informational purposes only. For accurate diagnosis and treatment,
                    please consult with agricultural experts or plant pathologists.
                  </p>
                </div>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;