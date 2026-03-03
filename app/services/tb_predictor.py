"""
Tüberküloz Tahmin Servisi
DenseNet121/201 tabanlı 5-fold ensemble tahmin
"""
import os
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models
from typing import Dict, Any, List, Optional, Tuple

from app.config import settings
from app.constants import TB_IMAGE_SIZE
from app.logger import logger


# ─── Model Tanımları ───

TB_MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "densenet121_balanced": {
        "name": "DenseNet-121 (Balanced)",
        "description": "DenseNet-121 mimarisi, dengeli veri seti ile eğitilmiş",
        "architecture": "densenet121",
        "folder": "densenet121_balanced",
        "num_folds": 5,
    },
    "densenet121_unbalanced": {
        "name": "DenseNet-121 (Unbalanced)",
        "description": "DenseNet-121 mimarisi, dengesiz veri seti ile eğitilmiş",
        "architecture": "densenet121",
        "folder": "densenet121_unbalanced",
        "num_folds": 5,
    },
    "densenet201_balanced": {
        "name": "DenseNet-201 (Balanced)",
        "description": "DenseNet-201 mimarisi, dengeli veri seti ile eğitilmiş",
        "architecture": "densenet201",
        "folder": "densenet201_balanced",
        "num_folds": 5,
    },
    "densenet201_unbalanced": {
        "name": "DenseNet-201 (Unbalanced)",
        "description": "DenseNet-201 mimarisi, dengesiz veri seti ile eğitilmiş",
        "architecture": "densenet201",
        "folder": "densenet201_unbalanced",
        "num_folds": 5,
    },
}

# Sınıf etiketleri
TB_CLASSES = ["Normal", "Tüberküloz"]

# Model cache (lazy loading)
_model_cache: Dict[str, List[nn.Module]] = {}


# ─── Cihaz Seçimi ───

def _get_device() -> torch.device:
    """Kullanılacak cihazı belirle"""
    if settings.USE_GPU and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


device = _get_device()


# ─── Model Oluşturma ───

def _create_densenet(architecture: str) -> nn.Module:
    """DenseNet modeli oluştur (eğitilmiş ağırlıklar yüklenecek)"""
    if architecture == "densenet121":
        model = models.densenet121(weights=None)
    elif architecture == "densenet201":
        model = models.densenet201(weights=None)
    else:
        raise ValueError(f"Desteklenmeyen mimari: {architecture}")
    
    # Kullanıcının eğitim mimarisine uygun Sequential classifier
    # Linear(features→512) → ReLU → Dropout → Linear(512→1)
    num_features = model.classifier.in_features
    model.classifier = nn.Sequential(
        nn.Linear(num_features, 512),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(512, 1)
    )
    
    return model


# ─── Model Yükleme ───

def _get_model_folder(model_key: str) -> str:
    """Model klasör yolunu döndür"""
    info = TB_MODEL_REGISTRY[model_key]
    return os.path.join(settings.TB_MODELS_DIR, info["folder"])


def _load_fold_models(model_key: str) -> List[nn.Module]:
    """Bir model grubunun 5 fold modelini yükle"""
    if model_key in _model_cache:
        return _model_cache[model_key]
    
    info = TB_MODEL_REGISTRY[model_key]
    folder = _get_model_folder(model_key)
    loaded_models: List[nn.Module] = []
    
    for fold_idx in range(1, info["num_folds"] + 1):
        model_path = os.path.join(folder, f"fold{fold_idx}.pth")
        
        if not os.path.exists(model_path):
            logger.error(
                "TB model dosyası bulunamadı",
                model=model_key,
                fold=fold_idx,
                path=model_path
            )
            raise FileNotFoundError(
                f"Model dosyası bulunamadı: {model_path}"
            )
        
        model = _create_densenet(info["architecture"])
        model.load_state_dict(
            torch.load(model_path, map_location=device, weights_only=True)
        )
        model.to(device)
        model.eval()
        loaded_models.append(model)
        
        logger.info(
            "TB fold modeli yüklendi",
            model=model_key,
            fold=fold_idx,
            device=str(device)
        )
    
    _model_cache[model_key] = loaded_models
    logger.info(
        "TB model grubu yüklendi",
        model=model_key, 
        total_folds=len(loaded_models)
    )
    
    return loaded_models


