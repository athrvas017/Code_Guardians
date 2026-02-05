import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import os
import gc

# Configuration
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model', 'ai_detector_efficientnet.pth')
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Memory-safe constants
MAX_IMAGE_SIZE = 1024  # Max dimension in pixels
MAX_FILE_SIZE_MB = 10  # Max file size in MB


class AIDetector:
    def __init__(self):
        self.model = None
        self._model_loaded = False

    def _ensure_model_loaded(self):
        """Lazy load model only when needed to avoid memory spike on import"""
        if self._model_loaded:
            return self.model is not None
            
        try:
            import timm
            
            # Initialize model architecture (EfficientNet-B0)
            self.model = timm.create_model('efficientnet_b0', pretrained=False, num_classes=2)
            
            if os.path.exists(MODEL_PATH):
                # Load with weights_only=True for security and memory efficiency
                state_dict = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True)
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
        finally:
            self._model_loaded = True
            
        return self.model is not None

    def _resize_image_if_needed(self, image):
        """
        Memory-safe resize: limit image to MAX_IMAGE_SIZE on longest side.
        This prevents memory exhaustion with very large images.
        """
        width, height = image.size
        max_dim = max(width, height)
        
        if max_dim > MAX_IMAGE_SIZE:
            ratio = MAX_IMAGE_SIZE / max_dim
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"Resized image from {width}x{height} to {new_width}x{new_height}")
            
        return image

    def _validate_file(self, image_path):
        """Validate file size before processing"""
        if not os.path.exists(image_path):
            return False, "Image file not found"
            
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            return False, f"File too large ({file_size_mb:.1f}MB). Maximum allowed: {MAX_FILE_SIZE_MB}MB"
            
        return True, None

    def predict(self, image_path):
        # Validate file first
        valid, error = self._validate_file(image_path)
        if not valid:
            return {"error": error}
        
        # Lazy load model
        if not self._ensure_model_loaded():
            return {"error": "Model not loaded. Please check server logs."}

        try:
            # Open and resize image for memory safety
            image = Image.open(image_path).convert('RGB')
            image = self._resize_image_if_needed(image)
            
            # Preprocessing - transforms.Resize expects (H, W) format
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])

            input_tensor = transform(image).unsqueeze(0).to(DEVICE)
            
            # Close PIL image to free memory
            image.close()

            with torch.no_grad():
                output = self.model(input_tensor)
                probabilities = torch.nn.functional.softmax(output[0], dim=0)
                
                # Class 0 = Real, Class 1 = AI Generated
                conf_real = probabilities[0].item() * 100
                conf_ai = probabilities[1].item() * 100
                
                prediction = "ai_generated" if conf_ai > conf_real else "real"
                confidence = conf_ai if prediction == "ai_generated" else conf_real

                result = {
                    "prediction": prediction,
                    "confidence": round(confidence, 2),
                    "probabilities": {
                        "real": round(conf_real, 2),
                        "ai_generated": round(conf_ai, 2)
                    }
                }

            # Cleanup tensors to free memory
            del input_tensor, output, probabilities
            if DEVICE.type == "cuda":
                torch.cuda.empty_cache()
            gc.collect()

            return result

        except Exception as e:
            # Cleanup on error
            gc.collect()
            return {"error": str(e)}


# Lazy-initialized global instance (model loads on first use, not on import)
_detector = None

def detect_image(image_path):
    """Main entry point for AI image detection"""
    global _detector
    if _detector is None:
        _detector = AIDetector()
    return _detector.predict(image_path)
