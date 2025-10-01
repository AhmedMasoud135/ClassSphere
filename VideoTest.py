import torch
import torch.nn as nn
from torchvision.models import mobilenet_v2, MobileNet_V2_Weights
import cv2
import numpy as np
import albumentations as A
from albumentations.pytorch import ToTensorV2


# ----------- Config -----------
SEQUENCE_LENGTH = 12
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


# ----------- Frame Extraction -----------
def extract_frames(video_path, sequence_length=SEQUENCE_LENGTH, transform=None):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    target_indices = np.linspace(0, frame_count - 1, num=sequence_length, dtype=int)

    frames = []
    for i in target_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i))
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (224, 224))
        if transform:
            frame = transform(image=frame)['image']
        else:
            frame = torch.from_numpy(frame).permute(2, 0, 1).float() / 255.0
        frames.append(frame)
    cap.release()

    while len(frames) < sequence_length:
        frames.append(frames[-1].clone())

    return torch.stack(frames)


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


# ----------- Inference Function -----------
def predict_video(model, video_path, transform, device, threshold=0.5):
    model.eval()
    frames = extract_frames(video_path, SEQUENCE_LENGTH, transform)
    frames = frames.unsqueeze(0).to(device)

    with torch.no_grad():
        prob = model(frames).item()
        pred = 1 if prob > threshold else 0
    return prob, pred


# ----------- Main Run -----------
# Load trained model
model = create_model(FEATURE_DIM, HIDDEN_DIM, NUM_CLASSES, DEVICE)
model.load_state_dict(torch.load("best_model.pth", map_location=DEVICE))

# Test on new video
new_video_path = r"C:\Users\IT\Desktop\vv\3.mp4"
prob, pred = predict_video(model, new_video_path, val_test_transform, DEVICE)

if pred == 1:
    print(f"Prediction: Violence ⚠️ | Probability={prob:.4f}")
else:
    print(f"Prediction: Non-Violence ✅ | Probability={prob:.4f}")
