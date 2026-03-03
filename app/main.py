"""
Zetevnia AI Araç Kutusu - Ana Uygulama
FastAPI Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import Dict, Any
import uvicorn

from app.config import settings
from app.constants import PAGE_HOME, PAGE_RAKAM_TAHMINI, PAGE_TB_TAHMIN, TEMPLATE_INDEX, TEMPLATE_RAKAM_TAHMINI, TEMPLATE_TB_TAHMIN
from app.logger import logger
from app.middleware import (
    RateLimitMiddleware,
    RequestSizeLimitMiddleware,
    ContentTypeValidationMiddleware,
    BruteForceProtectionMiddleware
)
from app.api import stats_router
from app.api.number_guesser import router as rakam_router
from app.api.tb_predictor import router as tb_router


def create_app() -> FastAPI:
    """Factory pattern ile uygulama oluştur"""
    
    application = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url=None,
        redoc_url=None
    )
    
    _configure_middleware(application)
    _configure_routes(application)
    
    logger.info("Uygulama başlatıldı", version=settings.APP_VERSION)
    
    return application


def _configure_middleware(application: FastAPI) -> None:
    """Middleware'leri yapılandır (sıralama önemli)"""
    
    # CORS
    origins = ["*"] if settings.CORS_ALLOW_ALL else settings.CORS_ORIGINS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Request Size Limit
    application.add_middleware(
        RequestSizeLimitMiddleware,
        max_size_mb=settings.MAX_REQUEST_SIZE_MB
    )
    
    # Content-Type Validation
    application.add_middleware(
        ContentTypeValidationMiddleware,
        required_content_type="application/json"
    )
    
    # Brute Force Protection
    application.add_middleware(
        BruteForceProtectionMiddleware,
        max_failed_attempts=settings.MAX_FAILED_ATTEMPTS,
        ban_duration_minutes=settings.BAN_DURATION_MINUTES
    )
    
    # Rate Limiting
    application.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
        requests_per_hour=settings.RATE_LIMIT_PER_HOUR
    )


def _configure_routes(application: FastAPI) -> None:
    """Router'ları ve statik dosyaları yapılandır"""
    
    # Static dosyalar
    application.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Router'ları ekle
    application.include_router(rakam_router)
    application.include_router(tb_router)
    application.include_router(stats_router)


# Uygulama instance'ı
app = create_app()

# Template engine
templates = Jinja2Templates(directory="templates")


# Sayfa route'ları
@app.get("/", response_class=HTMLResponse)
async def ana_sayfa(request: Request) -> HTMLResponse:
    """Ana sayfa"""
    return templates.TemplateResponse(
        TEMPLATE_INDEX,
        {"request": request, "active_page": PAGE_HOME}
    )


@app.get("/rakam-tahmini", response_class=HTMLResponse)
async def rakam_tahmini_sayfasi(request: Request) -> HTMLResponse:
    """Rakam tahmini modül sayfası"""
    return templates.TemplateResponse(
        TEMPLATE_RAKAM_TAHMINI,
        {"request": request, "active_page": PAGE_RAKAM_TAHMINI}
    )


@app.get("/tb-tahmin", response_class=HTMLResponse)
async def tb_tahmin_sayfasi(request: Request) -> HTMLResponse:
    """TB tahmin modül sayfası"""
    return templates.TemplateResponse(
        TEMPLATE_TB_TAHMIN,
        {"request": request, "active_page": PAGE_TB_TAHMIN}
    )


def run_server(use_ssl: bool = False) -> None:
    """Sunucuyu başlat"""
    import sys
    import os
    
    config: Dict[str, Any] = {
        "app": "app.main:app",
        "host": settings.HOST,
        "port": settings.SSL_PORT if use_ssl else settings.PORT,
        "reload": settings.DEBUG
    }
    
    if use_ssl:
        key_file, cert_file = settings.get_ssl_paths()
        
        if os.path.exists(key_file) and os.path.exists(cert_file):
            config["ssl_keyfile"] = key_file
            config["ssl_certfile"] = cert_file
            logger.info(f"HTTPS modu aktif", port=config['port'])
            print(f"🔒 HTTPS modu aktif - https://localhost:{config['port']}")
        else:
            logger.error("SSL sertifikaları bulunamadı")
            print("⚠️  SSL sertifikaları bulunamadı!")
            print("   Önce çalıştırın: python scripts/generate_cert.py")
            sys.exit(1)
    else:
        logger.info(f"HTTP modu aktif", port=config['port'])
        print(f"🌐 HTTP modu - http://localhost:{config['port']}")
        print("   HTTPS için: python -m app.main --ssl")
    
    uvicorn.run(**config)


if __name__ == "__main__":
    import sys
    use_ssl = "--ssl" in sys.argv
    run_server(use_ssl)
