"""
Middleware Testleri
"""
import pytest
from datetime import datetime


class TestContentTypeValidation:
    """Content-Type validation testleri"""
    
    def test_post_without_json_fails(self, client):
        """JSON olmadan POST başarısız olmalı"""
        response = client.post(
            "/api/rakam/tahmin-et",
            content="not json",
            headers={"Content-Type": "text/plain"}
        )
        assert response.status_code == 415
    
    def test_post_with_json_succeeds(self, client):
        """JSON ile POST geçmeli (validation hatası verebilir)"""
        response = client.post(
            "/api/rakam/tahmin-et",
            json={"image_data": ""},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code != 415


class TestRateLimitHeaders:
    """Rate limit header testleri"""
    
    def test_rate_limit_headers_present(self, client):
        """Rate limit header'ları bulunmalı"""
        response = client.get("/api/stats/summary")
        
        assert "X-RateLimit-Limit-Minute" in response.headers
        assert "X-RateLimit-Remaining-Minute" in response.headers
        assert "X-RateLimit-Limit-Hour" in response.headers
        assert "X-RateLimit-Remaining-Hour" in response.headers
