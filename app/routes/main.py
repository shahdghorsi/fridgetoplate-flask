"""
Main routes for the FridgeToPlate application.
"""
from flask import Blueprint, render_template, current_app, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

@main_bp.route('/capture')
def capture():
    """Render the image capture page."""
    return render_template('capture.html')
