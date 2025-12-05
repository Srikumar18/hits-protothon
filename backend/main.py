from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import shutil
from extract import process_pdf
from fastapi.staticfiles import StaticFiles
from config import CORS_ORIGINS, PORT, HOST


app = FastAPI(title="PDF Text Extraction API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories if they don't exist
os.makedirs("extracted_images", exist_ok=True)
os.makedirs("uploaded_pdfs", exist_ok=True)

app.mount(
    "/images",
    StaticFiles(directory="extracted_images"),
    name="images"
)

app.mount(
    "/pdfs",
    StaticFiles(directory="uploaded_pdfs"),
    name="pdfs"
)



@app.post("/extract-pdf")
async def extract_pdf_content(file: UploadFile = File(...)):
    print(f"Received file: {file.filename}, content_type: {file.content_type}")
    
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    temp_file_path = None
    mounted_file_path = None
    try:
        # Generate unique filename to avoid conflicts
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        safe_filename = f"{unique_id}_{file.filename}"
        
        # Save uploaded file temporarily for processing
        temp_file_path = f"temp_{safe_filename}"
        mounted_file_path = os.path.join("uploaded_pdfs", safe_filename)
        
        # Read file content once
        file_content = await file.read()
        
        # Save temporary file for processing
        with open(temp_file_path, "wb") as f:
            f.write(file_content)
        
        # Save mounted file for viewing
        with open(mounted_file_path, "wb") as f:
            f.write(file_content)
        
        print(f"Processing PDF: {temp_file_path}")
        
        # Process the PDF
        result = process_pdf(temp_file_path)
        
        # Add PDF URL to the result
        result["pdf_url"] = f"/pdfs/{safe_filename}"
        result["original_filename"] = file.filename
        
        # Clean up temporary file (keep mounted file)
        os.unlink(temp_file_path)
        
        return JSONResponse(content=result)
    
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        # Clean up temporary file if it exists
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass
        # Clean up mounted file on error
        if mounted_file_path and os.path.exists(mounted_file_path):
            try:
                os.unlink(mounted_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.get("/pdf/{filename}")
async def get_pdf(filename: str):
    """Serve PDF files for viewing"""
    file_path = os.path.join("uploaded_pdfs", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(file_path, media_type="application/pdf")

@app.get("/")
async def root():
    return {"message": "PDF Text Extraction API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)