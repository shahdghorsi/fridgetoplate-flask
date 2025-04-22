"""
Application entry point for the FridgeToPlate Flask application.
This file is configured for deployment to Render.
"""
import os
import sys

# Create uploads directory
os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads'), exist_ok=True)

# Create the Flask application instance
def create_app():
    from app import create_app as _create_app
    config_name = os.environ.get('FLASK_CONFIG', 'production')
    return _create_app(config_name)

# This is the variable that Gunicorn looks for
app = create_app()

if __name__ == '__main__':
    # Run the application when executed directly
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
