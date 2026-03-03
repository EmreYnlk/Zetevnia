"""
Özel Exception Sınıfları
Uygulamaya özgü hata tipleri
"""
from typing import Optional, Any


class ZetevniaException(Exception):
    """Tüm uygulama hatalarının temel sınıfı"""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = 500,
        detail: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class ValidationError(ZetevniaException):
    """Veri doğrulama hataları"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=422,
            detail={"field": field} if field else None
        )
        self.field = field


class ImageProcessingError(ZetevniaException):
    """Görüntü işleme hataları"""
    
    def __init__(self, message: str, stage: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=400,
            detail={"stage": stage} if stage else None
        )
        self.stage = stage


class ModelInferenceError(ZetevniaException):
    """Model tahmin hataları"""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=500,
            detail={"type": "model_error"}
        )


class RateLimitExceeded(ZetevniaException):
    """Rate limit aşımı"""
    
    def __init__(self, retry_after: int, limit_type: str = "minute"):
        super().__init__(
            message="Çok fazla istek gönderdiniz",
            status_code=429,
            detail={"retry_after": retry_after, "limit_type": limit_type}
        )
        self.retry_after = retry_after


class IPBannedError(ZetevniaException):
    """IP ban hatası"""
    
    def __init__(self, retry_after: int):
        super().__init__(
            message="IP adresiniz geçici olarak engellendi",
            status_code=403,
            detail={"retry_after_seconds": retry_after}
        )
        self.retry_after = retry_after


class ContentTypeError(ZetevniaException):
    """Content-Type hatası"""
    
    def __init__(self, expected: str, received: str):
        super().__init__(
            message=f"Geçersiz Content-Type. Beklenen: {expected}",
            status_code=415,
            detail={"expected": expected, "received": received}
        )


class RequestTooLargeError(ZetevniaException):
    """İstek boyutu hatası"""
    
    def __init__(self, max_size_mb: float):
        super().__init__(
            message=f"İstek boyutu çok büyük. Maksimum: {max_size_mb}MB",
            status_code=413,
            detail={"max_size_mb": max_size_mb}
        )
