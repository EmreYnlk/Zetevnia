"""
Uygulama Konfigürasyonu
Environment variables ve varsayılan değerler
"""
import os
from typing import List
from functools import lru_cache


class Settings:
    """Uygulama ayarları - environment variable'lardan veya varsayılanlardan okunur"""
    
    # Uygulama Bilgileri
    APP_NAME: str = "Zetevnia AI Araç Kutusu"
    APP_VERSION: str = "2.1.0"
    APP_DESCRIPTION: str = "Modüler Yapay Zeka Platformu"
    
    # Sunucu Ayarları
    HOST: str = os.getenv("ZETEVNIA_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("ZETEVNIA_PORT", "8000"))
    SSL_PORT: int = int(os.getenv("ZETEVNIA_SSL_PORT", "8443"))
    DEBUG: bool = os.getenv("ZETEVNIA_DEBUG", "true").lower() == "true"
    
    # CORS Ayarları
    CORS_ORIGINS: List[str] = os.getenv(
        "ZETEVNIA_CORS_ORIGINS", 
        "http://localhost:8000,http://127.0.0.1:8000"
    ).split(",")
    CORS_ALLOW_ALL: bool = os.getenv("ZETEVNIA_CORS_ALLOW_ALL", "true").lower() == "true"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("ZETEVNIA_RATE_LIMIT_MINUTE", "30"))
    RATE_LIMIT_PER_HOUR: int = int(os.getenv("ZETEVNIA_RATE_LIMIT_HOUR", "500"))
    
    # Request Size Limit
    MAX_REQUEST_SIZE_MB: float = float(os.getenv("ZETEVNIA_MAX_REQUEST_MB", "5.0"))
    
    # Brute Force Protection
    MAX_FAILED_ATTEMPTS: int = int(os.getenv("ZETEVNIA_MAX_FAILED_ATTEMPTS", "10"))
    BAN_DURATION_MINUTES: int = int(os.getenv("ZETEVNIA_BAN_DURATION_MINUTES", "5"))
    
    # Model Ayarları
    MODEL_PATH: str = os.getenv(
        "ZETEVNIA_MODEL_PATH", 
        "models/rakam_cnn_model.pth"
    )
    TB_MODELS_DIR: str = os.getenv(
        "ZETEVNIA_TB_MODELS_DIR",
        "models/tb"
    )
    USE_GPU: bool = os.getenv("ZETEVNIA_USE_GPU", "false").lower() == "true"
    
    # İstatistik Ayarları
    MAX_RECENT_PREDICTIONS: int = int(os.getenv("ZETEVNIA_MAX_RECENT_PREDICTIONS", "100"))
    
    # SSL Ayarları
    SSL_CERT_DIR: str = os.getenv("ZETEVNIA_SSL_CERT_DIR", "certs")
    SSL_KEY_FILE: str = "key.pem"
    SSL_CERT_FILE: str = "cert.pem"
    
    # Logging
    LOG_LEVEL: str = os.getenv("ZETEVNIA_LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("ZETEVNIA_LOG_FILE", "logs/zetevnia.log")
    
    @classmethod
    def get_ssl_paths(cls) -> tuple:
        """SSL sertifika yollarını döndür"""
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cert_dir = os.path.join(base_dir, cls.SSL_CERT_DIR)
        return (
            os.path.join(cert_dir, cls.SSL_KEY_FILE),
            os.path.join(cert_dir, cls.SSL_CERT_FILE)
        )


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance döndür"""
    return Settings()


# Global erişim için
settings = get_settings()
