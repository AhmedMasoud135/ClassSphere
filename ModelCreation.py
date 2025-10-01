import os
import cv2
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision.models import mobilenet_v2, MobileNet_V2_Weights
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np
from tqdm import tqdm
import albumentations as A
from albumentations.pytorch import ToTensorV2



torch.backends.cudnn.deterministic = False  
torch.backends.cudnn.benchmark = True       


# ----------- Hyperparameters -----------
BATCH_SIZE = 3
EPOCHS = 20
LEARNING_RATE = 0.001
SEQUENCE_LENGTH = 12  
FEATURE_DIM = 1280  # MobileNetV2 feature dimension (imagenet)
HIDDEN_DIM = 256
NUM_CLASSES = 1  # Binary classification for sigmoid activation
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")


# ----------- Paths -----------
DATA_ROOT = r"D:\My Course\Projects\DEPI GP R3\Violence Detection\Videos Data\Real Life Violence Dataset"  
VIOLENCE_DIR = os.path.join(DATA_ROOT, "Violence")
NON_VIOLENCE_DIR = os.path.join(DATA_ROOT, "NonViolence")


# ----------- Load video file paths and labels -----------
violence_videos = [os.path.join(VIOLENCE_DIR, f) for f in os.listdir(VIOLENCE_DIR) if f.endswith('.mp4')]
non_violence_videos = [os.path.join(NON_VIOLENCE_DIR, f) for f in os.listdir(NON_VIOLENCE_DIR) if f.endswith('.mp4')]
all_videos = violence_videos + non_violence_videos
all_labels = [1] * len(violence_videos) + [0] * len(non_violence_videos)
#print(f"Total videos: {len(all_labels)}, Violence: {sum(all_labels)}, Non-Violence: {len(all_labels) - sum(all_labels)}")


# ----------- Data Augmentation -----------
train_transform = A.Compose([
    A.Resize(224, 224),
    A.HorizontalFlip(p=0.5),
    A.RandomBrightnessContrast(p=0.2),
    A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ToTensorV2()
])

val_test_transform = A.Compose([
    A.Resize(224, 224),
    A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ToTensorV2()
])


# ----------- Extract Frames ----------- 
def extract_frames(video_path, sequence_length = SEQUENCE_LENGTH, transform=None, device=DEVICE):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_count <= 0:
        cap.release()
        raise RuntimeError("Video contains no frames.")

    # Pick evenly spaced frame indices
    target_indices = np.linspace(0, frame_count - 1, num=sequence_length, dtype=int)

    frames = []
    for i in target_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i))
        ret, frame = cap.read()
        if not ret:
            continue  # Skip if frame not read

        # BGR -> RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (224, 224))  

        if transform is not None:
            frame = transform(image=frame)['image']
        else:
            frame = torch.from_numpy(frame).permute(2, 0, 1).float() / 255.0

        frames.append(frame)

    cap.release()

    # Padding if video too short
    if len(frames) == 0:
        raise RuntimeError("No frames extracted from video.")
    while len(frames) < sequence_length:
        frames.append(frames[-1].clone())

    out = torch.stack(frames)  # (seq_len, C, H, W)
    
    return out



# Split indices for train/val/test
total_samples = len(all_videos)
train_size = int(0.7 * total_samples)
val_size = int(0.15 * total_samples)
test_size = total_samples - train_size - val_size


# Generate indices and split
indices = list(range(total_samples))
np.random.shuffle(indices)  # Random shuffle for splitting
train_indices = indices[:train_size]
val_indices = indices[train_size:train_size + val_size]
test_indices = indices[train_size + val_size:]


# Functions to get data for each split
def get_train_item(self, idx):
    video_path = all_videos[train_indices[idx]]
    label = all_labels[train_indices[idx]]
    frames = extract_frames(video_path, SEQUENCE_LENGTH, train_transform)
    return frames, torch.tensor(label, dtype=torch.float32)

