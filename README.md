# NetShield

**Your AI-Powered Shield Against Digital Threats**

NetShield (formerly CodeGuardians) is a comprehensive cybersecurity command center designed to protect users from modern digital threats. It unifies advanced detection engines for identifying AI-generated deepfakes, phishing attacks, and malicious URLs into a single, intuitive platform.

## Features

### 🔍 AI Image Detection
Leverages advanced deep learning (EfficientNet-B0) to analyze images and detect AI-generated synthetic content. This feature helps users identify deepfakes and fake profiles, protecting against misinformation and identity theft.
- **Drag-and-Drop Interface**: Easy upload for analysis.
- **Real-time Scoring**: distinct confidence scores for "Real" or "AI-Generated".
- **Visual Feedback**: Immediate visual cues on the analysis result.

### 🎣 Phishing Email Detector
Uses machine learning to analyze email content and subject lines to flag potential phishing attempts.
- **Content Analysis**: Scans text for common phishing patterns.
- **Risk Assessment**: Classifies emails as Safe, Suspicious, or Malicious.

### 🔗 Link & URL Safety Check
Integrates with Google Safe Browsing and internal logic to assess the safety of URLs before you click.
- **Malware Detection**: Identifies known malware distribution sites.
- **Phishing Verification**: Cross-references links against known phishing databases.
- **Infrastructure Analysis**: Checks for suspicious domain characteristics.

### 🔐 Password Strength & Breach View
A complete toolkit for credential security.
- **Strength Meter**: Real-time feedback on password complexity.
- **Breach Check**: (Planned) Integration with "Have I Been Pwned" to check if credentials have been exposed.
- **Secure Generator**: Generates cryptographically strong passwords.

### 🛡️ Cyber Awareness Guide
An interactive educational module to help users stay informed about the latest cyber threats.
- **Threat Encyclopedia**: detailed explanations of common attacks.
- **Best Practices**: Actionable advice for digital hygiene.
- **Self-Assessment**: Quizzes to test your cybersecurity knowledge.

## Installation & Setup

### Prerequisites
- Python 3.8 or higher

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/NetShield.git
cd NetShield
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
```bash
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.\venv\Scripts\activate.bat

# Linux/macOS
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

### Start the Backend Server
```bash
cd backend
python app.py
```
The application will start on `http://127.0.0.1:5000`.

### Navigation
| Route | Feature |
|-------|---------|
| `/` | Home / Dashboard |
| `/ai-detection` | AI Image Detection |
| `/phishing` | Phishing Detector |
| `/url-safety` | URL Safety Checker |
| `/password` | Password Toolkit |
| `/awareness` | Cyber Awareness Guide |

## Project Structure
```
NetShield/
├── backend/            # Flask application & ML models
│   ├── app.py          # Main entry point
│   ├── models/         # Trained models (pkl, pth)
│   ├── templates/      # Jinja2 HTML templates
│   └── ...
├── frontend/           # Static assets & HTML pages
│   ├── assets/         # Images, icons, logos
│   ├── pages/          # Feature HTML pages
│   └── ...
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```