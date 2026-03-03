"""
Security Middleware Collection
- Rate Limiting
- Request Size Limit
- Content-Type Validation
- Brute Force Protection
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from app.utils import get_client_ip
from app.logger import logger


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """İstek boyutunu sınırlar (DoS koruması)"""
    
    def __init__(self, app, max_size_mb: float = 5.0):
        super().__init__(app)
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)
        self.max_size_mb = max_size_mb

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        
        if content_length and int(content_length) > self.max_size_bytes:
            client_ip = get_client_ip(request)
            logger.security(
                "Büyük istek engellendi",
                ip=client_ip,
                size_mb=round(int(content_length) / (1024*1024), 2)
            )
            return JSONResponse(
                status_code=413,
                content={
                    "detail": f"İstek boyutu çok büyük. Maksimum: {self.max_size_mb}MB",
                    "max_size_mb": self.max_size_mb
                }
            )
        
        return await call_next(request)


class ContentTypeValidationMiddleware(BaseHTTPMiddleware):
    """POST/PUT isteklerinde Content-Type kontrolü"""
    
    METHODS_TO_CHECK = {"POST", "PUT", "PATCH"}
    
    # Bu path'ler multipart/form-data kabul eder (dosya yükleme)
    MULTIPART_PATHS = {"/api/tb/predict"}
    
    def __init__(self, app, required_content_type: str = "application/json"):
        super().__init__(app)
        self.required_content_type = required_content_type

    async def dispatch(self, request: Request, call_next):
        if request.method in self.METHODS_TO_CHECK:
            path = request.url.path
            
            if path.startswith("/api"):
                content_type = request.headers.get("content-type", "")
                
                # Multipart path'ler için multipart/form-data kabul et
                if path in self.MULTIPART_PATHS:
                    if not (content_type.startswith(self.required_content_type) or 
                            content_type.startswith("multipart/form-data")):
                        client_ip = get_client_ip(request)
                        logger.security(
                            "Geçersiz Content-Type",
                            ip=client_ip,
                            received=content_type or "None"
                        )
                        return JSONResponse(
                            status_code=415,
                            content={
                                "detail": f"Geçersiz Content-Type. Beklenen: {self.required_content_type} veya multipart/form-data",
                                "received": content_type or "Belirtilmemiş"
                            }
                        )
                elif not content_type.startswith(self.required_content_type):
                    client_ip = get_client_ip(request)
                    logger.security(
                        "Geçersiz Content-Type",
                        ip=client_ip,
                        received=content_type or "None"
                    )
                    return JSONResponse(
                        status_code=415,
                        content={
                            "detail": f"Geçersiz Content-Type. Beklenen: {self.required_content_type}",
                            "received": content_type or "Belirtilmemiş"
                        }
                    )
        
        return await call_next(request)


class BruteForceProtectionMiddleware(BaseHTTPMiddleware):
    """Brute force saldırılarına karşı koruma"""
    
    def __init__(
        self, 
        app, 
        max_failed_attempts: int = 10,
        ban_duration_minutes: int = 5
    ):
        super().__init__(app)
        self.max_failed_attempts = max_failed_attempts
        self.ban_duration = timedelta(minutes=ban_duration_minutes)
        self.failed_attempts: Dict[str, List[datetime]] = defaultdict(list)
        self.banned_ips: Dict[str, datetime] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = get_client_ip(request)
        now = datetime.now()
        
        ban_response = self._check_ban(client_ip, now)
        if ban_response:
            return ban_response
        
        response = await call_next(request)
        
        if request.url.path.startswith("/api"):
            self._process_response(client_ip, response.status_code, now)
        
        return response

    def _check_ban(self, client_ip: str, now: datetime) -> Optional[JSONResponse]:
        """IP'nin ban durumunu kontrol et"""
        if client_ip not in self.banned_ips:
            return None
            
        ban_expires = self.banned_ips[client_ip]
        
        if now >= ban_expires:
            del self.banned_ips[client_ip]
            self.failed_attempts[client_ip] = []
            return None
        
        remaining = int((ban_expires - now).total_seconds())
        return JSONResponse(
            status_code=403,
            content={
                "detail": "IP adresiniz geçici olarak engellendi.",
                "retry_after_seconds": remaining
            },
            headers={"Retry-After": str(remaining)}
        )

    def _process_response(self, client_ip: str, status_code: int, now: datetime) -> None:
        """Response'a göre failed attempts güncelle"""
        if status_code >= 400:
            self._record_failed_attempt(client_ip, now)
            
            recent_failures = self._get_recent_failures(client_ip, now)
            if len(recent_failures) >= self.max_failed_attempts:
                self.banned_ips[client_ip] = now + self.ban_duration
                self.failed_attempts[client_ip] = []
                logger.security("IP engellendi", ip=client_ip, duration_min=self.ban_duration.seconds // 60)
        else:
            if client_ip in self.failed_attempts:
                self.failed_attempts[client_ip] = []

    def _record_failed_attempt(self, client_ip: str, timestamp: datetime) -> None:
        """Başarısız deneme kaydet"""
        self.failed_attempts[client_ip].append(timestamp)

    def _get_recent_failures(self, client_ip: str, now: datetime) -> List[datetime]:
        """Son ban süresi içindeki başarısız denemeleri getir"""
        cutoff = now - self.ban_duration
        self.failed_attempts[client_ip] = [
            t for t in self.failed_attempts[client_ip] if t > cutoff
        ]
        return self.failed_attempts[client_ip]

    def get_ban_status(self, client_ip: str) -> Dict:
        """IP'nin ban durumunu döndür"""
        now = datetime.now()
        if client_ip in self.banned_ips:
            ban_expires = self.banned_ips[client_ip]
            if now < ban_expires:
                return {
                    "banned": True,
                    "expires_in_seconds": int((ban_expires - now).total_seconds())
                }
        return {"banned": False}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """IP bazlı rate limiting"""
    
    DEFAULT_EXCLUDED_PATHS = ["/", "/static", "/favicon.ico"]
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 30,
        requests_per_hour: int = 500,
        excluded_paths: Optional[List[str]] = None
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.excluded_paths = excluded_paths or self.DEFAULT_EXCLUDED_PATHS
        
        self.minute_requests: Dict[str, List[datetime]] = defaultdict(list)
        self.hour_requests: Dict[str, List[datetime]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        if self._should_skip(path):
            return await call_next(request)

        client_ip = get_client_ip(request)
        now = datetime.now()

        self._cleanup_old_requests(client_ip, now)

        rate_limit_response = self._check_limits(client_ip)
        if rate_limit_response:
            logger.security("Rate limit aşıldı", ip=client_ip)
            return rate_limit_response

        self._record_request(client_ip, now)

        response = await call_next(request)
        self._add_rate_limit_headers(response, client_ip)

        return response

    def _should_skip(self, path: str) -> bool:
        """Bu path'i atlamalı mıyız?"""
        if any(path.startswith(excluded) for excluded in self.excluded_paths):
            return True
        return not path.startswith("/api")

    def _check_limits(self, client_ip: str) -> Optional[JSONResponse]:
        """Rate limit kontrolü"""
        minute_count = len(self.minute_requests[client_ip])
        hour_count = len(self.hour_requests[client_ip])

        if minute_count >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Çok fazla istek gönderdiniz. Lütfen 1 dakika bekleyin.",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )

        if hour_count >= self.requests_per_hour:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Saatlik istek limitinize ulaştınız. Lütfen daha sonra tekrar deneyin.",
                    "retry_after": 3600
                },
                headers={"Retry-After": "3600"}
            )

        return None

    def _record_request(self, client_ip: str, now: datetime) -> None:
        """İsteği kaydet"""
        self.minute_requests[client_ip].append(now)
        self.hour_requests[client_ip].append(now)

    def _cleanup_old_requests(self, client_ip: str, now: datetime) -> None:
        """Eski istek kayıtlarını temizle"""
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)

        self.minute_requests[client_ip] = [
            t for t in self.minute_requests[client_ip] if t > minute_ago
        ]
        self.hour_requests[client_ip] = [
            t for t in self.hour_requests[client_ip] if t > hour_ago
        ]

    def _add_rate_limit_headers(self, response, client_ip: str) -> None:
        """Response'a rate limit header'ları ekle"""
        minute_count = len(self.minute_requests[client_ip])
        hour_count = len(self.hour_requests[client_ip])
        
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(max(0, self.requests_per_minute - minute_count))
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(max(0, self.requests_per_hour - hour_count))

    def get_stats_for_ip(self, client_ip: str) -> Dict:
        """Belirli bir IP için rate limit durumunu döndür"""
        now = datetime.now()
        self._cleanup_old_requests(client_ip, now)
        
        return {
            "minute_used": len(self.minute_requests[client_ip]),
            "minute_limit": self.requests_per_minute,
            "hour_used": len(self.hour_requests[client_ip]),
            "hour_limit": self.requests_per_hour
        }
