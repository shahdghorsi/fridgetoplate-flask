"""
Image recognition service for the FridgeToPlate application.

This module provides functionality to recognize ingredients in images
using Google Cloud Vision API or mock data for development.
"""
import os
import io
import base64
from flask import current_app
from google.cloud import vision
from google.oauth2 import service_account
import json

# Mock data for development without API keys
MOCK_INGREDIENTS = {
    'apple': ['apple', 'fruit', 'red apple', 'green apple'],
    'banana': ['banana', 'fruit', 'yellow banana'],
    'carrot': ['carrot', 'vegetable', 'orange carrot'],
    'tomato': ['tomato', 'vegetable', 'red tomato'],
    'onion': ['onion', 'vegetable', 'white onion', 'yellow onion'],
    'potato': ['potato', 'vegetable', 'russet potato'],
    'chicken': ['chicken', 'meat', 'chicken breast', 'chicken thigh'],
    'beef': ['beef', 'meat', 'ground beef', 'beef steak'],
    'fish': ['fish', 'seafood', 'salmon', 'tuna'],
    'rice': ['rice', 'grain', 'white rice', 'brown rice'],
    'pasta': ['pasta', 'grain', 'spaghetti', 'penne'],
    'cheese': ['cheese', 'dairy', 'cheddar cheese', 'mozzarella'],
    'milk': ['milk', 'dairy', 'whole milk', 'skim milk'],
    'egg': ['egg', 'protein', 'chicken egg'],
    'bread': ['bread', 'bakery', 'white bread', 'whole wheat bread'],
    'lettuce': ['lettuce', 'vegetable', 'green lettuce', 'romaine lettuce'],
    'cucumber': ['cucumber', 'vegetable', 'green cucumber'],
    'pepper': ['pepper', 'vegetable', 'bell pepper', 'red pepper', 'green pepper'],
    'garlic': ['garlic', 'vegetable', 'garlic clove'],
    'lemon': ['lemon', 'fruit', 'yellow lemon'],
}

def recognize_ingredients(image_path):
    """
    Recognize ingredients in an image using Google Cloud Vision API or mock data.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        list: List of recognized ingredient names
    """
    # Check if we should use mock data
    if current_app.config.get('USE_MOCK_VISION', True):
        return _mock_recognize_ingredients(image_path)
    
    # Use Google Cloud Vision API
    return _vision_api_recognize_ingredients(image_path)

def _mock_recognize_ingredients(image_path):
    """
    Mock implementation of ingredient recognition for development.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        list: List of mock ingredient names based on the image filename
    """
    # Extract filename without path and extension
    filename = os.path.basename(image_path).lower()
    
    # Initialize results
    results = []
    
    # Check if filename contains any of our mock ingredients
    for ingredient, variations in MOCK_INGREDIENTS.items():
        if any(variation in filename for variation in variations):
            results.append(ingredient)
    
    # If no matches found, return some default ingredients
    if not results:
        # Return 2-4 random ingredients
        import random
        num_ingredients = random.randint(2, 4)
        results = random.sample(list(MOCK_INGREDIENTS.keys()), num_ingredients)
    
    return results

def _vision_api_recognize_ingredients(image_path):
    """
    Recognize ingredients in an image using Google Cloud Vision API.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        list: List of recognized ingredient names
    """
    api_key = current_app.config.get('GOOGLE_CLOUD_VISION_API_KEY')
    
    if not api_key:
        current_app.logger.warning("Google Cloud Vision API key not found, using mock data")
        return _mock_recognize_ingredients(image_path)
    
    try:
        # Initialize Vision client
        client = vision.ImageAnnotatorClient.from_service_account_json(api_key)
        
        # Read image file
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        
        # Perform label detection
        response = client.label_detection(image=image)
        labels = response.label_annotations
        
        # Filter for food-related labels
        food_labels = []
        for label in labels:
            if _is_food_related(label.description):
                food_labels.append(label.description.lower())
        
        # If no food items detected, use object detection as fallback
        if not food_labels:
            response = client.object_localization(image=image)
            objects = response.localized_object_annotations
            
            for obj in objects:
                if _is_food_related(obj.name):
                    food_labels.append(obj.name.lower())
        
        # Map detected labels to known ingredients
        ingredients = _map_labels_to_ingredients(food_labels)
        
        return ingredients
        
    except Exception as e:
        current_app.logger.error(f"Error using Vision API: {str(e)}")
        return _mock_recognize_ingredients(image_path)

def _is_food_related(label):
    """
    Check if a label is related to food.
    
    Args:
        label (str): The label to check
        
    Returns:
        bool: True if the label is food-related, False otherwise
    """
    food_categories = [
        'food', 'fruit', 'vegetable', 'meat', 'dairy', 'grain', 'spice', 
        'herb', 'beverage', 'dish', 'meal', 'ingredient', 'produce'
    ]
    
    label_lower = label.lower()
    
    # Check if label contains any food category
    if any(category in label_lower for category in food_categories):
        return True
    
    # Check if label is a known ingredient
    for ingredient in MOCK_INGREDIENTS.keys():
        if ingredient in label_lower:
            return True
    
    return False

def _map_labels_to_ingredients(labels):
    """
    Map detected labels to known ingredients.
    
    Args:
        labels (list): List of detected labels
        
    Returns:
        list: List of ingredient names
    """
    ingredients = set()
    
    for label in labels:
        # Check if label directly matches a known ingredient
        for ingredient, variations in MOCK_INGREDIENTS.items():
            if label in variations or ingredient in label:
                ingredients.add(ingredient)
    
    return list(ingredients)
