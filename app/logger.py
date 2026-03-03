"""
Logging Konfigürasyonu
Merkezi loglama sistemi
"""
import logging
import os
from datetime import datetime
from typing import Optional
from .config import settings


class ZetevniaLogger:
    """Uygulama için özelleştirilmiş logger"""
    
    _instance: Optional['ZetevniaLogger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self) -> None:
        """Logger'ı yapılandır"""
        self._logger = logging.getLogger("zetevnia")
        self._logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
        
        # Formatter
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # File Handler (opsiyonel)
        if settings.LOG_FILE:
            try:
                log_dir = os.path.dirname(settings.LOG_FILE)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                
                file_handler = logging.FileHandler(
                    settings.LOG_FILE, 
                    encoding='utf-8'
                )
                file_handler.setFormatter(formatter)
                self._logger.addHandler(file_handler)
            except Exception as e:
                self._logger.warning(f"Log dosyası oluşturulamadı: {e}")
    
    def info(self, message: str, **kwargs) -> None:
        """Info seviyesinde log"""
        self._logger.info(self._format_message(message, kwargs))
    
    def warning(self, message: str, **kwargs) -> None:
        """Warning seviyesinde log"""
        self._logger.warning(self._format_message(message, kwargs))
    
    def error(self, message: str, **kwargs) -> None:
        """Error seviyesinde log"""
        self._logger.error(self._format_message(message, kwargs))
    
    def debug(self, message: str, **kwargs) -> None:
        """Debug seviyesinde log"""
        self._logger.debug(self._format_message(message, kwargs))
    
    def security(self, message: str, **kwargs) -> None:
        """Güvenlik olayları için özel log"""
        self._logger.warning(f"[SECURITY] {self._format_message(message, kwargs)}")
    
    def api_call(self, endpoint: str, method: str, status: int, ip: str, duration_ms: float = 0) -> None:
        """API çağrısı logu"""
        self._logger.info(
            f"[API] {method} {endpoint} | Status: {status} | IP: {ip} | {duration_ms:.2f}ms"
        )
    
    def _format_message(self, message: str, extras: dict) -> str:
        """Ek bilgileri mesaja ekle"""
        if extras:
            extra_str = " | ".join(f"{k}={v}" for k, v in extras.items())
            return f"{message} | {extra_str}"
        return message


# Singleton instance
logger = ZetevniaLogger()
