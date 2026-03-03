#  Zetevnia AI Toolbox

Modular Artificial Intelligence Platform — FastAPI based, PyTorch powered.

---

##  Features

- **Digit Guessing** — Multi-digit number recognition drawn on a canvas using CNN
- **Tuberculosis Prediction** — TB detection from chest X-rays using CNN ensemble models
- **Dark Mode** — Theme support
- **Multilingual** — Turkish / English
- **API Statistics** — Usage tracking and real-time dashboard
- **Security** — Rate limiting, brute force protection, input validation

---

##  Requirements

| Package | Version | Description |
|-------|----------|----------|
| **Python** | `>= 3.10` | Runtime |
| **fastapi** | `>= 0.109.0` | Web framework |
| **uvicorn** | `>= 0.27.0` | ASGI server |
| **jinja2** | `>= 3.1.3` | Template engine |
| **python-multipart** | `>= 0.0.6` | Form data parsing |
| **torch** | `>= 2.1.0` | PyTorch (AI/ML) |
| **numpy** | `>= 1.26.0` | Numerical computing |
| **opencv-python** | `>= 4.9.0` | Image processing |
| **pillow** | `>= 10.2.0` | Image I/O |
| **pytest** | `>= 8.0.0` | Test framework |
| **httpx** | `>= 0.26.0` | HTTP client (test) |
| **ruff** | `>= 0.2.0` | Linter / formatter |

---

##  Installation

```bash
# 1. Clone the repository
git clone https://github.com/EmreYnlk/Zetevnia.git
cd Zetevnia

# 2. Create virtual environment
python -m venv venv

# 3. Activate
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Windows (CMD)
venv\Scripts\activate.bat

# 4. Install dependencies
pip install -r requirements.txt
```

---

##  Usage

### Quick Start

```bash
# Windows — double click or in terminal:
scripts\start.bat

# Or manual:
python -m app.main
```

The server runs on `http://localhost:8000` by default.

---

## Project Structure

```
Zetevnia/
├── app/                        # Main application package
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Configuration management
│   ├── constants.py            # Constants
│   ├── logger.py               # Logging system
│   ├── exceptions.py           # Custom exception classes
│   ├── middleware.py           # Security middlewares
│   ├── stats.py                # Statistics service
│   ├── utils.py                # Utility functions
│   ├── api/                    # API routers
│   │   ├── stats.py            # Statistics endpoints
│   │   ├── tb_predictor.py     # TB prediction endpoints
│   │   └── number_guesser.py   # Digit guessing endpoints
│   └── services/               # Business logic
│       ├── tb_predictor.py     # TB recognition service (Ensemble CNN)
│       └── number_guesser.py   # Digit recognition service (CNN)
├── models/                     # Trained ML models
│   ├── rakam_cnn_model.pth     # CNN model weights
│   └── tb/                     # TB prediction models (DenseNet etc.)
├── static/                     # Web assets
│   ├── css/                    # Style files
│   ├── js/                     # JavaScript files
│   └── locales/                # Language files (TR/EN)
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Main layout
│   ├── index.html              # Home page
│   └── modules/                # Module pages
├── scripts/                    # Helper scripts
│   ├── start.bat               # Windows quick start
│   └── generate_cert.py        # SSL certificate generation
├── tests/                      # Test files
├── certs/                      # SSL certificates
├── logs/                       # Runtime log files
├── .env.example                # Example configuration
├── requirements.txt            # Python dependencies
└── README.md
```

---

##  API Endpoints

| Endpoint | Method | Description |
|----------|--------|----------|
| `/` | `GET` | Home page |
| `/rakam-tahmini` | `GET` | Digit guessing page (canvas UI) |
| `/tb-tahmin` | `GET` | Tuberculosis prediction page |
| `/api/rakam/tahmin-et` | `POST` | Digit guessing API |
| `/api/tb/models` | `GET` | List available TB models |
| `/api/tb/predict` | `POST` | TB prediction API from X-ray image |
| `/api/stats/summary` | `GET` | Statistics summary |
| `/api/stats/recent` | `GET` | Recent predictions |
| `/api/stats/hourly` | `GET` | Hourly statistics |
| `/api/stats/reset` | `POST` | Reset statistics |

---

## Configuration

Copy `.env.example` as `.env` and edit:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|----------|------------|----------|
| `ZETEVNIA_HOST` | `0.0.0.0` | Server host |
| `ZETEVNIA_PORT` | `8000` | HTTP port |
| `ZETEVNIA_SSL_PORT` | `8443` | HTTPS port |
| `ZETEVNIA_DEBUG` | `true` | Debug mode |
| `ZETEVNIA_RATE_LIMIT_MINUTE` | `30` | Requests limit per minute |
| `ZETEVNIA_RATE_LIMIT_HOUR` | `500` | Requests limit per hour |
| `ZETEVNIA_LOG_LEVEL` | `INFO` | Log level |
| `ZETEVNIA_USE_GPU` | `false` | GPU usage |

---

##  Security

- **Rate Limiting** — IP-based request limiting (minute & hour)
- **Brute Force Protection** — Temporary ban after failed attempts
- **Request Size Limit** — Maximum 5 MB
- **Content-Type Validation** — JSON requisite
- **Input Validation** — Base64 and format check

---

##  Development

```bash
# Run tests
pytest tests/ -v

# Linting
ruff check .

# Format
ruff format .
```
