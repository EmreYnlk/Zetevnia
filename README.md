# Zetevnia AI Araç Kutusu

Modüler Yapay Zeka Platformu — FastAPI tabanlı, PyTorch destekli.

---

##  Özellikler

- **Rakam Tahmini** — Canvas üzerinde çizilen çok haneli sayıları CNN ile tanıma
- **Karanlık Mod** — Tema desteği
- **Çok Dilli** — Türkçe / İngilizce
- **API İstatistikleri** — Kullanım takibi ve anlık dashboard
- **Güvenlik** — Rate limiting, brute force koruması, input validation

---

## Gereksinimler

| Paket | Versiyon | Açıklama |
|-------|----------|----------|
| **Python** | `>= 3.10` | Runtime |
| **fastapi** | `>= 0.109.0` | Web framework |
| **uvicorn** | `>= 0.27.0` | ASGI sunucu |
| **jinja2** | `>= 3.1.3` | Template engine |
| **python-multipart** | `>= 0.0.6` | Form data parsing |
| **torch** | `>= 2.1.0` | PyTorch (AI/ML) |
| **numpy** | `>= 1.26.0` | Sayısal hesaplama |
| **opencv-python** | `>= 4.9.0` | Görüntü işleme |
| **pillow** | `>= 10.2.0` | Görüntü I/O |
| **pytest** | `>= 8.0.0` | Test framework |
| **httpx** | `>= 0.26.0` | HTTP client (test) |
| **ruff** | `>= 0.2.0` | Linter / formatter |

---

## Kurulum

```bash
# 1. Repoyu klonla
git clone https://github.com/<kullanıcı>/Zetevnia.git
cd Zetevnia

# 2. Virtual environment oluştur
python -m venv venv

# 3. Aktive et
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Windows (CMD)
venv\Scripts\activate.bat

# 4. Bağımlılıkları yükle
pip install -r requirements.txt
```

---

## Kullanım

### Hızlı Başlatma

```bash
# Windows — çift tıkla veya terminalde:
scripts\start.bat

# Veya manuel:
python -m app.main
```

Sunucu varsayılan olarak `http://localhost:8000` adresinde çalışır.

### HTTPS ile Başlatma

```bash
# Önce sertifika oluştur
python scripts/generate_cert.py

# HTTPS modunda başlat
python -m app.main --ssl
```

---

##  Proje Yapısı

```
Zetevnia/
├── app/                        # Ana uygulama paketi
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Konfigürasyon yönetimi
│   ├── constants.py            # Sabitler
│   ├── logger.py               # Loglama sistemi
│   ├── exceptions.py           # Özel exception sınıfları
│   ├── middleware.py           # Güvenlik middleware'leri
│   ├── stats.py                # İstatistik servisi
│   ├── utils.py                # Yardımcı fonksiyonlar
│   ├── api/                    # API router'ları
│   │   ├── stats.py            # İstatistik endpoint'leri
│   │   └── number_guesser.py   # Rakam tahmini endpoint'leri
│   └── services/               # İş mantığı
│       └── number_guesser.py   # Rakam tanıma servisi (CNN)
├── models/                     # Eğitilmiş ML modelleri
│   └── rakam_cnn_model.pth     # CNN model ağırlıkları
├── static/                     # Web varlıkları
│   ├── css/                    # Stil dosyaları
│   ├── js/                     # JavaScript dosyaları
│   └── locales/                # Dil dosyaları (TR/EN)
├── templates/                  # Jinja2 HTML şablonları
│   ├── base.html               # Ana layout
│   ├── index.html              # Ana sayfa
│   └── modules/                # Modül sayfaları
├── scripts/                    # Yardımcı scriptler
│   ├── start.bat               # Windows hızlı başlatma
│   └── generate_cert.py        # SSL sertifika oluşturma
├── tests/                      # Test dosyaları
├── certs/                      # SSL sertifikaları
├── logs/                       # Runtime log dosyaları
├── .env.example                # Örnek konfigürasyon
├── requirements.txt            # Python bağımlılıkları
└── README.md
```

---

## API Endpoint'leri

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/` | `GET` | Ana sayfa |
| `/rakam-tahmini` | `GET` | Rakam tahmini sayfası (canvas UI) |
| `/api/rakam/tahmin-et` | `POST` | Rakam tahmini API |
| `/api/stats/summary` | `GET` | İstatistik özeti |
| `/api/stats/recent` | `GET` | Son tahminler |
| `/api/stats/hourly` | `GET` | Saatlik istatistikler |
| `/api/stats/reset` | `POST` | İstatistikleri sıfırla |

---

## Konfigürasyon

`.env.example` dosyasını `.env` olarak kopyalayıp düzenleyin:

```bash
cp .env.example .env
```

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `ZETEVNIA_HOST` | `0.0.0.0` | Sunucu host |
| `ZETEVNIA_PORT` | `8000` | HTTP port |
| `ZETEVNIA_SSL_PORT` | `8443` | HTTPS port |
| `ZETEVNIA_DEBUG` | `true` | Debug modu |
| `ZETEVNIA_RATE_LIMIT_MINUTE` | `30` | Dakikalık istek limiti |
| `ZETEVNIA_RATE_LIMIT_HOUR` | `500` | Saatlik istek limiti |
| `ZETEVNIA_LOG_LEVEL` | `INFO` | Log seviyesi |
| `ZETEVNIA_USE_GPU` | `false` | GPU kullanımı |

---

##  Güvenlik

- **Rate Limiting** — IP bazlı istek sınırlama (dakika & saat)
- **Brute Force Koruması** — Başarısız denemeler sonrası geçici ban
- **Request Size Limit** — Maksimum 5 MB
- **Content-Type Validation** — JSON zorunluluğu
- **Input Validation** — Base64 ve format kontrolü

---

##  Geliştirme

```bash
# Testleri çalıştır
pytest tests/ -v

# Linting
ruff check .

# Format
ruff format .
```

---

## 📄 Lisans

MIT License
