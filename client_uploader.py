import os
import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Generate AES-256 Key locally on client machine
SECRET_KEY = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(SECRET_KEY)
nonce = os.urandom(12)  # Unique 96-bit nonce

API_BASE = "http://127.0.0.1:8000/api/v1"

def encrypt_and_upload(file_path: str):
    filename = os.path.basename(file_path)
    
    # 1. Read raw local file
    with open(file_path, "rb") as f:
        plaintext_data = f.read()

    # 2. Encrypt locally (E2EE)
    encrypted_data = nonce + aesgcm.encrypt(nonce, plaintext_data, None)

    # 3. Request pre-signed URL from API
    res = requests.post(f"{API_BASE}/upload-url", json={"filename": filename})
    if res.status_code != 200:
        print(f"[-] Failed to get upload URL: {res.text}")
        return
        
    upload_url = res.json()["upload_url"]

    # 4. Direct Upload Encrypted Binary to S3 Cloud Storage
    upload_res = requests.put(upload_url, data=encrypted_data)
    
    if upload_res.status_code == 200:
        print(f"[+] File '{filename}' successfully encrypted and uploaded to S3!")
        print(f"[!] SAVE THIS KEY LOCALLY FOR DECRYPTION: {SECRET_KEY.hex()}")
    else:
        print(f"[-] S3 Upload failed with status code: {upload_res.status_code}")

if __name__ == "__main__":
    encrypt_and_upload("sample_report.pdf")