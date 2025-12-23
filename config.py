"""
Configuration module for Flask application.
Loads settings from environment variables with sensible defaults.
"""
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with common settings."""
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv(
        'MONGODB_URI',
        'mongodb+srv://anupamsoni27:Mystuff8358%401@india-01.kwer3ek.mongodb.net/'
    )
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'mf_data')
    MONGODB_TLS_ALLOW_INVALID_CERTIFICATES = True
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv(
        'CORS_ORIGINS', 
        'http://localhost:4200,https://icy-hill-0f6a2fa00.1.azurestaticapps.net'
    ).split(',')
    CORS_SUPPORTS_CREDENTIALS = True
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @staticmethod
    def init_logging():
        """Initialize logging configuration."""
        log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format=Config.LOG_FORMAT,
            handlers=[
                logging.StreamHandler(),  # Console output
                logging.FileHandler(Config.LOG_FILE)  # File output
            ]
        )
        
        # Set specific loggers
        logging.getLogger('werkzeug').setLevel(logging.WARNING)  # Reduce Flask noise


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    FLASK_ENV = 'development'
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    FLASK_ENV = 'production'
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = True
    MONGODB_URI = 'mongodb://localhost:27017/'  # Will be mocked anyway
    LOG_LEVEL = 'ERROR'  # Reduce noise during tests


# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on FLASK_ENV environment variable."""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
