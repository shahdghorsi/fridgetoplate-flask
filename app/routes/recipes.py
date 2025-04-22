"""
Recipe-related routes for the FridgeToPlate application.
"""
from flask import Blueprint, render_template, request, jsonify, current_app
from app.services.recipe_service import get_recipes_by_ingredients, generate_fusion_recipe
from app.models.ingredient import Ingredient

recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/')
def list_recipes():
    """Render the recipes page with suggestions based on available ingredients."""
    ingredients = Ingredient.query.all()
    ingredient_names = [ingredient.name for ingredient in ingredients]
    
    # Get recipe suggestions if ingredients are available
    recipes = []
    if ingredient_names:
        recipes = get_recipes_by_ingredients(ingredient_names)
    
    return render_template('recipes.html', recipes=recipes, ingredients=ingredients)

@recipes_bp.route('/detail/<int:recipe_id>')
def recipe_detail(recipe_id):
    """Render the recipe detail page."""
    # In a real application, we would fetch the recipe details from the API or database
    # For now, we'll use a mock implementation in the recipe service
    recipe = get_recipes_by_ingredients([], recipe_id=recipe_id)
    
    if not recipe:
        return render_template('404.html'), 404
    
    return render_template('recipe_detail.html', recipe=recipe)

@recipes_bp.route('/fusion', methods=['POST'])
def fusion():
    """Generate a fusion recipe."""
    data = request.get_json()
    
    if not data or 'cuisines' not in data or not data['cuisines']:
        return jsonify({'error': 'Cuisines are required'}), 400
    
    # Get available ingredients
    ingredients = Ingredient.query.all()
    ingredient_names = [ingredient.name for ingredient in ingredients]
    
    if not ingredient_names:
        return jsonify({'error': 'No ingredients available'}), 400
    
    # Generate fusion recipe
    recipe = generate_fusion_recipe(ingredient_names, data['cuisines'])
    
    return jsonify({
        'success': True,
        'recipe': recipe
    })
