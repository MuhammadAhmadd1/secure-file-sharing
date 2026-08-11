import os
import uuid
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="Secure E2EE File Sharing Portal")

# Create local directory to emulate cloud S3 bucket
STORAGE_DIR = "./s3_bucket"
os.makedirs(STORAGE_DIR, exist_ok=True)

class FileRequest(BaseModel):
    filename: str

@app.get("/")
def read_root():
    return {"status": "online", "system": "Secure E2EE File Sharing Portal"}

@app.post("/api/v1/upload-url")
def generate_upload_url(payload: FileRequest, request: Request):
    # Generates local pre-signed upload URL
    base_url = str(request.base_url).rstrip("/")
    token = uuid.uuid4().hex[:16]
    presigned_url = f"{base_url}/mock-s3/upload/{payload.filename}?token={token}"
    return {"upload_url": presigned_url, "file_key": f"encrypted/{payload.filename}"}

@app.post("/api/v1/download-url")
def generate_download_url(payload: FileRequest, request: Request):
    # Generates local pre-signed download URL
    base_url = str(request.base_url).rstrip("/")
    token = uuid.uuid4().hex[:16]
    presigned_url = f"{base_url}/mock-s3/download/{payload.filename}?token={token}"
    return {"download_url": presigned_url}

# --- Mock Cloud Storage Operations (Simulating S3 PUT/GET) ---

@app.put("/mock-s3/upload/{filename}")
async def mock_s3_upload(filename: str, request: Request):
    data = await request.body()
    file_path = os.path.join(STORAGE_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(data)
    return Response(status_code=200)

@app.get("/mock-s3/download/{filename}")
async def mock_s3_download(filename: str):
    file_path = os.path.join(STORAGE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found in S3 bucket")
    return FileResponse(file_path, media_type="application/octet-stream")