"""
Tüberküloz Tahmin API Router
Röntgen tabanlı TB tahmin endpoint'leri
"""
import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any, List

from app.stats import stats_service
from app.constants import SUPPORTED_XRAY_EXTENSIONS, MAX_XRAY_FILE_SIZE_MB
from app.logger import logger
from app.utils import sanitize_error_message
from app.services.tb_predictor import predict_tb, get_available_models


router = APIRouter(
    prefix="/api/tb",
    tags=["Tüberküloz Tahmin Modülü"]
)


ENDPOINT_PREDICT = "/api/tb/predict"


@router.get("/models")
async def model_listele() -> List[Dict[str, Any]]:
    """
    Kullanılabilir TB modellerini listele
    
    Returns:
        Mevcut modellerin listesi
    """
    return get_available_models()


@router.post("/predict")
async def tahmin_yap(
    file: UploadFile = File(..., description="Akciğer röntgen görüntüsü"),
    model_name: str = Form(..., description="Kullanılacak model (ör: densenet121_balanced)")
) -> Dict[str, Any]:
    """
    Röntgen görüntüsünden TB tahmini yap (5-fold ensemble)
    
    Args:
        file: Akciğer röntgen görüntü dosyası (PNG/JPG)
        model_name: Seçilen model grubu
        
    Returns:
        Ensemble tahmin sonucu ve fold detayları
    """
    try:
        # Dosya uzantısı kontrolü
        _, ext = os.path.splitext(file.filename or "")
        if ext.lower() not in SUPPORTED_XRAY_EXTENSIONS:
            raise ValueError(
                f"Desteklenmeyen dosya formatı: {ext}. "
                f"Desteklenen: {', '.join(SUPPORTED_XRAY_EXTENSIONS)}"
            )
        
        # Dosya boyutu kontrolü
        contents = await file.read()
        file_size_mb = len(contents) / (1024 * 1024)
        
        if file_size_mb > MAX_XRAY_FILE_SIZE_MB:
            raise ValueError(
                f"Dosya boyutu çok büyük: {file_size_mb:.1f}MB. "
                f"Maksimum: {MAX_XRAY_FILE_SIZE_MB}MB"
            )
        
        if len(contents) < 100:
            raise ValueError("Dosya çok küçük veya boş")
        
        # Tahmin yap
        sonuc = predict_tb(contents, model_name)
        
        # İstatistik kaydet
        stats_service.record_api_call(ENDPOINT_PREDICT, success=True)
        stats_service.record_prediction(
            module="tb_tahmin",
            prediction=sonuc["tahmin"],
            confidence=sonuc["guven"],
            success=True
        )
        
        logger.info(
            "TB tahmini başarılı",
            model=model_name,
            prediction=sonuc["tahmin"],
            confidence=sonuc["guven"]
        )
        
        return sonuc
        
    except ValueError as e:
        stats_service.record_api_call(ENDPOINT_PREDICT, success=False)
        logger.warning("TB doğrulama hatası", error=str(e))
        raise HTTPException(status_code=422, detail=str(e))
    
    except FileNotFoundError as e:
        stats_service.record_api_call(ENDPOINT_PREDICT, success=False)
        logger.error("TB model dosyası bulunamadı", error=str(e))
        raise HTTPException(
            status_code=503,
            detail="Model dosyaları bulunamadı. Lütfen yöneticiyle iletişime geçin."
        )
        
    except Exception as e:
        stats_service.record_api_call(ENDPOINT_PREDICT, success=False)
        safe_error = sanitize_error_message(str(e))
        logger.error("TB işleme hatası", error=safe_error)
        raise HTTPException(
            status_code=400,
            detail=f"Görüntü işlenirken bir hata oluştu: {safe_error}"
        )
