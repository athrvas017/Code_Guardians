# ==============================
# 1) Install & Import Libraries
# ==============================
# pip install kaggle timm albumentations torch torchvision tqdm

import os
import random
import json
from pathlib import Path
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
import albumentations as A
from albumentations.pytorch import ToTensorV2
import timm

# ==============================
# 2) Configuration
# ==============================
SEED = 42
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
IMG_SIZE = 224
BATCH_SIZE = 32 if DEVICE.type == "cuda" else 16
NUM_EPOCHS = 5
TOTAL_IMAGES = 6000  # use 5k-6k images total
TRAIN_SPLIT = 0.9
MODEL_NAME = "resnet18"
LR = 1e-4
WEIGHT_DECAY = 1e-4

# Kaggle dataset
KAGGLE_DATASET = "saurabhbagchi/deepfake-image-detection"
KAGGLE_DIR = Path("data/kaggle/deepfake-image-detection")
KAGGLE_JSON_ENV = "KAGGLE_JSON"      # optional: JSON content for kaggle.json
KAGGLE_USERNAME_ENV = "athrvas017"
KAGGLE_KEY_ENV = "cead26c43289720d0c54eb52b5948d06"
# ==============================
# 3) Reproducibility
# ==============================
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if DEVICE.type == "cuda":
    torch.cuda.manual_seed_all(SEED)
    torch.backends.cudnn.benchmark = True

# ==============================
# 4) Kaggle Auth Helper (optional)
# ==============================
# Priority:
# 1) If ~/.kaggle/kaggle.json exists, use it.
# 2) Else, if KAGGLE_JSON is set, write it to ~/.kaggle/kaggle.json.
# 3) Else, if KAGGLE_USERNAME and KAGGLE_KEY are set, create kaggle.json.

def ensure_kaggle_credentials():
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_file = kaggle_dir / "kaggle.json"

    if kaggle_file.exists():
        return

    kaggle_json = os.getenv(KAGGLE_JSON_ENV)
    if kaggle_json:
        kaggle_dir.mkdir(parents=True, exist_ok=True)
        try:
            data = json.loads(kaggle_json)
        except json.JSONDecodeError:
            raise ValueError("KAGGLE_JSON is set but not valid JSON")

        with open(kaggle_file, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.chmod(kaggle_file, 0o600)
        return

    username = os.getenv(KAGGLE_USERNAME_ENV)
    key = os.getenv(KAGGLE_KEY_ENV)
    if username and key:
        kaggle_dir.mkdir(parents=True, exist_ok=True)
        with open(kaggle_file, "w", encoding="utf-8") as f:
            json.dump({"username": username, "key": key}, f)
        os.chmod(kaggle_file, 0o600)
        return

# ==============================
# 5) Download Dataset from Kaggle
# ==============================
print("Preparing Kaggle dataset...")
ensure_kaggle_credentials()

KAGGLE_DIR.mkdir(parents=True, exist_ok=True)

if not any(KAGGLE_DIR.glob("**/*.jpg")) and not any(KAGGLE_DIR.glob("**/*.png")):
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except Exception as e:
        raise RuntimeError(
            "Kaggle API not available. Install it with: pip install kaggle"
        ) from e

    api = KaggleApi()
    api.authenticate()
    print("Downloading Kaggle dataset...")
    api.dataset_download_files(KAGGLE_DATASET, path=str(KAGGLE_DIR), unzip=True)

# ==============================
# 6) Build Image Index
# ==============================
print("Indexing images...")
image_paths = []
label_map = {"real": 0, "fake": 1, "ai": 1, "deepfake": 1}

for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
    for p in KAGGLE_DIR.rglob(ext):
        parts = [part.lower() for part in p.parts]
        label = None
        for name, idx in label_map.items():
            if name in parts:
                label = idx
                break
        if label is None:
            parent = p.parent.name.lower()
            if parent in label_map:
                label = label_map[parent]

        if label is not None:
            image_paths.append((p, label))

if not image_paths:
    raise RuntimeError("No labeled images found. Check dataset structure in KAGGLE_DIR.")

# Balance classes and limit total images
real_paths = [p for p in image_paths if p[1] == 0]
fake_paths = [p for p in image_paths if p[1] == 1]

random.shuffle(real_paths)
random.shuffle(fake_paths)

per_class = TOTAL_IMAGES // 2
real_paths = real_paths[:per_class]
fake_paths = fake_paths[:per_class]

combined = real_paths + fake_paths
random.shuffle(combined)

# Train/val split
split_idx = int(len(combined) * TRAIN_SPLIT)
train_items = combined[:split_idx]
val_items = combined[split_idx:]

print(f"-> {len(train_items)} train, {len(val_items)} val samples.")

# ==============================
# 7) Transforms
# ==============================
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

train_transform = A.Compose([
    A.RandomResizedCrop(size=(IMG_SIZE, IMG_SIZE), scale=(0.8, 1.0)),
    A.HorizontalFlip(p=0.5),
    A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05, p=0.5),
    A.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ToTensorV2(),
])

