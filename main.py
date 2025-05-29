# Path: social-support-ai/app/main.py

from fastapi import FastAPI, HTTPException,  UploadFile, File
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
import shutil
import json
import os
from typing import List
from agents.orchestrator import run_pipeline 
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder




app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR_PDF = Path("uploads/pdfs")
UPLOAD_DIR_JPG = Path("uploads/jpgs")

# Ensure directories exist
os.makedirs(UPLOAD_DIR_PDF, exist_ok=True)
os.makedirs(UPLOAD_DIR_JPG, exist_ok=True)

@app.post("/upload")
async def upload_bank_statement(files: List[UploadFile] = File(...)):
    print("Received files for upload:", files)

    if not files:
        raise HTTPException(status_code=400, detail="No files provided for upload.")
    saved_files = []

    for file in files:
        filename = file.filename.lower()
        print(f"Received file: {filename}")
        file_ext = Path(filename).suffix
        print(f"File extension detected: {file_ext}")

        if file_ext not in [".pdf", ".jpg", ".jpeg"]:
            raise HTTPException(status_code=400, detail="Only PDF and JPG files are allowed.")

        if file_ext == ".pdf":
            file_path = Path(UPLOAD_DIR_PDF)/filename
            print(f"Saving PDF file to: {file_path}")
        elif file_ext in [".jpg", ".jpeg"]:
            file_path = Path(UPLOAD_DIR_JPG)/filename
            print(f"Saving JPG file to: {file_path}")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        saved_files.append(filename)
    try:
        result = run_pipeline(file_path)
        print("Pipeline result:", result)
        result_jsonable = jsonable_encoder(result)
        print("JSON-encoded result:", result_jsonable)
        return JSONResponse(content={"status": "success", "result": result_jsonable})
    except Exception as e:
        return {"status": "error", "message": str(e)}



    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
