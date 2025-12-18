import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Base configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    MONGO_URI = os.getenv('MONGO_URI')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}