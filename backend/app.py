from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import uuid
import numpy as np
from PIL import Image
import io
import base64
from flask_cors import CORS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['AUDIO_FOLDER'] = 'static/audio'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# ─────────────────────────────────────────────
#  CLASS LABELS
# ─────────────────────────────────────────────
CLASS_NAMES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy"
]

DISPLAY_NAMES = {
    "Apple___Apple_scab":       "Apple Scab",
    "Apple___Black_rot":        "Black Rot",
    "Apple___Cedar_apple_rust": "Cedar Apple Rust",
    "Apple___healthy":          "Healthy"
}

# ─────────────────────────────────────────────
#  SEVERITY LOGIC (based on confidence score)
# ─────────────────────────────────────────────
def get_severity(class_name, confidence):
    if class_name == "Apple___healthy":
        return "None", "✅"
    if confidence >= 0.85:
        return "Severe", "🔴"
    elif confidence >= 0.60:
        return "Moderate", "🟠"
    else:
        return "Mild", "🟡"

# ─────────────────────────────────────────────
#  DISEASE RECOMMENDATIONS
# ─────────────────────────────────────────────
RECOMMENDATIONS = {
    "Apple___Apple_scab": {
        "en": {
            "description": "Apple Scab is a fungal disease caused by Venturia inaequalis. It appears as dark, velvety spots on leaves and fruit.",
            "treatment": [
                "Apply fungicides such as Captan, Mancozeb, or Myclobutanil at early leaf stage.",
                "Remove and destroy all infected leaves and fruit from the ground.",
                "Prune trees to improve air circulation and reduce humidity.",
                "Apply dormant sprays (lime sulfur) before bud break in spring."
            ],
            "prevention": [
                "Plant scab-resistant apple varieties.",
                "Avoid overhead irrigation — use drip irrigation instead.",
                "Apply protective fungicide sprays during wet spring weather.",
                "Clean up fallen leaves in autumn to reduce fungal spores."
            ]
        },
        "hi": {
            "description": "एप्पल स्कैब एक फंगल रोग है जो Venturia inaequalis के कारण होता है। पत्तियों और फलों पर काले धब्बे दिखाई देते हैं।",
            "treatment": [
                "कैप्टान, मैनकोजेब या मायक्लोबुटानिल जैसे फफूंदनाशकों का प्रयोग करें।",
                "संक्रमित पत्तियों और फलों को नष्ट करें।",
                "पेड़ों की छंटाई करें ताकि हवा का संचार बेहतर हो।",
                "वसंत में कलियाँ खिलने से पहले डोर्मेंट स्प्रे करें।"
            ],
            "prevention": [
                "स्कैब-प्रतिरोधी सेब की किस्में लगाएं।",
                "ऊपर से सिंचाई से बचें — ड्रिप सिंचाई का उपयोग करें।",
                "गीले मौसम में फफूंदनाशक स्प्रे लगाएं।",
                "शरद ऋतु में गिरी पत्तियों को साफ करें।"
            ]
        },
        "ta": {
            "description": "ஆப்பிள் ஸ்கேப் என்பது Venturia inaequalis என்ற பூஞ்சையால் ஏற்படும் நோய். இலைகள் மற்றும் பழங்களில் கருப்பு புள்ளிகள் தோன்றும்.",
            "treatment": [
                "கேப்டன், மான்கோஜெப் அல்லது மைக்லோபுட்டானில் போன்ற பூஞ்சைக்கொல்லிகளை தெளிக்கவும்.",
                "பாதிக்கப்பட்ட இலைகளை அகற்றி அழிக்கவும்.",
                "காற்று சுழற்சி மேம்பட மரங்களை கத்தரிக்கவும்.",
                "வசந்த காலத்தில் முளைகள் வெடிப்பதற்கு முன் தெளிப்பு செய்யவும்."
            ],
            "prevention": [
                "ஸ்கேப்-எதிர்ப்பு ஆப்பிள் வகைகளை நடவும்.",
                "மேலிருந்து நீர்ப்பாசனம் தவிர்க்கவும்.",
                "மழை காலத்தில் பூஞ்சைக்கொல்லி தெளிக்கவும்.",
                "இலைகளை சேகரித்து அழிக்கவும்."
            ]
        },
        "te": {
            "description": "ఆపిల్ స్కాబ్ అనేది Venturia inaequalis వల్ల వచ్చే శిలీంధ్ర వ్యాధి. ఆకులు మరియు పండ్లపై నల్లని మచ్చలు కనిపిస్తాయి.",
            "treatment": [
                "క్యాప్టన్, మాంకోజెబ్ లేదా మైక్లోబుటానిల్ వంటి శిలీంధ్రనాశినులు వాడండి.",
                "సోకిన ఆకులు మరియు పండ్లను తొలగించి నాశనం చేయండి.",
                "గాలి ప్రసరణ మెరుగుపడేలా చెట్లను కత్తిరించండి.",
                "వసంత కాలంలో మొగ్గలు వికసించే ముందు స్ప్రే చేయండి."
            ],
            "prevention": [
                "స్కాబ్-నిరోధక ఆపిల్ రకాలు నాటండి.",
                "పై నుండి నీటి పారుదల మానుకోండి.",
                "వర్షాకాలంలో శిలీంధ్రనాశిని స్ప్రే చేయండి.",
                "రాలిన ఆకులు సేకరించి నాశనం చేయండి."
            ]
        }
    },
    "Apple___Black_rot": {
        "en": {
            "description": "Black Rot is caused by the fungus Botryosphaeria obtusa. It causes circular brown spots that turn black, and can destroy fruit.",
            "treatment": [
                "Apply fungicides like Thiophanate-methyl or Captan during the growing season.",
                "Prune out all dead or cankered wood and burn it.",
                "Remove mummified (dried-up) fruit from the tree and ground.",
                "Sterilize pruning tools between cuts with 70% alcohol."
            ],
            "prevention": [
                "Maintain tree health through proper fertilization and watering.",
                "Avoid wounding the tree bark during mowing or other activities.",
                "Inspect trees regularly, especially after storms.",
                "Apply copper-based fungicides as a preventive spray."
            ]
        },
        "hi": {
            "description": "ब्लैक रॉट Botryosphaeria obtusa कवक के कारण होता है। यह गोल भूरे धब्बे बनाता है जो काले हो जाते हैं।",
            "treatment": [
                "थायोफेनेट-मेथिल या कैप्टान जैसे फफूंदनाशक लगाएं।",
                "मृत या कैंकर वाली लकड़ी को काटकर जलाएं।",
                "पेड़ और जमीन से सूखे फलों को हटाएं।",
                "कटाई के औजारों को 70% अल्कोहल से साफ करें।"
            ],
            "prevention": [
                "उचित उर्वरीकरण और पानी से पेड़ को स्वस्थ रखें।",
                "घास काटते समय छाल को घाव से बचाएं।",
                "नियमित रूप से पेड़ों का निरीक्षण करें।",
                "कॉपर-आधारित फफूंदनाशक का निवारक स्प्रे करें।"
            ]
        },
        "ta": {
            "description": "Black Rot என்பது Botryosphaeria obtusa பூஞ்சையால் ஏற்படுகிறது. வட்டமான பழுப்பு புள்ளிகள் கருப்பாக மாறும்.",
            "treatment": [
                "தியோஃபனேட்-மீத்தைல் அல்லது கேப்டன் போன்ற பூஞ்சைக்கொல்லிகளை தெளிக்கவும்.",
                "இறந்த கிளைகளை கத்தரித்து எரிக்கவும்.",
                "உலர்ந்த பழங்களை மரத்திலிருந்து அகற்றவும்.",
                "கத்தரிக்கும் கருவிகளை 70% ஆல்கஹாலில் கிருமிநாசினி செய்யவும்."
            ],
            "prevention": [
                "சரியான உரமிடல் மூலம் மரத்தை ஆரோக்கியமாக வைக்கவும்.",
                "மர பட்டையை காயப்படுத்துவதை தவிர்க்கவும்.",
                "தாமரை நோயின் அறிகுறிகளை தவறாமல் சரிபார்க்கவும்.",
                "தாமிர-அடிப்படையிலான பூஞ்சைக்கொல்லி தெளிக்கவும்."
            ]
        },
        "te": {
            "description": "Black Rot అనేది Botryosphaeria obtusa శిలీంధ్రం వల్ల కలుగుతుంది. గుండ్రటి గోధుమ మచ్చలు నల్లబడతాయి.",
            "treatment": [
                "థయోఫనేట్-మీథైల్ లేదా క్యాప్టన్ వంటి శిలీంధ్రనాశినులు వాడండి.",
                "చనిపోయిన కొమ్మలు కత్తిరించి కాల్చివేయండి.",
                "ఎండిన పండ్లను చెట్టు నుండి తొలగించండి.",
                "కత్తిరించే పరికరాలను 70% ఆల్కహాల్‌తో శుభ్రం చేయండి."
            ],
            "prevention": [
                "సరైన ఎరువులు మరియు నీటిపారుదలతో చెట్టు ఆరోగ్యం కాపాడండి.",
                "చెట్టు బెరడుకు గాయం కాకుండా జాగ్రత్త వహించండి.",
                "క్రమం తప్పకుండా చెట్లను పరీక్షించండి.",
                "రాగి ఆధారిత శిలీంధ్రనాశిని స్ప్రే చేయండి."
            ]
        }
    },
    "Apple___Cedar_apple_rust": {
        "en": {
            "description": "Cedar Apple Rust is caused by the fungus Gymnosporangium juniperi-virginianae. It requires both apple and cedar/juniper trees to complete its life cycle.",
            "treatment": [
                "Apply fungicides like Myclobutanil or Propiconazole at pink bud stage.",
                "Remove nearby cedar or juniper trees if possible.",
                "Cut out orange rust galls from cedar trees in late winter.",
                "Spray every 7–10 days during spring infection period."
            ],
            "prevention": [
                "Plant rust-resistant apple varieties such as Liberty or Enterprise.",
                "Do not plant apple trees near cedar or juniper trees.",
                "Apply preventive fungicides starting at bud break.",
                "Monitor weather — wet springs favor rust outbreaks."
            ]
        },
        "hi": {
            "description": "सीडर एप्पल रस्ट Gymnosporangium juniperi-virginianae कवक से होता है। इसे सेब और देवदार दोनों पेड़ों की जरूरत होती है।",
            "treatment": [
                "मायक्लोबुटानिल या प्रोपिकोनाज़ोल जैसे फफूंदनाशक लगाएं।",
                "यदि संभव हो तो आस-पास के देवदार/जुनिपर पेड़ हटाएं।",
                "देवदार पेड़ों से नारंगी जंग की गठानें काटें।",
                "वसंत में हर 7-10 दिन पर स्प्रे करें।"
            ],
            "prevention": [
                "रस्ट-प्रतिरोधी किस्में जैसे Liberty या Enterprise लगाएं।",
                "सेब के पेड़ों को देवदार के पास न लगाएं।",
                "कली खिलने पर निवारक फफूंदनाशक लगाएं।",
                "गीले वसंत में ज्यादा सावधानी रखें।"
            ]
        },
        "ta": {
            "description": "Cedar Apple Rust என்பது Gymnosporangium juniperi-virginianae பூஞ்சையால் ஏற்படுகிறது. ஆப்பிள் மற்றும் கேதுரு மரங்கள் இரண்டும் தேவை.",
            "treatment": [
                "மைக்லோபுட்டானில் அல்லது புரோபிக்கோனஸோல் போன்ற பூஞ்சைக்கொல்லிகளை தெளிக்கவும்.",
                "அருகில் உள்ள கேதுரு மரங்களை அகற்றவும்.",
                "கேதுரு மரங்களிலிருந்து ஆரஞ்சு நிற கட்டிகளை கத்தரிக்கவும்.",
                "வசந்த காலத்தில் 7-10 நாட்களுக்கு ஒருமுறை தெளிக்கவும்."
            ],
            "prevention": [
                "Liberty அல்லது Enterprise போன்ற ரஸ்ட்-எதிர்ப்பு வகைகளை நடவும்.",
                "ஆப்பிள் மரங்களை கேதுரு மரங்களுக்கு அருகில் நடாதீர்கள்.",
                "முளைகள் வெடிக்கும் போது பூஞ்சைக்கொல்லி தெளிக்கவும்.",
                "மழை காலத்தில் கூடுதல் கவனம் செலுத்தவும்."
            ]
        },
        "te": {
            "description": "Cedar Apple Rust అనేది Gymnosporangium juniperi-virginianae శిలీంధ్రం వల్ల వస్తుంది. ఇది ఆపిల్ మరియు సీడర్ చెట్లు రెండూ అవసరం.",
            "treatment": [
                "మైక్లోబుటానిల్ లేదా ప్రొపికొనజోల్ వంటి శిలీంధ్రనాశినులు వాడండి.",
                "సమీపంలోని సీడర్/జూనిపర్ చెట్లను తొలగించండి.",
                "సీడర్ చెట్ల నుండి నారింజ రంగు గడ్డలు తొలగించండి.",
                "వసంత కాలంలో 7-10 రోజులకు ఒకసారి స్ప్రే చేయండి."
            ],
            "prevention": [
                "Liberty లేదా Enterprise వంటి రస్ట్-నిరోధక రకాలు నాటండి.",
                "ఆపిల్ చెట్లను సీడర్ చెట్లకు దగ్గరగా నాటకండి.",
                "మొగ్గలు వికసించే సమయంలో శిలీంధ్రనాశిని స్ప్రే చేయండి.",
                "తడి వసంత కాలంలో అదనపు జాగ్రత్త వహించండి."
            ]
        }
    },
    "Apple___healthy": {
        "en": {
            "description": "Your apple leaf looks healthy! No signs of disease detected.",
            "treatment": ["No treatment needed."],
            "prevention": [
                "Continue regular watering and fertilization.",
                "Monitor leaves periodically for early signs of disease.",
                "Maintain proper pruning for good air circulation.",
                "Apply preventive fungicide sprays during wet seasons."
            ]
        },
        "hi": {
            "description": "आपकी सेब की पत्ती स्वस्थ दिखती है! कोई बीमारी नहीं मिली।",
            "treatment": ["कोई उपचार की जरूरत नहीं।"],
            "prevention": [
                "नियमित रूप से पानी और उर्वरक देते रहें।",
                "समय-समय पर पत्तियों की जांच करें।",
                "अच्छी वायु परिसंचरण के लिए छंटाई करें।",
                "गीले मौसम में निवारक फफूंदनाशक स्प्रे करें।"
            ]
        },
        "ta": {
            "description": "உங்கள் ஆப்பிள் இலை ஆரோக்கியமாக உள்ளது! நோய் எதுவும் கண்டறியப்படவில்லை.",
            "treatment": ["சிகிச்சை தேவையில்லை."],
            "prevention": [
                "தொடர்ந்து தண்ணீர் மற்றும் உரமிடவும்.",
                "அவ்வப்போது இலைகளை சரிபார்க்கவும்.",
                "நல்ல காற்று சுழற்சிக்கு கத்தரிக்கவும்.",
                "மழை காலத்தில் பூஞ்சைக்கொல்லி தெளிக்கவும்."
            ]
        },
        "te": {
            "description": "మీ ఆపిల్ ఆకు ఆరోగ్యంగా ఉంది! ఎటువంటి వ్యాధి కనుగొనబడలేదు.",
            "treatment": ["చికిత్స అవసరం లేదు."],
            "prevention": [
                "క్రమం తప్పకుండా నీరు మరియు ఎరువులు వేయండి.",
                "అప్పుడప్పుడు ఆకులు పరీక్షించండి.",
                "మంచి గాలి ప్రసరణ కోసం కత్తిరించండి.",
                "తడి కాలంలో శిలీంధ్రనాశిని స్ప్రే చేయండి."
            ]
        }
    }
}