def get_val_item(self, idx):
    video_path = all_videos[val_indices[idx]]
    label = all_labels[val_indices[idx]]
    frames = extract_frames(video_path, SEQUENCE_LENGTH, val_test_transform)
    return frames, torch.tensor(label, dtype=torch.float32)

def get_test_item(self, idx):
    video_path = all_videos[test_indices[idx]]
    label = all_labels[test_indices[idx]]
    frames = extract_frames(video_path, SEQUENCE_LENGTH, val_test_transform)
    return frames, torch.tensor(label, dtype=torch.float32)

# Custom dataset wrappers (using lambda for len and getitem)
train_dataset = type('LambdaDataset', (), {'__len__': lambda self: len(train_indices), '__getitem__': get_train_item})
val_dataset = type('LambdaDataset', (), {'__len__': lambda self: len(val_indices), '__getitem__': get_val_item})
test_dataset = type('LambdaDataset', (), {'__len__': lambda self: len(test_indices), '__getitem__': get_test_item})

train_loader = DataLoader(train_dataset(), batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset(), batch_size=BATCH_SIZE, shuffle=False)
test_loader = DataLoader(test_dataset(), batch_size=BATCH_SIZE, shuffle=False)


# ----------- Model Definition -----------
class Model(nn.Module):
    def __init__(self, feature_dim, hidden_dim, num_classes):
        super().__init__()

        # CNN backbone (MobileNetV2)
        # Use pretrained MobileNetV2 as a feature extractor
        self.cnn = mobilenet_v2(weights=MobileNet_V2_Weights.DEFAULT)

        # Remove the final classifier layer (we only need features, not ImageNet logits)
        self.cnn.classifier = nn.Identity()

        # LSTM for temporal modeling
        # Takes CNN features (feature_dim), outputs hidden_dim
        # Bidirectional=True → output size doubles (hidden_dim * 2)
        self.lstm = nn.LSTM(
            input_size=feature_dim,
            hidden_size=hidden_dim,
            num_layers=1,
            batch_first=True,
            bidirectional=True
        )

        # Fully connected classifier
        # Input: hidden_dim*2 (because of bidirectional LSTM)
        # Output: num_classes (1 for binary classification)
        self.fc = nn.Linear(hidden_dim * 2, num_classes)

        # Sigmoid activation
        # For binary classification, convert logits → probabilities
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        """
        x shape: (batch_size, seq_len, C, H, W)
        """

        batch_size, seq_len, c, h, w = x.size()

        # Step 1: Flatten sequence for CNN
        # Reshape (batch_size * seq_len, C, H, W)
        x = x.view(batch_size * seq_len, c, h, w)

        # Step 2: CNN feature extraction
        features = self.cnn(x)   # (batch_size * seq_len, feature_dim)

        # Step 3: Restore temporal structure
        # Reshape back → (batch_size, seq_len, feature_dim) for LSTM
        features = features.view(batch_size, seq_len, -1)

        # Step 4: LSTM for sequence modeling
        lstm_out, _ = self.lstm(features)  # (batch_size, seq_len, hidden_dim*2)

        # Take the LAST time step’s output for classification
        lstm_out = lstm_out[:, -1, :]  # (batch_size, hidden_dim*2)

        # Step 5: Fully connected classifier
        out = self.fc(lstm_out)

        # Step 6: Sigmoid activation
        return self.sigmoid(out)


# Function to create model instance
def create_model(feature_dim, hidden_dim, num_classes, device):
    model = Model(feature_dim, hidden_dim, num_classes).to(device)
    return model


model = create_model(FEATURE_DIM, HIDDEN_DIM, NUM_CLASSES, DEVICE)


# ----------- Loss, Optimizer and Scheduler -----------
criterion = nn.BCELoss()       # Binary Cross Entropy Loss for binary classification
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=3)


