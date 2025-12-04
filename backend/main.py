from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from extract import process_pdf

app = FastAPI(title="PDF Text Extraction API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract-pdf/")
async def extract_pdf_content(file: UploadFile = File(...)):
    print(f"Received file: {file.filename}, content_type: {file.content_type}")
    
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    temp_file_path = None
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        print(f"Processing PDF: {temp_file_path}")
        
        # Process the PDF
        result = process_pdf(temp_file_path)
        
        # Clean up temporary file
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
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.get("/")
async def root():
    return {"message": "PDF Text Extraction API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)