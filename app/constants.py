"""
Uygulama Sabitleri
Tekrar eden string ve değerler burada tanımlanır
"""

# Modül İsimleri
MODULE_RAKAM_TAHMINI = "rakam_tahmini"
MODULE_METIN_ANALIZI = "metin_analizi"
MODULE_GORSEL_TANIMA = "gorsel_tanima"
MODULE_SES_ISLEME = "ses_isleme"
MODULE_TB_TAHMIN = "tb_tahmin"

# API Endpoint'leri
API_PREFIX = "/api"
API_RAKAM_PREFIX = "/api/rakam"
API_STATS_PREFIX = "/api/stats"
API_TB_PREFIX = "/api/tb"

# Desteklenen Görüntü Formatları (Rakam Tahmini - Base64)
SUPPORTED_IMAGE_FORMATS = [
    "data:image/png;base64,",
    "data:image/jpeg;base64,",
    "data:image/jpg;base64,"
]

# Desteklenen Röntgen Dosya Formatları (TB Tahmin - Upload)
SUPPORTED_XRAY_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MAX_XRAY_FILE_SIZE_MB = 10
TB_IMAGE_SIZE = 224  # DenseNet input boyutu

# Base64 Limitleri
MAX_IMAGE_DATA_LENGTH = 7_000_000  # ~5MB base64 encoded
MIN_IMAGE_BYTES = 100

# HTTP Status Mesajları
MSG_SUCCESS = "İşlem başarılı"
MSG_ERROR_GENERIC = "Bir hata oluştu"
MSG_ERROR_VALIDATION = "Doğrulama hatası"
MSG_ERROR_NOT_FOUND = "Kaynak bulunamadı"
MSG_ERROR_RATE_LIMIT = "Çok fazla istek gönderdiniz"
MSG_ERROR_BANNED = "IP adresiniz geçici olarak engellendi"
MSG_ERROR_SIZE_LIMIT = "İstek boyutu çok büyük"
MSG_ERROR_CONTENT_TYPE = "Geçersiz Content-Type"

# Sayfa İsimleri
PAGE_HOME = "anasayfa"
PAGE_RAKAM_TAHMINI = "rakam-tahmini"
PAGE_TB_TAHMIN = "tb-tahmin"

# Template Yolları
TEMPLATE_INDEX = "index.html"
TEMPLATE_RAKAM_TAHMINI = "modules/number_guesser.html"
TEMPLATE_TB_TAHMIN = "modules/tb_predictor.html"

# Zaman Formatları
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
HOUR_FORMAT = "%Y-%m-%d-%H"