# ----------- Training Loop -----------
def train_epoch(model, loader, criterion, optimizer, device):
    model.train()  # set model to training mode
    running_loss = 0.0
    total_samples = 0

    for inputs, labels in tqdm(loader):
        # Move data to GPU/CPU
        inputs = inputs.to(device)
        labels = labels.to(device).unsqueeze(1)  # (batch_size, 1)

        # Reset gradients
        optimizer.zero_grad()

        # Forward pass
        outputs = model(inputs)

        # Compute loss
        loss = criterion(outputs, labels)

        # Backward pass
        loss.backward()
        optimizer.step()

        # Track loss * number of samples
        batch_size = inputs.size(0)
        running_loss += loss.item() * batch_size
        total_samples += batch_size

        # Clear GPU cache after each batch
        torch.cuda.empty_cache()

    # Average loss per sample
    return running_loss / total_samples


# ----------- Validation Loop -----------
def evaluate(model, loader, criterion, device, phase="val"):
    model.eval()  # set model to evaluation mode
    running_loss = 0.0
    total_samples = 0
    all_preds, all_labels = [], []

    with torch.no_grad():  # no gradients needed
        for inputs, labels in tqdm(loader):
            # Move to GPU/CPU
            inputs = inputs.to(device)
            labels = labels.to(device).unsqueeze(1)

            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, labels)

            # Track loss * batch size
            batch_size = inputs.size(0)
            running_loss += loss.item() * batch_size
            total_samples += batch_size

            # Predictions: threshold at 0.5
            preds = (outputs > 0.5).float()

            # Store results for metrics
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    # Compute metrics
    acc = accuracy_score(all_labels, all_preds)
    prec = precision_score(all_labels, all_preds, zero_division=0)
    rec = recall_score(all_labels, all_preds, zero_division=0)
    f1 = f1_score(all_labels, all_preds, zero_division=0)

    # Print results
    print(f"{phase.capitalize()} Metrics: "
          f"Acc={acc:.4f}, Prec={prec:.4f}, Rec={rec:.4f}, F1={f1:.4f}")

    # Return average loss + metrics
    return running_loss / total_samples, acc, prec, rec, f1



# ----------- Main Training Loop with Early Stopping -----------
best_val_loss = float('inf')   # Start with infinite loss, so any real val_loss will be better
patience = 5                   # Stop if val_loss doesn't improve for 5 epochs
counter = 0                    # Counts epochs without improvement

for epoch in range(EPOCHS):
    # ---- Training phase ----
    model.train()   # Important: set model to training mode (dropout, batchnorm behave differently)
    train_loss = train_epoch(model, train_loader, criterion, optimizer, DEVICE)

    # ---- Validation phase ----
    val_loss, val_acc, val_prec, val_rec, val_f1 = evaluate(
        model, val_loader, criterion, DEVICE, phase='val'
    )

    # ---- Scheduler update ----
    scheduler.step(val_loss)  # Reduce LR if validation loss plateaus

    print(f"Epoch {epoch+1}/{EPOCHS} | "
          f"Train Loss: {train_loss:.4f} | "
          f"Val Loss: {val_loss:.4f} | "
          f"Val Acc: {val_acc:.4f} | "
          f"Val Prec: {val_prec:.4f} | "
          f"Val Rec: {val_rec:.4f} | "
          f"Val F1: {val_f1:.4f}")

    # ---- Early stopping check ----
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        # Save best model
        torch.save(model.state_dict(), "best_model.pth")
        counter = 0  # reset patience counter
    else:
        counter += 1
        if counter >= patience:
            print("Early stopping triggered")
            break

# ---- Load best model back ----
model.load_state_dict(torch.load("best_model.pth", map_location=DEVICE))


# ---- Test phase ----
test_loss, test_acc, test_prec, test_rec, test_f1 = evaluate(
    model, test_loader, criterion, DEVICE, phase='test'
)
print(f"Test Results | Loss={test_loss:.4f}, Acc={test_acc:.4f}, Prec={test_prec:.4f}, Rec={test_rec:.4f}, F1={test_f1:.4f}")
