from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import torch
import numpy as np
import cv2
import os

# Import your model utils
from model_utils import load_model, ViolencePredictor, val_test_transform, DEVICE, SEQUENCE_LENGTH


# =========================================================
# -------------------- APP SETUP ---------------------------
# =========================================================
app = FastAPI(
    title="Violence Detection API",
    description="API for real-time violence detection using trained deep learning model",
    version="2.0"
)

# Load model only once on startup
model = load_model()
predictor = ViolencePredictor(model, DEVICE, threshold=0.5)
print("[INFO] Violence detection model loaded successfully.")


# =========================================================
# -------------------- API ENDPOINTS -----------------------
# =========================================================
@app.get("/")
def root():
    return {"message": "Violence Detection API is running successfully."}


@app.post("/predict_video/")
async def predict_video(file: UploadFile = File(...)):
    """
    Accepts a video file and returns a violence prediction.
    """
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

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
        return JSONResponse(
            {"status": "error", "message": "Not enough frames in video"},
            status_code=400
        )

    frames = torch.stack(frames).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        prob = model(frames).item()
        pred = 1 if prob > predictor.threshold else 0

    return {
        "status": "success",
        "probability": round(float(prob), 4),
        "violence": bool(pred)
    }


@app.post("/predict_frame/")
async def predict_frame(file: UploadFile = File(...)):
    """
    Accepts a single frame and performs prediction incrementally.
    Frontend can send frames one by one for real-time monitoring.
    """
    contents = await file.read()
    npimg = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    prob, pred = predictor.add_frame(frame)

    if prob is None:
        return {"status": "collecting", "message": "Waiting for enough frames."}

    return {
        "status": "success",
        "probability": round(float(prob), 4),
        "violence": bool(pred)
    }