val_transform = A.Compose([
    A.Resize(IMG_SIZE, IMG_SIZE),
    A.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ToTensorV2(),
])

# ==============================
# 8) Dataset Class
# ==============================
class KaggleDeepfakeDataset(Dataset):
    def __init__(self, items, transform):
        self.items = items
        self.transform = transform

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        path, label = self.items[int(idx)]
        image = Image.open(path).convert("RGB")
        image = np.array(image)
        image = self.transform(image=image)["image"]
        return image, torch.tensor(label, dtype=torch.long)

pin_memory = DEVICE.type == "cuda"
train_loader = DataLoader(
    KaggleDeepfakeDataset(train_items, train_transform),
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0,
    pin_memory=pin_memory,
)
val_loader = DataLoader(
    KaggleDeepfakeDataset(val_items, val_transform),
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0,
    pin_memory=pin_memory,
)

# ==============================
# 9) Model, Loss & Optimizer
# ==============================
print(f"Creating model ({MODEL_NAME}) on {DEVICE}...")
model = timm.create_model(MODEL_NAME, pretrained=True, num_classes=2).to(DEVICE)
criterion = nn.CrossEntropyLoss(label_smoothing=0.05)
optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)

# ==============================
# 10) Training Loop (Save Best)
# ==============================
best_acc = -1.0
os.makedirs("model", exist_ok=True)
best_path = "model/ai_detector_best.pth"

scaler = torch.cuda.amp.GradScaler(enabled=DEVICE.type == "cuda")

for epoch in range(NUM_EPOCHS):
    model.train()
    running_loss = 0.0
    pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{NUM_EPOCHS} Training")

    for images, labels_batch in pbar:
        images, labels_batch = images.to(DEVICE), labels_batch.to(DEVICE)

        optimizer.zero_grad(set_to_none=True)
        with torch.cuda.amp.autocast(enabled=DEVICE.type == "cuda"):
            outputs = model(images)
            loss = criterion(outputs, labels_batch)

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        running_loss += loss.item()
        pbar.set_postfix({"loss": f"{loss.item():.4f}"})

    avg_loss = running_loss / max(1, len(train_loader))
    print(f"-> Epoch {epoch+1} Average Train Loss: {avg_loss:.4f}")

    # Validation
    model.eval()
    val_correct = 0
    val_total = 0
    with torch.no_grad():
        for images, labels_batch in val_loader:
            images, labels_batch = images.to(DEVICE), labels_batch.to(DEVICE)
            outputs = model(images)
            preds = outputs.argmax(dim=1)
            val_correct += (preds == labels_batch).sum().item()
            val_total += labels_batch.size(0)

    val_acc = val_correct / max(1, val_total)
    print(f"-> Epoch {epoch+1} Validation Accuracy: {val_acc:.4f}")

    if val_acc > best_acc:
        best_acc = val_acc
        torch.save(model.state_dict(), best_path)
        print(f"-> Saved new best model: {best_path}")

# ==============================
# 11) Load Best Model
# ==============================
if os.path.exists(best_path):
    model.load_state_dict(torch.load(best_path, map_location=DEVICE))
    print(f"Loaded best model from {best_path}")

# ==============================
# 12) Prediction / Confidence Function
# ==============================
label_names = ["Real", "Fake"]

def predict(model, dataloader, device):
    model.eval()
    all_preds, all_confs = [], []
    with torch.no_grad():
        for images, _ in dataloader:
            images = images.to(device)
            outputs = model(images)
            probs = F.softmax(outputs, dim=1)
            confs, preds = torch.max(probs, dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_confs.extend(confs.cpu().numpy())
    return all_preds, all_confs

preds, confs = predict(model, val_loader, DEVICE)
for i in range(min(10, len(preds))):
    label = label_names[preds[i]]
    print(f"Predicted: {label}, Confidence: {confs[i]:.4f}")

print("--- Training & Prediction Finished ---")
