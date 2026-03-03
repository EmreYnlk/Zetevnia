"""
Utility Fonksiyon Testleri
"""
import pytest
from app.utils import (
    validate_base64_image,
    format_uptime,
    sanitize_error_message
)


class TestValidateBase64Image:
    """Base64 doğrulama testleri"""
    
    def test_empty_data_fails(self):
        """Boş veri başarısız olmalı"""
        is_valid, error = validate_base64_image("")
        assert is_valid is False
        assert "boş" in error.lower()
    
    def test_no_prefix_fails(self):
        """Prefix olmadan başarısız olmalı"""
        is_valid, error = validate_base64_image("SGVsbG8=")
        assert is_valid is False
        assert "data:image/" in error
    
    def test_invalid_format_fails(self):
        """Desteklenmeyen format başarısız olmalı"""
        is_valid, error = validate_base64_image("data:image/gif;base64,SGVsbG8=")
        assert is_valid is False
        assert "Desteklenmeyen" in error


class TestFormatUptime:
    """Uptime formatlama testleri"""
    
    def test_seconds_only(self):
        """Sadece saniye formatlanmalı"""
        result = format_uptime(45)
        assert "45sn" in result
    
    def test_minutes_and_seconds(self):
        """Dakika ve saniye formatlanmalı"""
        result = format_uptime(125)
        assert "2d" in result
        assert "5sn" in result
    
    def test_hours(self):
        """Saat formatlanmalı"""
        result = format_uptime(3665)
        assert "1s" in result


class TestSanitizeErrorMessage:
    """Hata mesajı temizleme testleri"""
    
    def test_removes_password(self):
        """Password gizlenmeli"""
        result = sanitize_error_message("Error: password=secret123")
        assert "secret123" not in result
        assert "[REDACTED]" in result
    
    def test_removes_api_key(self):
        """API key gizlenmeli"""
        result = sanitize_error_message("Failed with api_key=abc123")
        assert "abc123" not in result
    
    def test_preserves_normal_text(self):
        """Normal metin korunmalı"""
        result = sanitize_error_message("Connection timeout")
        assert result == "Connection timeout"
