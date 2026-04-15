import React, { useRef, useState, useEffect } from "react";
import Webcam from "react-webcam";
import axios from "axios";

function UploadWithCamera({ setResult, language }) {
    const webcamRef = useRef(null);
    const fileInputRef = useRef(null);

    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [uploadMode, setUploadMode] = useState(null); // 'file', 'camera', or null
    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState(null);
    const [cameraReady, setCameraReady] = useState(false);

    // Clear error when user interacts
    useEffect(() => {
        if (error && (file || uploadMode)) {
            setError(null);
        }
    }, [file, uploadMode, error]);

    // 📁 Upload from system
    const handleFileChange = (e) => {
        const selected = e.target.files[0];
        if (!selected) return;

        // Validate file type
        if (!selected.type.startsWith('image/')) {
            setError('Please select a valid image file (JPG, PNG, etc.)');
            return;
        }

        // Validate file size (max 10MB)
        if (selected.size > 10 * 1024 * 1024) {
            setError('File size must be less than 10MB');
            return;
        }

        setFile(selected);
        setPreview(URL.createObjectURL(selected));
        setError(null);
    };

    // 📷 Capture from camera
    const captureImage = () => {
        if (!cameraReady) {
            setError('Camera is not ready yet. Please wait...');
            return;
        }

        const imageSrc = webcamRef.current.getScreenshot();
        if (!imageSrc) {
            setError('Failed to capture image. Please try again.');
            return;
        }

        fetch(imageSrc)
            .then((res) => res.blob())
            .then((blob) => {
                const file = new File([blob], "captured.jpg", {
                    type: "image/jpeg",
                });
                setFile(file);
                setPreview(imageSrc);
                setError(null);
            })
            .catch(() => {
                setError('Failed to process captured image.');
            });
    };

    // 🚀 Send to backend
    const handleUpload = async () => {
        if (!file) {
            setError("Please select or capture an image first");
            return;
        }

        setLoading(true);
        setProgress(0);
        setError(null);

        const formData = new FormData();
        formData.append("image", file);
        formData.append("language", language);

        try {
            // Simulate progress for better UX
            const progressInterval = setInterval(() => {
                setProgress(prev => Math.min(prev + 10, 90));
            }, 200);

            const res = await axios.post(
                "http://127.0.0.1:5000/predict",
                formData,
                {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                    timeout: 30000, // 30 second timeout
                }
            );

            clearInterval(progressInterval);
            setProgress(100);

            // Small delay to show 100% progress
            setTimeout(() => {
                setResult(res.data);
                setLoading(false);
                setProgress(0);
            }, 500);

        } catch (err) {
            console.error('Upload error:', err);
            setLoading(false);
            setProgress(0);

            if (err.code === 'ECONNABORTED') {
                setError('Request timed out. Please check your connection and try again.');
            } else if (err.response?.status === 413) {
                setError('Image file is too large. Please use a smaller image.');
            } else if (err.response?.status === 415) {
                setError('Unsupported file format. Please use JPG, PNG, or other common image formats.');
            } else {
                setError(err.response?.data?.error || 'Analysis failed. Please try again with a clearer image.');
            }
        }
    };

    const resetUpload = () => {
        setFile(null);
        setPreview(null);
        setError(null);
        setProgress(0);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    return (
        <div className="upload-container">
            <div className="upload-header">
                <h2>📷 Upload or Capture Apple Leaf Image</h2>
                <p className="upload-instruction">
                    Choose how you'd like to provide the apple leaf image for disease analysis
                </p>
            </div>

            {/* Error Display */}
            {error && (
                <div className="error-message">
                    <span className="error-icon">⚠️</span>
                    <span>{error}</span>
                    <button className="error-close" onClick={() => setError(null)}>×</button>
                </div>
            )}

            {/* Upload Method Selection */}
            <div className="method-selection">
                <div className="upload-controls">
                    <button
                        className={`upload-btn ${uploadMode === 'file' ? 'active' : ''}`}
                        onClick={() => {
                            setUploadMode('file');
                            resetUpload();
                        }}
                    >
                        📁 Browse Files
                    </button>
                    <button
                        className={`camera-btn ${uploadMode === 'camera' ? 'active' : ''}`}
                        onClick={() => {
                            setUploadMode('camera');
                            resetUpload();
                        }}
                    >
                        📷 Use Camera
                    </button>
                </div>
            </div>

            {/* File Upload Section */}
            {uploadMode === 'file' && !preview && (
                <div className="upload-zone">
                    <div className="file-upload-area" onClick={() => fileInputRef.current?.click()}>
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/*"
                            onChange={handleFileChange}
                            className="file-input"
                            style={{ display: 'none' }}
                        />
                        <div className="upload-placeholder">
                            <div className="upload-icon">📎</div>
                            <p>Click to browse or drag & drop an image</p>
                            <small>Supported: JPG, PNG, GIF (Max 10MB)</small>
                        </div>
                    </div>
                </div>
            )}

            {/* Camera Section */}
            {uploadMode === 'camera' && (
                <div className="camera-section">
                    <div className="camera-container">
                        <Webcam
                            ref={webcamRef}
                            screenshotFormat="image/jpeg"
                            width={320}
                            height={240}
                            onUserMedia={() => setCameraReady(true)}
                            onUserMediaError={() => {
                                setError('Camera access denied. Please allow camera permissions and try again.');
                                setCameraReady(false);
                            }}
                            videoConstraints={{
                                facingMode: "environment" // Use back camera on mobile
                            }}
                        />
                        {!cameraReady && (
                            <div className="camera-loading">
                                <div className="loading-spinner"></div>
                                <p>Initializing camera...</p>
                            </div>
                        )}
                    </div>
                    <div className="camera-controls">
                        <button
                            className="capture-btn"
                            onClick={captureImage}
                            disabled={!cameraReady}
                        >
                            📸 Capture Image
                        </button>
                        <p className="camera-tip">Position the apple leaf clearly in the frame</p>
                    </div>
                </div>
            )}

            {/* Image Preview */}
            {preview && (
                <div className="preview-section">
                    <div className="preview-header">
                        <h4>📸 Image Preview</h4>
                        <button className="remove-btn" onClick={resetUpload} title="Remove image">
                            🗑️
                        </button>
                    </div>
                    <div className="preview-container">
                        <img src={preview} alt="Selected leaf" className="preview-image" />
                        <div className="image-info">
                            <span className="file-name">{file?.name || 'Captured Image'}</span>
                            <span className="file-size">
                                {file ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : ''}
                            </span>
                        </div>
                    </div>
                </div>
            )}

            {/* Progress Bar */}
            {loading && (
                <div className="progress-section">
                    <div className="progress-bar">
                        <div
                            className="progress-fill"
                            style={{ width: `${progress}%` }}
                        ></div>
                    </div>
                    <p className="progress-text">
                        Analyzing image... {progress}%
                    </p>
                </div>
            )}

            {/* Analyze Button */}
            <div className="action-section">
                <button
                    className="analyze-btn"
                    onClick={handleUpload}
                    disabled={loading || !file}
                >
                    {loading ? (
                        <>
                            <span className="loading-spinner"></span>
                            Analyzing Disease...
                        </>
                    ) : (
                        <>
                            🔬 Analyze Disease
                            {file && <span className="ready-indicator">✓</span>}
                        </>
                    )}
                </button>

                {!file && !loading && (
                    <p className="help-text">
                        💡 Select or capture an image to enable analysis
                    </p>
                )}
            </div>
        </div>
    );
}

export default UploadWithCamera;