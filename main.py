from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from uuid import uuid4
import base64
import os
from pdfExtractionHelper import PDFExtractor

app = FastAPI()

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class ExtractionRequest(BaseModel):
    file_id: str
    keywords: List[str]
    prompt: str


class FileUpload(BaseModel):
    base64_string: str


file_store = {}


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
