"""
Ingredient-related routes for the FridgeToPlate application.
"""
from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
import os
import uuid
from werkzeug.utils import secure_filename
from app.services.image_recognition import recognize_ingredients
from app.models.ingredient import Ingredient
from app import db

ingredients_bp = Blueprint('ingredients', __name__)

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@ingredients_bp.route('/')
def list_ingredients():
    """Render the ingredients management page."""
    ingredients = Ingredient.query.all()
    return render_template('ingredients.html', ingredients=ingredients)

@ingredients_bp.route('/add', methods=['POST'])
def add_ingredient():
    """Add a new ingredient manually."""
    name = request.form.get('name')
    if name:
        ingredient = Ingredient(name=name)
        db.session.add(ingredient)
        db.session.commit()
    return redirect(url_for('ingredients'))

@ingredients_bp.route('/delete/<int:id>', methods=['POST'])
def delete_ingredient(id):
    """Delete an ingredient."""
    ingredient = Ingredient.query.get_or_404(id)
    db.session.delete(ingredient)
    db.session.commit()
    return redirect(url_for('ingredients'))

@ingredients_bp.route('/upload', methods=['POST'])
def upload_image():
    """Upload an image and recognize ingredients."""
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Generate a secure filename with UUID to prevent collisions
        filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Recognize ingredients in the image
        ingredients = recognize_ingredients(filepath)
        
        # Save recognized ingredients to database
        for ingredient_name in ingredients:
            # Check if ingredient already exists
            existing = Ingredient.query.filter_by(name=ingredient_name).first()
            if not existing:
                ingredient = Ingredient(name=ingredient_name)
                db.session.add(ingredient)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'ingredients': ingredients,
            'message': f'Recognized {len(ingredients)} ingredients'
        })
    
    return jsonify({'error': 'File type not allowed'}), 400