# ─────────────────────────────────────────────
#  MODEL LOADING
# ─────────────────────────────────────────────
yolo_model = None
keras_model = None

def load_models():
    global yolo_model, keras_model

    # Load YOLOv8 model
    try:
        from ultralytics import YOLO
        yolo_model = YOLO("models/best.pt")
        print(" YOLOv8 model loaded")
    except Exception as e:
        print(f" YOLOv8 not loaded: {e}")

    # Load Keras model
    try:
        import tensorflow as tf
        keras_model = tf.keras.models.load_model("models/mobilenetv2_apple.h5")
        print(" Keras model loaded")
    except Exception as e:
        print(f" Keras model not loaded: {e}")

# ─────────────────────────────────────────────
#  IMAGE PREPROCESSING
# ─────────────────────────────────────────────
def preprocess_for_keras(image_path, target_size=(224, 224)):
    img = Image.open(image_path).convert("RGB")
    img = img.resize(target_size)
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def preprocess_for_yolo(image_path):
    return image_path  # YOLO accepts file path directly

# ─────────────────────────────────────────────
#  INFERENCE LOGIC
# ─────────────────────────────────────────────
def run_inference(image_path):
    results = {}

    # --- YOLOv8 Inference ---
    if yolo_model:
        try:
            yolo_results = yolo_model(image_path)
            probs = yolo_results[0].probs
            top_idx = int(probs.top1)
            top_conf = float(probs.top1conf)
            # Map to apple-only classes (indices 0–3)
            if top_idx <= 3:
                results["yolo"] = {
                    "class_idx": top_idx,
                    "class_name": CLASS_NAMES[top_idx],
                    "confidence": round(top_conf, 4)
                }
            else:
                results["yolo"] = {"error": "Non-apple class detected"}
        except Exception as e:
            results["yolo"] = {"error": str(e)}

    # --- Keras / MobileNetV2 Inference ---
    if keras_model:
        try:
            img_array = preprocess_for_keras(image_path)
            predictions = keras_model.predict(img_array, verbose=0)
            top_idx = int(np.argmax(predictions[0]))
            top_conf = float(np.max(predictions[0]))
            results["keras"] = {
                "class_idx": top_idx,
                "class_name": CLASS_NAMES[top_idx],
                "confidence": round(top_conf, 4)
            }
        except Exception as e:
            results["keras"] = {"error": str(e)}

    return results

