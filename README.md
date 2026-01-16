# Code_Guardians

A Flask-based web application for URL safety checking and security services.

## Prerequisites

- Python 3.8 or higher

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Code_Guardians.git
cd Code_Guardians
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

```bash
# Linux/macOS
source venv/bin/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.\venv\Scripts\activate.bat
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

### Start the Flask Server

```bash
cd backend
python app.py
```

The application will start on `http://127.0.0.1:5000` by default.

### Available Pages

| Route | Description |
|-------|-------------|
| `/` | Home / Landing Page |
| `/password` | Password Security Toolkit |
| `/url-safety` | URL Safety Checker |

## Project Structure

```
Code_Guardians/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── models.py           # Database models
│   ├── services/           # Business logic services
│   ├── templates/          # HTML templates (url_safety.html)
│   └── utils/              # Utility functions
├── frontend/
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── pages/              # HTML pages (index.html, pass.html)
├── requirements.txt        # Python dependencies
└── README.md
```

## Dependencies

- Flask 3.0.3
- Flask-SQLAlchemy 3.1.1
- SQLAlchemy 2.0.30
- requests 2.32.3
- validators 0.22.0