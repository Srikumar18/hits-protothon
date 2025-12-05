import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Backend configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
PORT = int(os.getenv('PORT', 8000))
HOST = os.getenv('HOST', '0.0.0.0')

# CORS origins for production
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://hits-protothon.vercel.app/"  # Replace with actual Vercel URL
]

# Environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')