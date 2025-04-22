"""
FridgeToPlate Flask application initialization.
Modified for production deployment on Render.
"""
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app(config_name='default'):
    """Create and configure the Flask application.
    
    Args:
        config_name (str): Configuration environment name ('development', 'testing', 'production')
        
    Returns:
        Flask: Configured Flask application instance
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    from app.config import config
    app.config.from_object(config[config_name])
    
    # Initialize app with config-specific settings
    if hasattr(config[config_name], 'init_app'):
        config[config_name].init_app(app)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.ingredients import ingredients_bp
    from app.routes.recipes import recipes_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(ingredients_bp, url_prefix='/ingredients')
    app.register_blueprint(recipes_bp, url_prefix='/recipes')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('404.html'), 500
    
    return app
