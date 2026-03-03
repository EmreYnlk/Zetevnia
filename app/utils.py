"""
Yardımcı Fonksiyonlar
Ortak kullanılan utility fonksiyonları
"""
from fastapi import Request
from typing import Optional
import re
import base64


def get_client_ip(request: Request) -> str:
    """
    İstemci IP adresini al (proxy arkasında da çalışır)
    
    Args:
        request: FastAPI request objesi
        
    Returns:
        İstemci IP adresi
    """
    # X-Forwarded-For header'ı kontrol et (proxy/load balancer arkasında)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # İlk IP gerçek istemci IP'sidir
        return forwarded.split(",")[0].strip()
    
    # X-Real-IP header'ı kontrol et (nginx)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Doğrudan bağlantı
    if request.client:
        return request.client.host
    
    return "unknown"


def validate_base64_image(data: str) -> tuple[bool, Optional[str]]:
    """
    Base64 görüntü verisini doğrula
    
    Args:
        data: Base64 encoded görüntü verisi
        
    Returns:
        (geçerli_mi, hata_mesajı)
    """
    from .constants import SUPPORTED_IMAGE_FORMATS, MIN_IMAGE_BYTES
    
    if not data or len(data.strip()) == 0:
        return False, "Görüntü verisi boş olamaz"
    
    if not data.startswith("data:image/"):
        return False, "Geçersiz görüntü formatı. data:image/ ile başlamalı"
    
    if not any(data.startswith(fmt) for fmt in SUPPORTED_IMAGE_FORMATS):
        return False, "Desteklenmeyen görüntü formatı. PNG veya JPEG olmalı"
    
    try:
        base64_part = data.split(",")[1] if "," in data else data
        
        if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', base64_part):
            return False, "Geçersiz base64 karakterleri"
        
        decoded = base64.b64decode(base64_part)
        
        if len(decoded) < MIN_IMAGE_BYTES:
            return False, "Görüntü verisi çok küçük"
            
    except Exception:
        return False, "Base64 decode hatası"
    
    return True, None


def format_uptime(seconds: int) -> str:
    """
    Saniyeyi okunabilir formata çevir
    
    Args:
        seconds: Toplam saniye
        
    Returns:
        Formatlanmış string (örn: "2g 5s 30d 15sn")
    """
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)
    
    return f"{days}g {hours}s {minutes}d {secs}sn"


def sanitize_error_message(message: str) -> str:
    """
    Hata mesajını güvenli hale getir (hassas bilgileri kaldır)
    
    Args:
        message: Ham hata mesajı
        
    Returns:
        Güvenli hata mesajı
    """
    sensitive_patterns = [
        r'password[=:]\s*\S+',
        r'api[_-]?key[=:]\s*\S+',
        r'secret[=:]\s*\S+',
        r'token[=:]\s*\S+',
        r'/home/\w+/',
        r'C:\\Users\\\w+\\',
    ]
    
    result = message
    for pattern in sensitive_patterns:
        result = re.sub(pattern, '[REDACTED]', result, flags=re.IGNORECASE)
    
    return result