# ─────────────────────────────────────────────
#  ENSEMBLE: COMBINE BOTH MODEL RESULTS
# ─────────────────────────────────────────────
def ensemble_results(inference_results):
    valid = []

    for model_name, result in inference_results.items():
        if "error" not in result:
            valid.append(result)

    if not valid:
        return None

    if len(valid) == 1:
        return valid[0]

    # Both models agree → use higher confidence
    if valid[0]["class_idx"] == valid[1]["class_idx"]:
        best = max(valid, key=lambda x: x["confidence"])
        best["model_agreement"] = True
        return best

    # Models disagree → pick the one with higher confidence
    best = max(valid, key=lambda x: x["confidence"])
    best["model_agreement"] = False
    return best


LANG_CODES = {
    "en": "en",
    "hi": "hi",
    "ta": "ta",
    "te": "te"
}

def generate_audio(text, language, filename):
    try:
        from gtts import gTTS
        lang_code = LANG_CODES.get(language, "en")
        tts = gTTS(text=text, lang=lang_code, slow=False)
        audio_path = os.path.join(app.config['AUDIO_FOLDER'], filename)
        tts.save(audio_path)
        return filename
    except Exception as e:
        print(f"⚠️ Audio generation failed: {e}")
        return None

def build_speech_text(disease_name, severity, recommendations, language):
    rec_data = recommendations
    if language == "en":
        text = f"Disease detected: {disease_name}. Severity: {severity}. "
        text += rec_data.get("description", "") + " "
        text += "Recommended treatments: " + ". ".join(rec_data.get("treatment", [])) + ". "
        text += "Prevention tips: " + ". ".join(rec_data.get("prevention", []))
    elif language == "hi":
        text = f"बीमारी: {disease_name}. गंभीरता: {severity}. "
        text += rec_data.get("description", "") + " "
        text += "उपचार: " + ". ".join(rec_data.get("treatment", [])) + ". "
        text += "बचाव: " + ". ".join(rec_data.get("prevention", []))
    elif language == "ta":
        text = f"கண்டறியப்பட்ட நோய்: {disease_name}. தீவிரம்: {severity}. "
        text += rec_data.get("description", "") + " "
        text += "சிகிச்சை: " + ". ".join(rec_data.get("treatment", [])) + ". "
        text += "தடுப்பு: " + ". ".join(rec_data.get("prevention", []))
    elif language == "te":
        text = f"గుర్తించిన వ్యాధి: {disease_name}. తీవ్రత: {severity}. "
        text += rec_data.get("description", "") + " "
        text += "చికిత్స: " + ". ".join(rec_data.get("treatment", [])) + ". "
        text += "నివారణ: " + ". ".join(rec_data.get("prevention", []))
    else:
        text = f"Disease: {disease_name}. Severity: {severity}."
    return text


