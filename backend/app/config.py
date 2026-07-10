import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Settings
    SECRET_KEY = os.environ.get("SECRET_KEY")
    
    # Database Settings
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    
    # Redirects after login/logout
    SECURITY_POST_LOGIN_VIEW = "/dashboard"
    SECURITY_POST_LOGOUT_VIEW = "/"

    #Session settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"