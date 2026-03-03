"""
Rakam Tahmini API Router
Çizim tabanlı sayı tanıma endpoint'leri
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator, Field
from typing import Dict, Any

from app.stats import stats_service
from app.constants import MAX_IMAGE_DATA_LENGTH, SUPPORTED_IMAGE_FORMATS, MIN_IMAGE_BYTES
from app.logger import logger
from app.utils import validate_base64_image, sanitize_error_message
from app.services.number_guesser import resmi_isle_ve_tahmin_et


router = APIRouter(
    prefix="/api/rakam",
    tags=["Rakam Tahmini Modülü"]
)


class CizimIstegi(BaseModel):
    """Çizim tahmin isteği"""
    image_data: str = Field(
        ..., 
        max_length=MAX_IMAGE_DATA_LENGTH,
        description="Base64 encoded görüntü verisi"
    )
    
    @field_validator('image_data')
    @classmethod
    def validate_image_data(cls, v: str) -> str:
        """Görüntü verisini doğrula"""
        is_valid, error_message = validate_base64_image(v)
        if not is_valid:
            raise ValueError(error_message)
        return v


class TahminSonucu(BaseModel):
    """Tahmin sonuç modeli"""
    basari: bool
    tahmin: str
    guven: float


ENDPOINT = "/api/rakam/tahmin-et"


@router.post("/tahmin-et", response_model=TahminSonucu)
async def tahmin_yap(istek: CizimIstegi) -> Dict[str, Any]:
    """
    Çizim verisi alır ve rakam tahmini yapar
    
    Args:
        istek: Base64 encoded görüntü verisi içeren istek
        
    Returns:
        Tahmin sonucu ve güven skoru
        
    Raises:
        HTTPException: Doğrulama veya işleme hatası durumunda
    """
    try:
        sonuc = resmi_isle_ve_tahmin_et(istek.image_data)
        
        stats_service.record_api_call(ENDPOINT, success=True)
        stats_service.record_prediction(
            module="rakam_tahmini",
            prediction=sonuc["tahmin"],
            confidence=sonuc["guven"],
            success=True
        )
        
        logger.info(
            "Tahmin başarılı",
            prediction=sonuc["tahmin"],
            confidence=sonuc["guven"]
        )
        
        return {
            "basari": True, 
            "tahmin": sonuc["tahmin"],
            "guven": sonuc["guven"]
        }
        
    except ValueError as e:
        stats_service.record_api_call(ENDPOINT, success=False)
        logger.warning("Doğrulama hatası", error=str(e))
        raise HTTPException(status_code=422, detail=str(e))
        
    except Exception as e:
        stats_service.record_api_call(ENDPOINT, success=False)
        safe_error = sanitize_error_message(str(e))
        logger.error("İşleme hatası", error=safe_error)
        raise HTTPException(
            status_code=400, 
            detail=f"Görüntü işlenirken bir hata oluştu: {safe_error}"
        )
