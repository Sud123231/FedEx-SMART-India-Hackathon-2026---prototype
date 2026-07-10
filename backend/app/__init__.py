from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv
from app.models import db
from .config import Config
from app.routes.auth import auth_bp
from app.routes.enterprise import enterprise_bp
from app.routes.dca import dca_bp

load_dotenv()

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS (session-based)
    CORS(app, supports_credentials=True)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register routes
    app.register_blueprint(dca_bp, url_prefix="/api/dca")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(enterprise_bp, url_prefix="/api/enterprise")

    return app
