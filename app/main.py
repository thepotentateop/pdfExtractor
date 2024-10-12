from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Dict
import logging
import os
import paramiko

from config import Settings
from auth import hash_password, verify_password, create_access_token, get_current_user
from pdf_extraction_helper import PDFExtractor

app = FastAPI()

# Load configuration
settings = Settings()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SFTP client
sftp_client = paramiko.SSHClient()
sftp_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
sftp_client.connect(hostname=settings.SFTP_HOST, username=settings.SFTP_USERNAME, password=settings.SFTP_PASSWORD)

# File storage
file_store = {}

class ExtractionRequest(BaseModel):
    file_id: str
    keywords: List[str]
    prompt: str

class FileUpload(BaseModel):
    base64_string: str

class User(BaseModel):
    username: str

class UserInDB(User):
    password: str

# Fake user database
fake_users_db = {
    "TSPABAP": {
        "username": "TSP ABAPers",
        "password": hash_password("Welcome@321")
    }
}

# Rate limiter
rate_limit_data: Dict[str, list] = {}
RATE_LIMIT = 100
TIME_WINDOW = 60  # seconds

def rate_limiter(request):
    client_ip = request.client.host
    now = int(datetime.now().timestamp())

    # Cleanup old requests
    rate_limit_data[client_ip] = [timestamp for timestamp in rate_limit_data[client_ip] if now - timestamp < TIME_WINDOW]

    if len(rate_limit_data[client_ip]) >= RATE_LIMIT:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")

    # Record the current request
    rate_limit_data[client_ip].append(now)

@app.middleware("http")
async def add_rate_limit(request, call_next):
    try:
        rate_limiter(request)
        response = await call_next(request)
    except HTTPException as e:
        response = JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    return response

@app.post("/token", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"]}

@app.post("/upload")
async def upload_file(file_upload: FileUpload):
    try:
        file_id = str(uuid.uuid4())
        sftp_client.open(f"{settings.SFTP_REMOTE_DIR}/{file_id}.pdf", "wb").write(base64.b64decode(file_upload.base64_string))
        file_store[file_id] = f"{settings.SFTP_REMOTE_DIR}/{file_id}.pdf"
        return JSONResponse(content={"file_id": file_id, "file_path": file_store[file_id]}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/extract-header")
async def extract_header(request: ExtractionRequest):
    try:
        if request.file_id not in file_store:
            raise HTTPException(status_code=404, detail="File not found")

        pdf_extractor = PDFExtractor()
        content = pdf_extractor.extract_header_from_pdf(request.keywords, request.prompt, file_store[request.file_id])

        return JSONResponse(content={"header_info": content}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/extract-items")
async def extract_items(request: ExtractionRequest):
    try:
        if request.file_id not in file_store:
            raise HTTPException(status_code=404, detail="File not found")

        pdf_extractor = PDFExtractor()
        content = pdf_extractor.extract_item_from_pdf(request.keywords, request.prompt, file_store[request.file_id])

        return JSONResponse(content={"item_info": content}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
