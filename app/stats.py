"""
API İstatistik Servisi
Kullanım istatistiklerini toplar ve raporlar
"""
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from app.config import settings
from app.constants import DATETIME_FORMAT, DATE_FORMAT, HOUR_FORMAT


@dataclass
class ModuleStats:
    """Modül bazlı istatistikler"""
    total_predictions: int = 0
    successful_predictions: int = 0
    average_confidence: float = 0.0
    confidence_sum: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_predictions": self.total_predictions,
            "successful_predictions": self.successful_predictions,
            "average_confidence": round(self.average_confidence, 2)
        }


class StatsService:
    """Singleton istatistik servisi"""
    
    _instance: Optional['StatsService'] = None
    
    def __new__(cls) -> 'StatsService':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """İlk değerleri ayarla"""
        self.start_time = datetime.now()
        self.max_recent = settings.MAX_RECENT_PREDICTIONS
        self._reset_counters()
    
    def _reset_counters(self) -> None:
        """Sayaçları sıfırla"""
        self.endpoint_calls: Dict[str, int] = defaultdict(int)
        self.endpoint_errors: Dict[str, int] = defaultdict(int)
        self.hourly_calls: Dict[str, int] = defaultdict(int)
        self.daily_calls: Dict[str, int] = defaultdict(int)
        self.module_stats: Dict[str, ModuleStats] = {
            "rakam_tahmini": ModuleStats()
        }
        self.recent_predictions: List[Dict[str, Any]] = []

    def record_api_call(self, endpoint: str, success: bool = True) -> None:
        """API çağrısını kaydet"""
        self.endpoint_calls[endpoint] += 1
        
        if not success:
            self.endpoint_errors[endpoint] += 1
        
        now = datetime.now()
        self.hourly_calls[now.strftime(HOUR_FORMAT)] += 1
        self.daily_calls[now.strftime(DATE_FORMAT)] += 1

    def record_prediction(
        self, 
        module: str, 
        prediction: str, 
        confidence: float, 
        success: bool = True
    ) -> None:
        """Tahmin sonucunu kaydet"""
        if module not in self.module_stats:
            self.module_stats[module] = ModuleStats()
        
        stats = self.module_stats[module]
        stats.total_predictions += 1
        
        if success:
            stats.successful_predictions += 1
        
        stats.confidence_sum += confidence
        stats.average_confidence = stats.confidence_sum / stats.total_predictions
        
        self._add_recent_prediction(module, prediction, confidence, success)

    def _add_recent_prediction(
        self, 
        module: str, 
        prediction: str, 
        confidence: float, 
        success: bool
    ) -> None:
        """Son tahminler listesine ekle"""
        self.recent_predictions.append({
            "module": module,
            "prediction": prediction,
            "confidence": confidence,
            "timestamp": datetime.now().strftime(DATETIME_FORMAT),
            "success": success
        })
        
        if len(self.recent_predictions) > self.max_recent:
            self.recent_predictions = self.recent_predictions[-self.max_recent:]

    def get_uptime(self) -> Dict[str, Any]:
        """Sunucu çalışma süresini döndür"""
        uptime = datetime.now() - self.start_time
        total_seconds = int(uptime.total_seconds())
        
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "total_seconds": total_seconds,
            "formatted": f"{days}g {hours}s {minutes}d {seconds}sn"
        }

    def get_summary(self) -> Dict[str, Any]:
        """Genel istatistik özeti"""
        total_calls = sum(self.endpoint_calls.values())
        total_errors = sum(self.endpoint_errors.values())
        error_rate = (total_errors / total_calls * 100) if total_calls > 0 else 0
        
        return {
            "uptime": self.get_uptime(),
            "total_api_calls": total_calls,
            "total_errors": total_errors,
            "error_rate": round(error_rate, 2),
            "endpoints": dict(self.endpoint_calls),
            "modules": {k: v.to_dict() for k, v in self.module_stats.items()},
            "today_calls": self.daily_calls.get(datetime.now().strftime(DATE_FORMAT), 0)
        }

    def reset(self) -> None:
        """Tüm istatistikleri sıfırla (uptime hariç)"""
        self._reset_counters()

    def get_recent_predictions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Son tahminleri döndür"""
        return self.recent_predictions[-limit:][::-1]

    def get_hourly_stats(self, hours: int = 24) -> Dict[str, int]:
        """Son N saatin istatistiklerini döndür"""
        now = datetime.now()
        result = {}
        
        for i in range(hours):
            hour = now - timedelta(hours=i)
            key = hour.strftime(HOUR_FORMAT)
            display_key = hour.strftime("%H:00")
            result[display_key] = self.hourly_calls.get(key, 0)
        
        return dict(reversed(list(result.items())))


# Singleton instance
stats_service = StatsService()
