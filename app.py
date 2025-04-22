"""
Application entry point for the FridgeToPlate Flask application.
This file is configured for deployment to Render.
"""
import os
from app import create_app

# Get configuration from environment variable or use default
config_name = os.environ.get('FLASK_CONFIG', 'production')
app = create_app(config_name)

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads'), exist_ok=True)
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
