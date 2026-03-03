"""
Pytest fixtures ve konfigürasyonu
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Test client fixture"""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def sample_image_data():
    """Örnek base64 görüntü verisi"""
    import base64
    import io
    from PIL import Image
    
    img = Image.new('RGB', (100, 100), color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    base64_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{base64_str}"


@pytest.fixture
def invalid_image_data():
    """Geçersiz görüntü verisi örnekleri"""
    return {
        "empty": "",
        "no_prefix": "SGVsbG8gV29ybGQ=",
        "invalid_base64": "data:image/png;base64,!!!invalid!!!",
        "wrong_format": "data:image/gif;base64,SGVsbG8=",
    }
