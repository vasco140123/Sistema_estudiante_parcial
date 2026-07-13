import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    db_url = os.getenv("DATABASE_URL")
    if db_url and db_url.startswith("mysql://"):
        db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)
    
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)