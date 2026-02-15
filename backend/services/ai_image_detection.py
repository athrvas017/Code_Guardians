import os
from gradio_client import Client, handle_file
from dotenv import load_dotenv

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
        if self._client_loaded:
            return self.client is not None

        try:
            if not self.api_url:
                print("HF_API_URL not set")
                return False

            print(f"Connecting to {self.api_url}")
            self.client = Client(self.api_url, token=self.api_token)
            self._client_loaded = True
            print("Connected successfully")
            return True

        except Exception as e:
            print("Connection error:", e)
            self.client = None
            return False

    def predict(self, image_path):
        if not os.path.exists(image_path):
            return {"error": "Image file not found"}

        if not self._ensure_client_loaded():
            return {"error": "Could not connect to AI Detection Service."}

        try:
            result = self.client.predict(
                image=handle_file(image_path),
                api_name="/predict"
            )

            print("RAW HF RESULT:", result)

            if not isinstance(result, dict):
                return {"error": "Invalid response from AI detection service"}

            prediction = result.get("prediction")

            # 🔥 FIX: pull correct key from HF
            confidence = (
                result.get("confidence")
                or result.get("confidence (%)")
                or result.get("real_probability (%)")
                or result.get("fake_probability (%)")
            )

            return {
                "prediction": prediction,
                "confidence": confidence
            }

        except Exception as e:
            print("Prediction error:", e)
            return {"error": str(e)}



_detector = None


def init_model():
    global _detector
    if _detector is None:
        _detector = AIDetector()
        _detector._ensure_client_loaded()


def detect_image(image_path):
    global _detector
    if _detector is None:
        init_model()
    return _detector.predict(image_path)
