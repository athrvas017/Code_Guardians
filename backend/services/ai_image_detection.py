import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import os
import timm

# Configuration
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model', 'ai_detector_efficientnet.pth')
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class AIDetector:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        try:
            # Initialize model architecture (EfficientNet-B0)
            # Assuming the model was trained with timm or torchvision. 
            # If it's a full checkpoint (not state_dict), we might load differently.
            # But usually it's state_dict. Let's try standard efficientnet_b0 first.
            
            # Trying timm first as it was in requirements
            self.model = timm.create_model('efficientnet_b0', pretrained=False, num_classes=2)
            
            if os.path.exists(MODEL_PATH):
                state_dict = torch.load(MODEL_PATH, map_location=DEVICE)
                self.model.load_state_dict(state_dict)
                self.model.to(DEVICE)
                self.model.eval()
                print(f"Model loaded successfully from {MODEL_PATH}")
            else:
                print(f"Model file not found at {MODEL_PATH}")
                self.model = None

        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None

    def predict(self, image_path):
        if not self.model:
            return {"error": "Model not loaded"}

        try:
            # Preprocessing
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])

            image = Image.open(image_path).convert('RGB')
            input_tensor = transform(image).unsqueeze(0).to(DEVICE)

            with torch.no_grad():
                output = self.model(input_tensor)
                probabilities = torch.nn.functional.softmax(output[0], dim=0)
                
                # Assuming class 0 = Real, class 1 = AI (or vice versa, need to match training)
                # Usually: 0: Real, 1: AI or Fake. 
                # We will return both probabilities.
                
                conf_real = probabilities[0].item() * 100
                conf_ai = probabilities[1].item() * 100
                
                prediction = "ai_generated" if conf_ai > conf_real else "real"
                confidence = conf_ai if prediction == "ai_generated" else conf_real

                return {
                    "prediction": prediction,
                    "confidence": confidence,
                    "probabilities": {
                        "real": conf_real,
                        "ai_generated": conf_ai
                    }
                }

        except Exception as e:
            return {"error": str(e)}

# global instance
detector = AIDetector()

def detect_image(image_path):
    return detector.predict(image_path)
