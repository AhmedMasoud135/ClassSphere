import cv2
import torch
import numpy as np
import torch.nn as nn
from torchvision.models import mobilenet_v2, MobileNet_V2_Weights
import albumentations as A
from albumentations.pytorch import ToTensorV2
from collections import deque


# ----------- Config -----------
SEQUENCE_LENGTH = 16
FEATURE_DIM = 1280
HIDDEN_DIM = 256
NUM_CLASSES = 1
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ----------- Transforms -----------
val_test_transform = A.Compose([
    A.Resize(224, 224),
    A.Normalize(mean=(0.485, 0.456, 0.406),
                std=(0.229, 0.224, 0.225)),
    ToTensorV2()
])


# ----------- Model Definition -----------
class Model(nn.Module):
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


def create_model(feature_dim, hidden_dim, num_classes, device):
    return Model(feature_dim, hidden_dim, num_classes).to(device)


# ----------- Real-time Webcam Inference -----------
def run_webcam(model, transform, device, threshold=0.5):
    cap = cv2.VideoCapture(0)  
    buffer = deque(maxlen=SEQUENCE_LENGTH)   # Store recent sequence length of frames

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Preprocess frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        transformed = transform(image=rgb)['image']  # tensor (C,H,W)
        buffer.append(transformed)

        label_text = "Collecting frames..."
        color = (0, 255, 255)  # Yellow until prediction available

        if len(buffer) == SEQUENCE_LENGTH:
            frames = torch.stack(list(buffer))  # (seq_len, C, H, W)
            frames = frames.unsqueeze(0).to(device)

            with torch.no_grad():
                prob = model(frames).item()
                pred = 1 if prob > threshold else 0

            if pred == 1:
                label_text = f"Violence ⚠️ ({prob:.2f})"
                color = (0, 0, 255)  # Red
            else:
                label_text = f"Non-Violence ✅ ({prob:.2f})"
                color = (0, 255, 0)  # Green

        # Overlay text
        cv2.putText(frame, label_text, (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        cv2.imshow("Violence Detection - Webcam", frame)

        # Quit with 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# ----------- Main Run -----------
# Load trained model
model = create_model(FEATURE_DIM, HIDDEN_DIM, NUM_CLASSES, DEVICE)
model.load_state_dict(torch.load("best_model.pth", map_location=DEVICE))
model.eval()

run_webcam(model, val_test_transform, DEVICE, threshold=0.7)
