"""
Self-Signed SSL Sertifikası Oluşturma Scripti
Kullanım: python certs/generate_cert.py
"""
import subprocess
import os
import sys

def generate_self_signed_cert():
    """OpenSSL kullanarak self-signed sertifika oluşturur"""
    
    cert_dir = os.path.dirname(os.path.abspath(__file__))
    key_file = os.path.join(cert_dir, "key.pem")
    cert_file = os.path.join(cert_dir, "cert.pem")
    
    # Eğer zaten varsa sor
    if os.path.exists(key_file) or os.path.exists(cert_file):
        response = input("Sertifika dosyaları zaten mevcut. Üzerine yazılsın mı? (e/h): ")
        if response.lower() != 'e':
            print("İşlem iptal edildi.")
            return
    
    print("Self-signed SSL sertifikası oluşturuluyor...")
    
    # OpenSSL komutu
    cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:4096",
        "-keyout", key_file,
        "-out", cert_file,
        "-days", "365",
        "-nodes",
        "-subj", "/CN=localhost/O=Zetevnia/C=TR"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n✓ Sertifika başarıyla oluşturuldu!")
        print(f"  Key: {key_file}")
        print(f"  Cert: {cert_file}")
        print(f"\nSunucuyu HTTPS ile başlatmak için:")
        print(f"  python -m core.main --ssl")
    except FileNotFoundError:
        print("\n✗ Hata: OpenSSL bulunamadı!")
        print("  Windows için: https://slproweb.com/products/Win32OpenSSL.html")
        print("  veya: choco install openssl")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Sertifika oluşturma hatası: {e}")

if __name__ == "__main__":
    generate_self_signed_cert()
