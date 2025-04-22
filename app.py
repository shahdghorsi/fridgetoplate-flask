"""
Application entry point for the FridgeToPlate Flask application.
This file is configured for deployment to Render.
"""
import os
from app import create_app

# Get configuration from environment variable or use default
config_name = os.environ.get('FLASK_CONFIG', 'production')
# Create the Flask application instance
application = create_app(config_name)
# Create 'app' variable that Gunicorn expects
app = application

# Create uploads directory
os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads'), exist_ok=True)

if __name__ == '__main__':
    # Run the application when executed directly
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
