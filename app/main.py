from app.auth import hash_password, verify_password, create_access_token, get_current_user, Token, TokenData
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from app.pdfExtractionHelper import PDFExtractor
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from collections import defaultdict
from typing import List
from uuid import uuid4
from typing import Dict
import logging
import base64
import os


app = FastAPI()


# Example user storage
fake_users_db = {
    "TSPABAP": {
        "username": "TSP ABAPers",
        "password": hash_password("Welcome@321")  # In a real app, use hashed passwords
    }
}

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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


# Configure logging
file_store = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

rate_limit_data: Dict[str, list] = defaultdict(list)
RATE_LIMIT = 100
TIME_WINDOW = timedelta(minutes=1)


def rate_limiter(request: Request):
    client_ip = request.client.host
    now = datetime.now()

    # Cleanup old requests
    rate_limit_data[client_ip] = [timestamp for timestamp in rate_limit_data[client_ip] if now - timestamp < TIME_WINDOW]

    if len(rate_limit_data[client_ip]) >= RATE_LIMIT:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")

    # Record the current request
    rate_limit_data[client_ip].append(now)


@app.middleware("http")
async def add_rate_limit(request: Request, call_next):
    try:
        rate_limiter(request)
        response = await call_next(request)
    except HTTPException as e:
        response = JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    return response


@app.post("/token", response_model=Token)
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


# Secured endpoint example
@app.get("/users/me", response_model=User)
async def read_users_me(current_user: TokenData = Depends(get_current_user)):
    return {"username": current_user.username}


@app.post("/upload")
async def upload_file(file_upload: FileUpload):
    try:
        file_id = str(uuid4())
        file_path = os.path.join(UPLOAD_FOLDER, f"{file_id}-converted_pdf.pdf")
        decoded_bytes = base64.b64decode(file_upload.base64_string)

        with open(file_path, 'wb') as output_file:
            output_file.write(decoded_bytes)

        file_store[file_id] = file_path
        return JSONResponse(content={"file_id": file_id, "file_path": file_path}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/extract-header")
async def extract_header(request: ExtractionRequest):
    try:
        if request.file_id not in file_store:
            raise HTTPException(status_code=404, detail="File not found")

        file_path = file_store[request.file_id]
        pdf_extractor = PDFExtractor()
        content = pdf_extractor.extract_header_from_pdf(request.keywords, request.prompt, file_path)

        return JSONResponse(content={"header_info": content}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/extract-items")
async def extract_items(request: ExtractionRequest):
    try:
        if request.file_id not in file_store:
            raise HTTPException(status_code=404, detail="File not found")

        file_path = file_store[request.file_id]
        pdf_extractor = PDFExtractor()
        content = pdf_extractor.extract_item_from_pdf(request.keywords, request.prompt, file_path)

        return JSONResponse(content={"item_info": content}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
