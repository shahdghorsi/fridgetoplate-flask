"""
This is a standalone Flask application file for deployment on Render.
All necessary imports and configurations are contained in this single file.
"""
import os
import base64
import json
import tempfile
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import requests
from PIL import Image
import io

# Create Flask application with explicit template and static folder paths
app = Flask(__name__, 
           template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/templates'),
           static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static'))

# Configure application
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///fridgetoplate.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
db = SQLAlchemy(app)

# Define models
class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Ingredient {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'created_at': self.created_at.isoformat()
        }

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    source_url = db.Column(db.String(500), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    instructions = db.Column(db.Text, nullable=True)
    ingredients = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Recipe {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'image_url': self.image_url,
            'source_url': self.source_url,
            'summary': self.summary,
            'instructions': self.instructions,
            'ingredients': self.ingredients,
            'created_at': self.created_at.isoformat()
        }

# Create database tables
with app.app_context():
    db.create_all()

# Image recognition service
def recognize_ingredients_from_image(image_path):
    """
    Recognize ingredients from an image using Google Cloud Vision API or mock data.
    """
    use_mock = os.environ.get('USE_MOCK_VISION', 'True').lower() == 'true'
    
    if use_mock:
        # Return mock data for testing
        return [
            {'name': 'Tomato', 'confidence': 0.95},
            {'name': 'Onion', 'confidence': 0.92},
            {'name': 'Bell Pepper', 'confidence': 0.88},
            {'name': 'Garlic', 'confidence': 0.85},
            {'name': 'Chicken', 'confidence': 0.82}
        ]
    
    try:
        # Use Google Cloud Vision API
        from google.cloud import vision
        
        # Get credentials from environment variable
        credentials_base64 = os.environ.get('GOOGLE_CLOUD_CREDENTIALS_BASE64')
        if not credentials_base64:
            raise ValueError("Google Cloud credentials not found in environment variables")
        
        # Decode credentials
        credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
        
        # Create a temporary file to store credentials
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.write(credentials_json.encode('utf-8'))
            temp_path = temp.name
        
        try:
            # Initialize Vision client with credentials
            client = vision.ImageAnnotatorClient.from_service_account_json(temp_path)
            
            # Load image
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Perform label detection
            response = client.label_detection(image=image)
            labels = response.label_annotations
            
            # Filter for food-related labels
            food_labels = []
            food_keywords = ['food', 'vegetable', 'fruit', 'meat', 'ingredient', 'dish', 'cuisine']
            
            for label in labels:
                description = label.description.lower()
                # Check if it's likely a food item
                if any(keyword in description for keyword in food_keywords) or label.score > 0.7:
                    food_labels.append({
                        'name': label.description,
                        'confidence': label.score
                    })
            
            return food_labels[:10]  # Return top 10 food-related labels
        
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
    
    except Exception as e:
        print(f"Error recognizing ingredients: {str(e)}")
        # Fall back to mock data
        return [
            {'name': 'Tomato', 'confidence': 0.95},
            {'name': 'Onion', 'confidence': 0.92},
            {'name': 'Bell Pepper', 'confidence': 0.88},
            {'name': 'Garlic', 'confidence': 0.85},
            {'name': 'Chicken', 'confidence': 0.82}
        ]

# Recipe service
def get_recipes_by_ingredients(ingredients):
    """
    Get recipes based on ingredients using Spoonacular API or mock data.
    """
    use_mock = os.environ.get('USE_MOCK_RECIPES', 'True').lower() == 'true'
    
    if use_mock:
        # Return mock data for testing
        return [
            {
                'id': 1,
                'title': 'Tomato and Onion Pasta',
                'image_url': 'https://spoonacular.com/recipeImages/123456-556x370.jpg',
                'source_url': 'https://example.com/recipe1',
                'summary': 'A delicious pasta dish with tomatoes and onions.',
                'instructions': '1. Cook pasta. 2. Sauté onions. 3. Add tomatoes. 4. Mix with pasta.',
                'ingredients': 'Pasta, Tomatoes, Onions, Olive Oil, Salt, Pepper'
            },
            {
                'id': 2,
                'title': 'Bell Pepper and Chicken Stir Fry',
                'image_url': 'https://spoonacular.com/recipeImages/234567-556x370.jpg',
                'source_url': 'https://example.com/recipe2',
                'summary': 'A quick and easy stir fry with bell peppers and chicken.',
                'instructions': '1. Cut chicken into pieces. 2. Slice bell peppers. 3. Stir fry chicken. 4. Add bell peppers.',
                'ingredients': 'Chicken, Bell Peppers, Soy Sauce, Garlic, Ginger, Oil'
            },
            {
                'id': 3,
                'title': 'Garlic Chicken with Vegetables',
                'image_url': 'https://spoonacular.com/recipeImages/345678-556x370.jpg',
                'source_url': 'https://example.com/recipe3',
                'summary': 'Flavorful garlic chicken with mixed vegetables.',
                'instructions': '1. Marinate chicken with garlic. 2. Prepare vegetables. 3. Cook chicken. 4. Add vegetables.',
                'ingredients': 'Chicken, Garlic, Bell Peppers, Onions, Carrots, Olive Oil, Herbs'
            }
        ]
    
    try:
        # Use Spoonacular API
        api_key = os.environ.get('SPOONACULAR_API_KEY')
        if not api_key:
            raise ValueError("Spoonacular API key not found in environment variables")
        
        # Prepare ingredients string
        ingredients_str = ','.join(ingredients)
        
        # Make API request
        url = f"https://api.spoonacular.com/recipes/findByIngredients"
        params = {
            'apiKey': api_key,
            'ingredients': ingredients_str,
            'number': 5,
            'ranking': 2,  # Maximize used ingredients
            'ignorePantry': True
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        recipes_data = response.json()
        
        # Get detailed information for each recipe
        detailed_recipes = []
        for recipe in recipes_data:
            recipe_id = recipe['id']
            detail_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
            detail_params = {
                'apiKey': api_key,
                'includeNutrition': False
            }
            
            detail_response = requests.get(detail_url, params=detail_params)
            detail_response.raise_for_status()
            
            recipe_details = detail_response.json()
            
            # Extract ingredients
            ingredients_list = []
            for ingredient in recipe_details.get('extendedIngredients', []):
                ingredients_list.append(ingredient.get('original', ''))
            
            detailed_recipes.append({
                'id': recipe_details.get('id'),
                'title': recipe_details.get('title'),
                'image_url': recipe_details.get('image'),
                'source_url': recipe_details.get('sourceUrl'),
                'summary': recipe_details.get('summary'),
                'instructions': recipe_details.get('instructions'),
                'ingredients': ', '.join(ingredients_list)
            })
        
        return detailed_recipes
    
    except Exception as e:
        print(f"Error getting recipes: {str(e)}")
        # Fall back to mock data
        return [
            {
                'id': 1,
                'title': 'Tomato and Onion Pasta',
                'image_url': 'https://spoonacular.com/recipeImages/123456-556x370.jpg',
                'source_url': 'https://example.com/recipe1',
                'summary': 'A delicious pasta dish with tomatoes and onions.',
                'instructions': '1. Cook pasta. 2. Sauté onions. 3. Add tomatoes. 4. Mix with pasta.',
                'ingredients': 'Pasta, Tomatoes, Onions, Olive Oil, Salt, Pepper'
            },
            {
                'id': 2,
                'title': 'Bell Pepper and Chicken Stir Fry',
                'image_url': 'https://spoonacular.com/recipeImages/234567-556x370.jpg',
                'source_url': 'https://example.com/recipe2',
                'summary': 'A quick and easy stir fry with bell peppers and chicken.',
                'instructions': '1. Cut chicken into pieces. 2. Slice bell peppers. 3. Stir fry chicken. 4. Add bell peppers.',
                'ingredients': 'Chicken, Bell Peppers, Soy Sauce, Garlic, Ginger, Oil'
            }
        ]

def generate_fusion_recipe(ingredients, cuisine1, cuisine2):
    """
    Generate a fusion recipe combining two cuisines using the provided ingredients.
    """
    # Define cuisine characteristics
    cuisine_characteristics = {
        'italian': {
            'spices': ['basil', 'oregano', 'rosemary', 'thyme'],
            'cooking_methods': ['simmer', 'bake', 'grill'],
            'base_ingredients': ['tomatoes', 'olive oil', 'garlic', 'pasta']
        },
        'mexican': {
            'spices': ['cumin', 'cilantro', 'chili powder', 'oregano'],
            'cooking_methods': ['grill', 'fry', 'simmer'],
            'base_ingredients': ['beans', 'corn', 'avocado', 'lime']
        },
        'indian': {
            'spices': ['turmeric', 'cumin', 'coriander', 'garam masala'],
            'cooking_methods': ['simmer', 'fry', 'steam'],
            'base_ingredients': ['rice', 'lentils', 'yogurt', 'ghee']
        },
        'chinese': {
            'spices': ['five spice', 'star anise', 'ginger', 'garlic'],
            'cooking_methods': ['stir-fry', 'steam', 'braise'],
            'base_ingredients': ['soy sauce', 'rice', 'sesame oil', 'green onions']
        },
        'japanese': {
            'spices': ['wasabi', 'ginger', 'shiso', 'togarashi'],
            'cooking_methods': ['grill', 'steam', 'fry'],
            'base_ingredients': ['rice', 'miso', 'soy sauce', 'sake']
        },
        'thai': {
            'spices': ['lemongrass', 'galangal', 'Thai basil', 'chili'],
            'cooking_methods': ['stir-fry', 'simmer', 'grill'],
            'base_ingredients': ['coconut milk', 'fish sauce', 'lime', 'rice noodles']
        }
    }
    
    # Get characteristics for selected cuisines
    cuisine1_data = cuisine_characteristics.get(cuisine1.lower(), cuisine_characteristics['italian'])
    cuisine2_data = cuisine_characteristics.get(cuisine2.lower(), cuisine_characteristics['chinese'])
    
    # Create fusion recipe
    fusion_title = f"{cuisine1.title()}-{cuisine2.title()} Fusion with {', '.join(ingredients[:3])}"
    
    # Combine spices and cooking methods
    fusion_spices = cuisine1_data['spices'][:2] + cuisine2_data['spices'][:2]
    fusion_cooking_method = cuisine1_data['cooking_methods'][0] + " and " + cuisine2_data['cooking_methods'][0]
    
    # Create ingredient list
    fusion_ingredients = ingredients + fusion_spices
    fusion_ingredients.extend([item for item in cuisine1_data['base_ingredients'][:2] if item not in fusion_ingredients])
    fusion_ingredients.extend([item for item in cuisine2_data['base_ingredients'][:2] if item not in fusion_ingredients])
    
    # Generate instructions
    instructions = [
        f"1. Prepare all ingredients: {', '.join(ingredients)}.",
        f"2. Season with {', '.join(fusion_spices)}.",
        f"3. {fusion_cooking_method.title()} the main ingredients.",
        f"4. Add {cuisine1_data['base_ingredients'][0]} and {cuisine2_data['base_ingredients'][0]}.",
        f"5. Finish with {cuisine1_data['base_ingredients'][1]} and {cuisine2_data['base_ingredients'][1]}.",
        f"6. Serve hot and enjoy your {cuisine1.title()}-{cuisine2.title()} fusion dish!"
    ]
    
    return {
        'id': str(uuid.uuid4()),
        'title': fusion_title,
        'image_url': 'https://example.com/fusion_recipe.jpg',
        'summary': f"A creative fusion of {cuisine1.title()} and {cuisine2.title()} cuisines using {', '.join(ingredients)}.",
        'instructions': '\n'.join(instructions),
        'ingredients': ', '.join(fusion_ingredients)
    }

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/capture', methods=['GET', 'POST'])
def capture():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['image']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Recognize ingredients
            ingredients = recognize_ingredients_from_image(file_path)
            
            # Store in session
            session['recognized_ingredients'] = ingredients
            
            return redirect(url_for('ingredients'))
    
    return render_template('capture.html')

@app.route('/ingredients', methods=['GET', 'POST'])
def ingredients():
    if request.method == 'POST':
        # Add new ingredient
        name = request.form.get('name')
        quantity = request.form.get('quantity', '')
        
        if name:
            ingredient = Ingredient(name=name, quantity=quantity)
            db.session.add(ingredient)
            db.session.commit()
            flash(f'Added {name} to ingredients')
    
    # Get recognized ingredients from session
    recognized_ingredients = session.get('recognized_ingredients', [])
    
    # Get all ingredients from database
    all_ingredients = Ingredient.query.all()
    
    return render_template('ingredients.html', 
                          recognized_ingredients=recognized_ingredients,
                          ingredients=all_ingredients)

@app.route('/ingredients/add', methods=['POST'])
def add_ingredient():
    data = request.json
    name = data.get('name')
    quantity = data.get('quantity', '')
    
    if name:
        ingredient = Ingredient(name=name, quantity=quantity)
        db.session.add(ingredient)
        db.session.commit()
        return jsonify({'success': True, 'ingredient': ingredient.to_dict()})
    
    return jsonify({'success': False, 'error': 'Name is required'}), 400

@app.route('/ingredients/delete/<int:id>', methods=['POST'])
def delete_ingredient(id):
    ingredient = Ingredient.query.get_or_404(id)
    db.session.delete(ingredient)
    db.session.commit()
    flash(f'Deleted {ingredient.name} from ingredients')
    return redirect(url_for('ingredients'))

@app.route('/recipes')
def recipes():
    # Get all ingredients from database
    all_ingredients = Ingredient.query.all()
    ingredient_names = [ingredient.name for ingredient in all_ingredients]
    
    # Get recipes based on ingredients
    recipe_list = get_recipes_by_ingredients(ingredient_names)
    
    return render_template('recipes.html', recipes=recipe_list)

@app.route('/recipes/<int:id>')
def recipe_detail(id):
    # Get all recipes
    all_ingredients = Ingredient.query.all()
    ingredient_names = [ingredient.name for ingredient in all_ingredients]
    recipe_list = get_recipes_by_ingredients(ingredient_names)
    
    # Find the specific recipe
    recipe = next((r for r in recipe_list if r['id'] == id), None)
    
    if not recipe:
        flash('Recipe not found')
        return redirect(url_for('recipes'))
    
    return render_template('recipe_detail.html', recipe=recipe)

@app.route('/fusion', methods=['POST'])
def fusion():
    data = request.json
    ingredients = data.get('ingredients', [])
    cuisine1 = data.get('cuisine1', 'italian')
    cuisine2 = data.get('cuisine2', 'chinese')
    
    fusion_recipe = generate_fusion_recipe(ingredients, cuisine1, cuisine2)
    
    return jsonify({'success': True, 'recipe': fusion_recipe})

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Run the application
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
