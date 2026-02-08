"""Routes module initialization"""
from .expenses import expenses_bp
from .auth import auth_bp

__all__ = ['expenses_bp', 'auth_bp']
