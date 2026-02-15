import os
from gradio_client import Client, handle_file
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

HF_API_URL = os.getenv("HF_API_URL")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")


class AIDetector:
    def __init__(self):
        self.client = None
        self._client_loaded = False
        self.api_url = HF_API_URL
        self.api_token = HF_API_TOKEN

    def _ensure_client_loaded(self):
        """Lazy load the Gradio client"""
        if self._client_loaded:
            return self.client is not None

        try:
            if not self.api_url:
                print("ERROR: HF_API_URL not set in .env")
                return False

            print(f"Connecting to AI Detector Space at {self.api_url}...")

            # ✅ FIXED: use `token=` instead of `hf_token=`
            self.client = Client(self.api_url, token=self.api_token)

            print("Connected to AI Detector Space successfully.")
            self._client_loaded = True
            return True

        except Exception as e:
            print(f"Error connecting to HF Space: {e}")
            self.client = None
            return False

    def predict(self, image_path):
        """Send image to Hugging Face Space for prediction"""

        if not os.path.exists(image_path):
            return {"error": "Image file not found"}

        if not self._ensure_client_loaded():
            return {"error": "Could not connect to AI Detection Service."}

        try:
            result = self.client.predict(
                image=handle_file(image_path),
                api_name="/predict"  # default endpoint for Gradio Interface
            )
            
            # Ensure result is a dictionary
            if not isinstance(result, dict):
                print(f"Unexpected response type from HF: {type(result)}")
                return {"error": "Invalid response from AI detection service"}

            # Reformat output to match requested JSON structure
            formatted_result = {
                "prediction": result.get("prediction"),
                "confidence (%)": result.get("confidence"),
                "real_probability (%)": result.get("real_probability"),
                "fake_probability (%)": result.get("fake_probability")
            }
            return formatted_result

        except Exception as e:
            print(f"Prediction error: {e}")
            return {"error": str(e)}


# Lazy global instance
_detector = None


def init_model():
    """Initialize detector once at app startup"""
    global _detector
    if _detector is None:
        _detector = AIDetector()
        _detector._ensure_client_loaded()


def detect_image(image_path):
    """Main function your app should call"""
    global _detector
    if _detector is None:
        init_model()
    return _detector.predict(image_path)