# ─── Görüntü İşleme ───

def _preprocess_xray(image_bytes: bytes) -> torch.Tensor:
    """
    Röntgen görüntüsünü model için hazırla
    - Decode → Resize 224x224 → RGB → Normalize → Tensor
    """
    # Bytes → numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Görüntü dosyası okunamadı veya bozuk")
    
    # BGR → RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Resize
    img = cv2.resize(img, (TB_IMAGE_SIZE, TB_IMAGE_SIZE), interpolation=cv2.INTER_AREA)
    
    # Normalize [0, 1] → ImageNet normalization
    img = img.astype(np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    img = (img - mean) / std
    
    # HWC → CHW → batch dimension
    img = np.transpose(img, (2, 0, 1))
    tensor = torch.tensor(img, dtype=torch.float32).unsqueeze(0)
    
    return tensor.to(device)


# ─── Ensemble Tahmin ───

def _predict_single_model(
    model: nn.Module, 
    tensor: torch.Tensor
) -> Tuple[int, float, float]:
    """Tek bir modelden tahmin al (sigmoid binary output)"""
    with torch.no_grad():
        output = model(tensor)
        # Sigmoid: 1 çıkış → TB olasılığı
        tb_prob = torch.sigmoid(output).item()
        normal_prob = 1.0 - tb_prob
        
        # 0 = Normal, 1 = TB
        predicted_class = 1 if tb_prob >= 0.5 else 0
        confidence = tb_prob if predicted_class == 1 else normal_prob
        
        return predicted_class, confidence * 100, tb_prob


def predict_tb(image_bytes: bytes, model_key: str) -> Dict[str, Any]:
    """
    Ensemble TB tahmini yap
    
    Args:
        image_bytes: Röntgen görüntüsünün byte verisi
        model_key: Seçilen model grubu (ör: "densenet121_balanced")
        
    Returns:
        {
            "basari": True,
            "tahmin": "Normal" | "Tüberküloz",
            "guven": float (0-100),
            "model_name": str,
            "fold_detaylari": [...]
        }
    """
    if model_key not in TB_MODEL_REGISTRY:
        raise ValueError(f"Geçersiz model: {model_key}")
    
    # Modelleri yükle (cache'den veya diskten)
    fold_models = _load_fold_models(model_key)
    
    # Görüntüyü hazırla
    tensor = _preprocess_xray(image_bytes)
    
    # Her fold'dan tahmin al
    all_tb_probs: List[float] = []
    fold_details: List[Dict[str, Any]] = []
    
    for fold_idx, model in enumerate(fold_models, 1):
        predicted_class, confidence, tb_prob = _predict_single_model(model, tensor)
        
        all_tb_probs.append(tb_prob)
        fold_details.append({
            "fold": fold_idx,
            "tahmin": TB_CLASSES[predicted_class],
            "guven": round(confidence, 1),
            "olasiliklar": {
                "Normal": round((1.0 - tb_prob) * 100, 1),
                "Tüberküloz": round(tb_prob * 100, 1)
            }
        })
    
    # Ensemble: TB olasılıklarının ortalaması
    avg_tb_prob = float(np.mean(all_tb_probs))
    final_class = 1 if avg_tb_prob >= 0.5 else 0
    final_confidence = avg_tb_prob if final_class == 1 else (1.0 - avg_tb_prob)
    
    return {
        "basari": True,
        "tahmin": TB_CLASSES[final_class],
        "guven": round(final_confidence * 100, 1),
        "model_name": TB_MODEL_REGISTRY[model_key]["name"],
        "fold_detaylari": fold_details
    }


# ─── API Yardımcıları ───

def get_available_models() -> List[Dict[str, str]]:
    """Kullanılabilir TB modellerini listele"""
    result = []
    for key, info in TB_MODEL_REGISTRY.items():
        folder = _get_model_folder(key)
        available = os.path.isdir(folder)
        
        result.append({
            "key": key,
            "name": info["name"],
            "description": info["description"],
            "architecture": info["architecture"],
            "num_folds": info["num_folds"],
            "available": available
        })
    
    return result
