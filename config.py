import os
from dotenv import load_dotenv

# Memuat file .env ke environment variables Python
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "belajarbackend.db")
SECRET_KEY = os.getenv("SECRET_KEY", "nyobain-bikin0-secretkey-987654321-12345")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))