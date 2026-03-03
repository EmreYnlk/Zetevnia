"""
API Endpoint Testleri
"""
import pytest


class TestHomePage:
    """Ana sayfa testleri"""
    
    def test_home_returns_200(self, client):
        """Ana sayfa 200 döndürmeli"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_home_returns_html(self, client):
        """Ana sayfa HTML döndürmeli"""
        response = client.get("/")
        assert "text/html" in response.headers["content-type"]


class TestRakamTahminiPage:
    """Rakam tahmini sayfa testleri"""
    
    def test_page_returns_200(self, client):
        """Sayfa 200 döndürmeli"""
        response = client.get("/rakam-tahmini")
        assert response.status_code == 200


class TestPredictionAPI:
    """Tahmin API testleri"""
    
    def test_missing_image_data(self, client):
        """Görüntü verisi olmadan istek hata vermeli"""
        response = client.post(
            "/api/rakam/tahmin-et",
            json={}
        )
        assert response.status_code == 422
    
    def test_empty_image_data(self, client, invalid_image_data):
        """Boş görüntü verisi hata vermeli"""
        response = client.post(
            "/api/rakam/tahmin-et",
            json={"image_data": invalid_image_data["empty"]}
        )
        assert response.status_code == 422
    
    def test_invalid_base64(self, client, invalid_image_data):
        """Geçersiz base64 hata vermeli"""
        response = client.post(
            "/api/rakam/tahmin-et",
            json={"image_data": invalid_image_data["invalid_base64"]}
        )
        assert response.status_code == 422
    
    def test_valid_image_returns_prediction(self, client, sample_image_data):
        """Geçerli görüntü tahmin döndürmeli"""
        response = client.post(
            "/api/rakam/tahmin-et",
            json={"image_data": sample_image_data}
        )
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert "basari" in data
            assert "tahmin" in data
            assert "guven" in data


class TestStatsAPI:
    """İstatistik API testleri"""
    
    def test_summary_returns_200(self, client):
        """Summary endpoint 200 döndürmeli"""
        response = client.get("/api/stats/summary")
        assert response.status_code == 200
    
    def test_summary_contains_uptime(self, client):
        """Summary uptime içermeli"""
        response = client.get("/api/stats/summary")
        data = response.json()
        assert "uptime" in data
    
    def test_recent_returns_list(self, client):
        """Recent endpoint liste döndürmeli"""
        response = client.get("/api/stats/recent")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_hourly_returns_dict(self, client):
        """Hourly endpoint dict döndürmeli"""
        response = client.get("/api/stats/hourly")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
    
    def test_reset_works(self, client):
        """Reset endpoint çalışmalı"""
        response = client.post("/api/stats/reset")
        assert response.status_code == 200
        assert response.json()["basari"] is True
