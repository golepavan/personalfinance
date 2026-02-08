"""
Configuration settings for Splitwise Analytics
API keys loaded from environment variables or .env file
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (explicit path)
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)


class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'splitwise-analytics-secret-key')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Database settings
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'splitwise_data.db')
    
    # Splitwise API credentials (no OAuth needed for local use)
    SPLITWISE_CONSUMER_KEY = os.getenv('SPLITWISE_CONSUMER_KEY', '')
    SPLITWISE_CONSUMER_SECRET = os.getenv('SPLITWISE_CONSUMER_SECRET', '')
    SPLITWISE_API_KEY = os.getenv('SPLITWISE_API_KEY', '')
    
    # Gemini API key
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Categories for expense classification
    EXPENSE_CATEGORIES = [
        'Food',
        'Grocery',
        'Transport',
        'Daily Essentials',
        'Shopping',
        'Entertainment',
        'Utilities',
        'Rent',
        'Travel',
        'Healthcare',
        'Subscriptions',
        'Education',
        'Personal Care',
        'Other'
    ]
