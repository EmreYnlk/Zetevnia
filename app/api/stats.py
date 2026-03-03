"""
İstatistik API Router'ı
Kullanım istatistikleri için endpoint'ler
"""
from fastapi import APIRouter, Query
from typing import List, Dict, Any
from app.stats import stats_service

router = APIRouter(
    prefix="/api/stats",
    tags=["İstatistikler"]
)


@router.get("/summary", response_model=Dict[str, Any])
async def get_stats_summary() -> Dict[str, Any]:
    """
    Genel istatistik özeti
    
    Returns:
        Uptime, toplam çağrı sayısı, hata oranı ve modül istatistikleri
    """
    return stats_service.get_summary()


@router.get("/recent", response_model=List[Dict[str, Any]])
async def get_recent_predictions(
    limit: int = Query(default=10, ge=1, le=100, description="Döndürülecek tahmin sayısı")
) -> List[Dict[str, Any]]:
    """
    Son yapılan tahminleri döndür
    
    Args:
        limit: Maksimum döndürülecek kayıt sayısı (1-100)
    
    Returns:
        Son tahminlerin listesi
    """
    return stats_service.get_recent_predictions(limit)


@router.get("/hourly", response_model=Dict[str, int])
async def get_hourly_stats(
    hours: int = Query(default=24, ge=1, le=168, description="Son kaç saatin istatistiği")
) -> Dict[str, int]:
    """
    Saatlik API çağrı istatistiklerini döndür
    
    Args:
        hours: Geriye dönük saat sayısı (1-168)
    
    Returns:
        Saat bazlı çağrı sayıları
    """
    return stats_service.get_hourly_stats(hours)


@router.post("/reset")
async def reset_stats() -> Dict[str, Any]:
    """
    Tüm istatistikleri sıfırla (uptime hariç)
    
    Returns:
        Başarı mesajı
    """
    stats_service.reset()
    return {"basari": True, "mesaj": "İstatistikler sıfırlandı"}
