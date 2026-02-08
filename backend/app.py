"""
Splitwise Analytics - Flask Application
Main entry point for the backend API
"""

from flask import Flask, send_from_directory
from flask_cors import CORS
import os

from config import Config
from database.db_manager import init_db
from routes.expenses import expenses_bp
from routes.auth import auth_bp

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    app.config.from_object(Config)
    
    # Enable CORS for frontend
    CORS(app, origins=['http://localhost:5000', 'http://127.0.0.1:5000'])
    
    # Initialize database
    with app.app_context():
        init_db()
    
    # Register blueprints
    app.register_blueprint(expenses_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Serve frontend
    @app.route('/')
    def serve_frontend():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        if os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')
    
    return app


if __name__ == '__main__':
    app = create_app()
    print("🚀 Splitwise Analytics running at http://localhost:5000")
    app.run(debug=True, port=5000)
