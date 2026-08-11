import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

API_BASE = "http://127.0.0.1:8000/api/v1"

def download_and_decrypt(filename: str, secret_key_hex: str, output_path: str):
    # 1. Get Pre-signed Download URL
    res = requests.post(f"{API_BASE}/download-url", json={"filename": filename})
    if res.status_code != 200:
        print(f"[-] Failed to get download URL: {res.text}")
        return

    download_url = res.json()["download_url"]

    # 2. Fetch encrypted binary payload
    file_res = requests.get(download_url)
    encrypted_payload = file_res.content

    # 3. Extract Nonce (first 12 bytes) and Decrypt locally
    nonce = encrypted_payload[:12]
    ciphertext = encrypted_payload[12:]
    
    key = bytes.fromhex(secret_key_hex)
    aesgcm = AESGCM(key)
    
    decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)

    # 4. Write original file back to disk
    with open(output_path, "wb") as f:
        f.write(decrypted_data)
        
    print(f"[+] File successfully downloaded and decrypted to: {output_path}")

if __name__ == "__main__":
    key_input = input("Enter AES Key Hex: ").strip()
    download_and_decrypt("sample_report.pdf", key_input, "restored_report.pdf")