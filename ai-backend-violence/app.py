from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import numpy as np
import cv2
import os

# Import your model utils
from model_utils import load_model, ViolencePredictor, val_test_transform, DEVICE, SEQUENCE_LENGTH

# =========================================================
# -------------------- APP SETUP ---------------------------
# =========================================================
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load model once
model = load_model()
predictor = ViolencePredictor(model, DEVICE, threshold=0.5)
print("[INFO] Violence detection model loaded successfully.")


# =========================================================
# -------------------- API ENDPOINTS -----------------------
# =========================================================

@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Violence Detection API (Flask) is running successfully."})


@app.route("/detect_frame", methods=["POST"])
def detect_frame():
    """
    Accepts a base64 encoded frame and performs violence detection incrementally.
    Requires 16 frames before making a prediction.
    """
    try:
        data = request.get_json()
        if not data or "image" not in data:
            return jsonify({"status": "error", "message": "No image provided"}), 400

        base64_image = data["image"]
        
        # Add frame to predictor buffer
        buffer_size = predictor.add_frame(base64_image)
        
        # Check if we have enough frames
        if not predictor.is_ready():
            return jsonify({
                "status": "waiting",
                "message": f"Collecting frames... ({buffer_size}/{SEQUENCE_LENGTH})",
                "buffer_size": buffer_size
            })
        
        # Make prediction
        result = predictor.predict()
        return jsonify(result)
        
    except Exception as e:
        print(f"[ERROR] Detection error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/reset_buffer", methods=["POST"])
def reset_buffer():
    """
    Reset the frame buffer to start a new detection session.
    """
    try:
        predictor.buffer.clear()
        return jsonify({
            "status": "success",
            "message": "Buffer reset successfully"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/predict_video/", methods=["POST"])
def predict_video():
    """
    Accepts a video file and returns a violence prediction.
    """
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file provided"}), 400

    file = request.files["file"]
    temp_path = f"temp_{file.filename}"
    file.save(temp_path)

    cap = cv2.VideoCapture(temp_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    indices = np.linspace(0, frame_count - 1, SEQUENCE_LENGTH, dtype=int)

    frames = []
    for i in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i))
        ret, frame = cap.read()
        if not ret:
            continue
        frame = predictor.preprocess_frame(frame)
        frames.append(frame)
    cap.release()
    os.remove(temp_path)

    if len(frames) < SEQUENCE_LENGTH:
        return jsonify({"status": "error", "message": "Not enough frames in video"}), 400

    frames = torch.stack(frames).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        prob = model(frames).item()
        pred = 1 if prob > predictor.threshold else 0

    return jsonify({
        "status": "success",
        "probability": round(float(prob), 4),
        "violence": bool(pred)
    })


@app.route("/predict_frame/", methods=["POST"])
def predict_frame():
    """
    Accepts a single frame and performs prediction incrementally.
    """
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file provided"}), 400

    file = request.files["file"]
    npimg = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    prob, pred = predictor.add_frame(frame)

    if prob is None:
        return jsonify({"status": "collecting", "message": "Waiting for enough frames."})

    return jsonify({
        "status": "success",
        "probability": round(float(prob), 4),
        "violence": bool(pred)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

