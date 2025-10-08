import torch
import torch.nn as nn
import cv2
import numpy as np
import albumentations as A
from albumentations.pytorch import ToTensorV2
from torchvision.models import mobilenet_v2, MobileNet_V2_Weights
from collections import deque
import base64
import os

# -------------------------------------------------
# Configuration
# -------------------------------------------------
SEQUENCE_LENGTH = 16
FEATURE_DIM = 1280
HIDDEN_DIM = 256
NUM_CLASSES = 1
THRESHOLD = 0.5
MODEL_PATH = "best_model.pth"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -------------------------------------------------
# Frame Transform
# -------------------------------------------------
val_test_transform = A.Compose([
    A.Resize(224, 224),
    A.Normalize(mean=(0.485, 0.456, 0.406),
                std=(0.229, 0.224, 0.225)),
    ToTensorV2()
])

# -------------------------------------------------
# Model Definition
# -------------------------------------------------
class ViolenceDetectionModel(nn.Module):
    def __init__(self, feature_dim, hidden_dim, num_classes):
        super().__init__()
        self.cnn = mobilenet_v2(weights=MobileNet_V2_Weights.DEFAULT)
        self.cnn.classifier = nn.Identity()
        self.lstm = nn.LSTM(
            input_size=feature_dim,
            hidden_size=hidden_dim,
            num_layers=1,
            batch_first=True,
            bidirectional=True
        )
        self.fc = nn.Linear(hidden_dim * 2, num_classes)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        b, s, c, h, w = x.size()
        x = x.view(b * s, c, h, w)
        features = self.cnn(x)
        features = features.view(b, s, -1)
        lstm_out, _ = self.lstm(features)
        lstm_out = lstm_out[:, -1, :]
        out = self.fc(lstm_out)
        return self.sigmoid(out)


# -------------------------------------------------
# Helper: Load Model Once
# -------------------------------------------------
def load_model():
    model = ViolenceDetectionModel(FEATURE_DIM, HIDDEN_DIM, NUM_CLASSES).to(DEVICE)
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        model.eval()
        print(f"[INFO] Model loaded successfully from {MODEL_PATH}")
    else:
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    return model


# -------------------------------------------------
# Helper: Frame Conversion
# -------------------------------------------------
def decode_base64_image(base64_str):
    """Decode base64 image string to numpy array (RGB)."""
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    img_bytes = base64.b64decode(base64_str)
    img_array = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def preprocess_frame(frame):
    """Apply Albumentations transform and return tensor."""
    return val_test_transform(image=frame)['image']


# -------------------------------------------------
# Violence Detection Logic
# -------------------------------------------------
class ViolencePredictor:
    def __init__(self, model, device, sequence_length=SEQUENCE_LENGTH, threshold=THRESHOLD):
        self.model = model
        self.device = device
        self.sequence_length = sequence_length
        self.threshold = threshold
        self.buffer = deque(maxlen=sequence_length)

    def add_frame(self, base64_image):
        """Add one frame (base64) to buffer."""
        frame = decode_base64_image(base64_image)
        transformed = preprocess_frame(frame)
        self.buffer.append(transformed)
        return len(self.buffer)

    def is_ready(self):
        """Check if enough frames are collected."""
        return len(self.buffer) == self.sequence_length

    def predict(self):
        """Run prediction if sequence ready."""
        if not self.is_ready():
            return {
                "status": "waiting",
                "message": f"Need {self.sequence_length - len(self.buffer)} more frames."
            }

        frames = torch.stack(list(self.buffer)).unsqueeze(0).to(self.device)
        with torch.no_grad():
            prob = self.model(frames).item()
            pred = 1 if prob > self.threshold else 0

        return {
            "status": "success",
            "prediction": "Violence" if pred else "Non-Violence",
            "probability": round(float(prob), 4)
        }


# -------------------------------------------------
# Initialize Model and Predictor
# -------------------------------------------------
model = load_model()
predictor = ViolencePredictor(model, DEVICE)
print("[INFO] Violence detection model ready for frame-based inference.")
