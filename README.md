---

# 📄 JsonifyPDF – Intelligent PDF to JSON System

JsonifyPDF is a full-stack document intelligence system that converts unstructured PDFs into structured, machine-readable JSON. It provides automatic summarization, keyword extraction, document hierarchy generation, and rich visual inspection through a modern web UI.

This project was built to make legacy PDF documents AI-ready by transforming them into clean, hierarchical, and searchable data.

---

## ✨ Features

### 📂 Backend (FastAPI)

* PDF to JSON conversion with rich metadata
* OCR support for scanned PDFs (Tesseract)
* Table extraction
* Image extraction
* Heading hierarchy generation
* Abstractive summarization (Hugging Face)
* Keyword extraction
* ML-powered classification support (XGBoost)

### 🖥️ Frontend (React)

* Interactive PDF Viewer with highlighting
* Clickable document hierarchy tree
* JSON Inspector (live structured view)
* Table and Image viewer
* Summary and keyword display
* Modern, responsive UI

---

## 🏗 Technology Stack

### **Backend**

* Python 3
* FastAPI
* Uvicorn
* PyMuPDF
* pdfplumber
* Camelot (OpenCV)
* Tesseract OCR
* pdf2image
* Hugging Face Hub
* NLTK
* XGBoost
* scikit-learn
* NumPy, Pandas
* Joblib

### **Frontend**

* React (Vite)
* TailwindCSS
* Zustand (state management)
* React-PDF
* React-JSON-View
* Axios
* Framer Motion
* Lucide React

---

## 📁 Repository Structure

```
DocMind/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

## ✅ Prerequisites

Install the following before running the project:

* Python 3.9+
* Node.js 18+
* Git
* Tesseract OCR
* Poppler

---

## 🔧 Backend Setup (FastAPI)

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/DocMind.git
cd DocMind/backend
```

### 2️⃣ Create and activate virtual environment

```bash
python3 -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Create `.env` file

```env
HF_API_TOKEN=your_huggingface_api_token
HF_SUMMARY_MODEL=facebook/bart-large-cnn
POPPLER_PATH=/path/to/poppler/bin
TESSERACT_PATH=/path/to/tesseract
```

### 5️⃣ Run the backend server

```bash
python3 main.py
```

Backend runs at:

```
http://localhost:8000
```

---

## ⚛️ Frontend Setup (React)

### 6️⃣ Navigate to frontend

```bash
cd ../frontend
```

### 7️⃣ Install dependencies

```bash
npm install
```

### 8️⃣ Start the frontend server

```bash
npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

---

## 📦 Backend requirements.txt

Add this in `backend/requirements.txt`:

```txt
fastapi
uvicorn[standard]
python-dotenv
pytesseract
pdf2image
camelot-py[cv]
opencv-python
pillow
PyMuPDF
pdfplumber
python-multipart
xgboost
scikit-learn
numpy
pandas
joblib
fastapi[all]
nltk
requests
huggingface_hub>=0.26.0
```

---

## 🧪 How to Use

1. Start the backend:

   ```bash
   python3 main.py
   ```
2. Start the frontend:

   ```bash
   npm run dev
   ```
3. Open your browser:

   ```
   http://localhost:5173
   ```
4. Upload a PDF and explore:

   * Hierarchy tree
   * JSON output
   * Summary and keywords
   * Page navigation

---

## 🎯 Environment Variables

| Variable         | Description                                     |
| ---------------- | ----------------------------------------------- |
| HF_API_TOKEN     | Hugging Face API key                            |
| HF_SUMMARY_MODEL | Summarization model (`facebook/bart-large-cnn`) |
| POPPLER_PATH     | Path to Poppler binaries                        |
| TESSERACT_PATH   | Path to Tesseract executable                    |

---

## 🏆 Hackathon Note

Built as part of an innovation-focused prototyping effort to modernize PDF document processing and make them AI-ready.

---

## 👤 Author

* **Srikumar V**
* **Sudarshan O**
* **Prawin Kumar S**
* **Yukesh D**

---

## 📌 License

MIT License

---