import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Settings
    SECRET_KEY = os.environ.get("SECRET_KEY")
    
    # Database Settings
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Security Settings
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
    SECURITY_PASSWORD_HASH = "argon2"
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    
    # Redirects after login/logout
    SECURITY_POST_LOGIN_VIEW = "/dashboard"
    SECURITY_POST_LOGOUT_VIEW = "/"