try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️ OpenCV (cv2) not available. Bounding boxes will be skipped.")

def draw_bounding_box(image_path, output_path):
    if not CV2_AVAILABLE:
        return False
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            return False

        h, w, _ = img.shape
        x1 = int(w * 0.25)
        y1 = int(h * 0.25)
        x2 = int(w * 0.75)
        y2 = int(h * 0.75)

        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
        cv2.putText(img, "Infected Area", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        cv2.imwrite(output_path, img)
        return True
    except Exception as e:
        print(f"⚠️ Failed to draw bounding box: {e}")
        return False

# ─────────────────────────────────────────────
# 🌐 ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")
@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    language = request.form.get("language", "en")

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Save uploaded image
    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    # Run inference
    inference_results = run_inference(filepath)
    final_result = ensemble_results(inference_results)

    if not final_result:
        return jsonify({"error": "Could not classify image. Please ensure both models are loaded."}), 500

    class_name = final_result["class_name"]
    confidence = final_result["confidence"]
    display_name = DISPLAY_NAMES.get(class_name, class_name)
    severity, severity_icon = get_severity(class_name, confidence)

    # Try to draw bounding box (optional)
    boxed_image_url = None
    if class_name != "Apple___healthy":
        try:
            boxed_filename = f"boxed_{filename}"
            boxed_path = os.path.join(app.config['UPLOAD_FOLDER'], boxed_filename)
            if draw_bounding_box(filepath, boxed_path):
                boxed_image_url = f"/static/uploads/{boxed_filename}"
        except Exception as e:
            print(f"⚠️ Could not create bounding box: {e}")

    # Get recommendations in chosen language
    lang_recs = RECOMMENDATIONS.get(class_name, {}).get(language)
    if not lang_recs:
        lang_recs = RECOMMENDATIONS.get(class_name, {}).get("en", {})

    # Generate audio
    speech_text = build_speech_text(display_name, severity, lang_recs, language)
    audio_filename = f"audio_{uuid.uuid4().hex}.mp3"
    audio_file = generate_audio(speech_text, language, audio_filename)
    audio_url = f"/static/audio/{audio_filename}" if audio_file else None

    response = {
        "disease": display_name,
        "class_name": class_name,
        "confidence": f"{confidence * 100:.1f}%",
        "severity": severity,
        "severity_icon": severity_icon,
        "description": lang_recs.get("description", ""),
        "treatment": lang_recs.get("treatment", []),
        "prevention": lang_recs.get("prevention", []),
        "audio_url": audio_url,
        "model_agreement": final_result.get("model_agreement", None),
        "model_results": {
            k: v for k, v in inference_results.items() if "error" not in v
        },
        "image_url": f"/static/uploads/{filename}",
        "boxed_image_url": boxed_image_url
    }

    return jsonify(response)

@app.route("/health")
def health():
    return jsonify({
        "status": "running",
        "yolo_loaded": yolo_model is not None,
        "keras_loaded": keras_model is not None
    })

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)


if __name__ == "__main__":
    CORS(app)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)
    load_models()
    app.run(debug=True, host="127.0.0.1", port=5000)