"""
Rakam Tanıma Servisi
OpenCV görüntü işleme ve PyTorch CNN tahmin
"""
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import base64
from typing import Dict, Any, List, Tuple

from app.config import settings
from app.logger import logger


class RakamTanimaCNN(nn.Module):
    """MNIST üzerinde eğitilmiş CNN modeli"""
    
    def __init__(self):
        super(RakamTanimaCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)
        self.dropout = nn.Dropout(0.25)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 64 * 7 * 7)
        x = self.dropout(F.relu(self.fc1(x)))
        x = self.fc2(x)
        return x


def _get_device() -> torch.device:
    """Kullanılacak cihazı belirle"""
    if settings.USE_GPU and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def _load_model() -> RakamTanimaCNN:
    """Modeli yükle ve hazırla"""
    device = _get_device()
    model = RakamTanimaCNN().to(device)
    
    try:
        model.load_state_dict(
            torch.load(
                settings.MODEL_PATH, 
                map_location=device, 
                weights_only=True
            )
        )
        model.eval()
        logger.info("Model yüklendi", device=str(device), path=settings.MODEL_PATH)
    except Exception as e:
        logger.error("Model yüklenemedi", error=str(e))
        raise
    
    return model


# Model instance (singleton)
device = _get_device()
model = _load_model()


def _decode_base64_image(base64_data: str) -> np.ndarray:
    """Base64 veriyi grayscale görüntüye çevir"""
    encoded_data = base64_data.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)


def _preprocess_image(img: np.ndarray) -> np.ndarray:
    """Görüntüyü MNIST formatına getir (siyah arkaplan, beyaz yazı)"""
    _, threshold_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    return threshold_img


def _find_digit_contours(threshold_img: np.ndarray, min_area: int = 50) -> List:
    """Rakam konturlarını bul ve soldan sağa sırala"""
    contours, _ = cv2.findContours(
        threshold_img, 
        cv2.RETR_EXTERNAL, 
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    valid_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
    return sorted(valid_contours, key=lambda c: cv2.boundingRect(c)[0])


def _extract_digit(
    threshold_img: np.ndarray, 
    contour, 
    padding_ratio: float = 0.2
) -> np.ndarray:
    """Konturdan rakamı kes ve 28x28'e boyutlandır"""
    x, y, w, h = cv2.boundingRect(contour)
    
    padding = int(max(w, h) * padding_ratio)
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(threshold_img.shape[1], x + w + padding)
    y2 = min(threshold_img.shape[0], y + h + padding)
    
    digit_crop = threshold_img[y1:y2, x1:x2]
    return cv2.resize(digit_crop, (28, 28), interpolation=cv2.INTER_AREA)


def _prepare_tensor(digit_28x28: np.ndarray) -> torch.Tensor:
    """28x28 görüntüyü model için tensor'a çevir"""
    normalized = digit_28x28.astype(np.float32) / 255.0
    standardized = (normalized - 0.5) / 0.5
    return torch.tensor(standardized).unsqueeze(0).unsqueeze(0).to(device)


def _predict_digit(tensor: torch.Tensor) -> Tuple[int, float]:
    """Tek bir rakam için tahmin ve güven skoru döndür"""
    with torch.no_grad():
        output = model(tensor)
        probabilities = F.softmax(output, dim=1)
        confidence, predicted = torch.max(probabilities, 1)
        return predicted.item(), confidence.item() * 100


def resmi_isle_ve_tahmin_et(base64_verisi: str) -> Dict[str, Any]:
    """
    Frontend'den gelen base64 resmini işle ve tahmin yap
    
    Args:
        base64_verisi: data:image/... formatında base64 encoded görüntü
        
    Returns:
        {"tahmin": str, "guven": float} formatında sonuç
    """
    img = _decode_base64_image(base64_verisi)
    threshold_img = _preprocess_image(img)
    contours = _find_digit_contours(threshold_img)
    
    if not contours:
        return {"tahmin": "Çizim Algılanamadı", "guven": 0}
    
    predictions: List[str] = []
    confidence_scores: List[float] = []
    
    for contour in contours:
        digit_28x28 = _extract_digit(threshold_img, contour)
        tensor = _prepare_tensor(digit_28x28)
        digit, confidence = _predict_digit(tensor)
        
        predictions.append(str(digit))
        confidence_scores.append(confidence)
    
    result_number = "".join(predictions)
    average_confidence = sum(confidence_scores) / len(confidence_scores)
    
    return {
        "tahmin": result_number, 
        "guven": round(average_confidence, 1)
    }
