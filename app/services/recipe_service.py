"""
Recipe service for the FridgeToPlate application.

This module provides functionality to get recipe suggestions based on ingredients
and generate fusion recipes combining different cuisines.
"""
import requests
import random
from flask import current_app
import json

# Mock data for development without API keys
MOCK_RECIPES = [
    {
        "id": 1,
        "title": "Pasta with Tomato Sauce",
        "image_url": "https://spoonacular.com/recipeImages/pasta-tomato-sauce.jpg",
        "source_url": "https://example.com/pasta-tomato-sauce",
        "servings": 4,
        "ready_in_minutes": 30,
        "instructions": "1. Cook pasta according to package instructions.\n2. Heat olive oil in a pan and add garlic.\n3. Add tomatoes and simmer for 15 minutes.\n4. Season with salt, pepper, and basil.\n5. Combine pasta with sauce and serve.",
        "summary": "A simple and delicious pasta dish with homemade tomato sauce.",
        "cuisines": ["Italian"],
        "ingredients": ["pasta", "tomato", "garlic", "olive oil", "basil"]
    },
    {
        "id": 2,
        "title": "Vegetable Stir Fry",
        "image_url": "https://spoonacular.com/recipeImages/vegetable-stir-fry.jpg",
        "source_url": "https://example.com/vegetable-stir-fry",
        "servings": 2,
        "ready_in_minutes": 20,
        "instructions": "1. Heat oil in a wok or large pan.\n2. Add garlic and ginger and stir for 30 seconds.\n3. Add vegetables and stir fry for 5-7 minutes.\n4. Add soy sauce and sesame oil.\n5. Serve over rice.",
        "summary": "A quick and healthy vegetable stir fry that's perfect for weeknight dinners.",
        "cuisines": ["Asian", "Chinese"],
        "ingredients": ["carrot", "bell pepper", "broccoli", "garlic", "ginger", "soy sauce", "rice"]
    },
    {
        "id": 3,
        "title": "Chicken Salad",
        "image_url": "https://spoonacular.com/recipeImages/chicken-salad.jpg",
        "source_url": "https://example.com/chicken-salad",
        "servings": 2,
        "ready_in_minutes": 15,
        "instructions": "1. Mix cooked chicken, celery, and onion in a bowl.\n2. In another bowl, combine mayonnaise, lemon juice, and seasonings.\n3. Pour dressing over chicken mixture and toss to coat.\n4. Serve on lettuce leaves or as a sandwich.",
        "summary": "A classic chicken salad that's perfect for lunch or a light dinner.",
        "cuisines": ["American"],
        "ingredients": ["chicken", "celery", "onion", "mayonnaise", "lemon", "lettuce"]
    },
    {
        "id": 4,
        "title": "Beef Tacos",
        "image_url": "https://spoonacular.com/recipeImages/beef-tacos.jpg",
        "source_url": "https://example.com/beef-tacos",
        "servings": 4,
        "ready_in_minutes": 25,
        "instructions": "1. Brown ground beef in a pan and drain excess fat.\n2. Add taco seasoning and water, simmer for 5 minutes.\n3. Warm taco shells in the oven.\n4. Fill shells with beef and top with lettuce, tomato, cheese, and salsa.",
        "summary": "Easy and delicious beef tacos that the whole family will love.",
        "cuisines": ["Mexican"],
        "ingredients": ["beef", "taco shells", "lettuce", "tomato", "cheese", "salsa"]
    },
    {
        "id": 5,
        "title": "Vegetable Soup",
        "image_url": "https://spoonacular.com/recipeImages/vegetable-soup.jpg",
        "source_url": "https://example.com/vegetable-soup",
        "servings": 6,
        "ready_in_minutes": 45,
        "instructions": "1. Heat oil in a large pot and sauté onions and garlic.\n2. Add carrots and celery and cook for 5 minutes.\n3. Add broth, tomatoes, and seasonings.\n4. Bring to a boil, then reduce heat and simmer for 30 minutes.\n5. Add remaining vegetables and cook until tender.",
        "summary": "A hearty vegetable soup that's perfect for cold days.",
        "cuisines": ["American", "Italian"],
        "ingredients": ["onion", "garlic", "carrot", "celery", "tomato", "potato", "broth"]
    }
]

# Cuisine data for fusion recipes
CUISINE_DATA = {
    "Italian": {
        "ingredients": ["pasta", "tomato", "basil", "olive oil", "garlic", "parmesan"],
        "techniques": ["simmer", "sauté", "bake"],
        "flavors": ["herbaceous", "savory", "acidic"]
    },
    "Mexican": {
        "ingredients": ["corn", "beans", "chili", "lime", "cilantro", "avocado"],
        "techniques": ["grill", "fry", "roast"],
        "flavors": ["spicy", "citrusy", "fresh"]
    },
    "Indian": {
        "ingredients": ["rice", "lentils", "curry", "ginger", "turmeric", "yogurt"],
        "techniques": ["simmer", "toast spices", "pressure cook"],
        "flavors": ["aromatic", "spicy", "complex"]
    },
    "Chinese": {
        "ingredients": ["soy sauce", "rice", "ginger", "garlic", "sesame oil", "green onion"],
        "techniques": ["stir fry", "steam", "braise"],
        "flavors": ["umami", "balanced", "aromatic"]
    },
    "Japanese": {
        "ingredients": ["rice", "soy sauce", "mirin", "seaweed", "ginger", "wasabi"],
        "techniques": ["grill", "simmer", "raw preparation"],
        "flavors": ["umami", "clean", "subtle"]
    },
    "Thai": {
        "ingredients": ["rice", "coconut milk", "fish sauce", "lime", "chili", "lemongrass"],
        "techniques": ["stir fry", "pound", "grill"],
        "flavors": ["spicy", "sour", "aromatic"]
    },
    "French": {
        "ingredients": ["butter", "wine", "shallots", "herbs", "cream", "mustard"],
        "techniques": ["sauté", "braise", "roast"],
        "flavors": ["rich", "buttery", "complex"]
    },
    "Mediterranean": {
        "ingredients": ["olive oil", "lemon", "yogurt", "herbs", "eggplant", "chickpeas"],
        "techniques": ["grill", "roast", "bake"],
        "flavors": ["fresh", "herbaceous", "bright"]
    }
}

def get_recipes_by_ingredients(ingredients, recipe_id=None):
    """
    Get recipe suggestions based on available ingredients.
    
    Args:
        ingredients (list): List of ingredient names
        recipe_id (int, optional): Specific recipe ID to retrieve
        
    Returns:
        list or dict: List of recipe dictionaries or a single recipe dictionary if recipe_id is provided
    """
    # Check if we should use mock data
    if current_app.config.get('USE_MOCK_RECIPES', True):
        return _mock_get_recipes(ingredients, recipe_id)
    
    # Use Spoonacular API
    return _spoonacular_get_recipes(ingredients, recipe_id)

def generate_fusion_recipe(ingredients, cuisines):
    """
    Generate a fusion recipe combining different cuisines.
    
    Args:
        ingredients (list): List of available ingredient names
        cuisines (list): List of cuisine names to combine
        
    Returns:
        dict: Generated fusion recipe
    """
    # Check if we should use mock data
    if current_app.config.get('USE_MOCK_RECIPES', True):
        return _mock_generate_fusion(ingredients, cuisines)
    
    # Use Spoonacular API with some custom logic
    return _spoonacular_generate_fusion(ingredients, cuisines)

def _mock_get_recipes(ingredients, recipe_id=None):
    """
    Mock implementation of recipe suggestions for development.
    
    Args:
        ingredients (list): List of ingredient names
        recipe_id (int, optional): Specific recipe ID to retrieve
        
    Returns:
        list or dict: List of recipe dictionaries or a single recipe dictionary if recipe_id is provided
    """
    # If recipe_id is provided, return that specific recipe
    if recipe_id:
        for recipe in MOCK_RECIPES:
            if recipe['id'] == recipe_id:
                return recipe
        return None
    
    # Filter recipes based on ingredients
    matching_recipes = []
    
    for recipe in MOCK_RECIPES:
        # Count how many ingredients match
        matching_count = sum(1 for ing in recipe['ingredients'] if ing in ingredients)
        
        # If at least one ingredient matches, include the recipe
        if matching_count > 0:
            # Add a match score to sort by later
            recipe_copy = recipe.copy()
            recipe_copy['match_score'] = matching_count / len(recipe['ingredients'])
            matching_recipes.append(recipe_copy)
    
    # Sort by match score (highest first)
    matching_recipes.sort(key=lambda x: x['match_score'], reverse=True)
    
    # Remove the match_score before returning
    for recipe in matching_recipes:
        if 'match_score' in recipe:
            del recipe['match_score']
    
    return matching_recipes

def _spoonacular_get_recipes(ingredients, recipe_id=None):
    """
    Get recipe suggestions using Spoonacular API.
    
    Args:
        ingredients (list): List of ingredient names
        recipe_id (int, optional): Specific recipe ID to retrieve
        
    Returns:
        list or dict: List of recipe dictionaries or a single recipe dictionary if recipe_id is provided
    """
    api_key = current_app.config.get('SPOONACULAR_API_KEY')
    
    if not api_key:
        current_app.logger.warning("Spoonacular API key not found, using mock data")
        return _mock_get_recipes(ingredients, recipe_id)
    
    try:
        base_url = "https://api.spoonacular.com"
        
        # If recipe_id is provided, get that specific recipe
        if recipe_id:
            endpoint = f"/recipes/{recipe_id}/information"
            params = {
                "apiKey": api_key,
                "includeNutrition": False
            }
            
            response = requests.get(f"{base_url}{endpoint}", params=params)
            response.raise_for_status()
            
            recipe_data = response.json()
            
            # Format the response to match our model
            recipe = {
                "id": recipe_data.get("id"),
                "title": recipe_data.get("title"),
                "image_url": recipe_data.get("image"),
                "source_url": recipe_data.get("sourceUrl"),
                "servings": recipe_data.get("servings"),
                "ready_in_minutes": recipe_data.get("readyInMinutes"),
                "instructions": recipe_data.get("instructions"),
                "summary": recipe_data.get("summary"),
                "cuisines": recipe_data.get("cuisines", []),
                "ingredients": [ingredient.get("name") for ingredient in recipe_data.get("extendedIngredients", [])]
            }
            
            return recipe
        
        # Otherwise, search for recipes by ingredients
        endpoint = "/recipes/findByIngredients"
        params = {
            "apiKey": api_key,
            "ingredients": ",".join(ingredients),
            "number": 10,
            "ranking": 2,  # Maximize used ingredients
            "ignorePantry": True
        }
        
        response = requests.get(f"{base_url}{endpoint}", params=params)
        response.raise_for_status()
        
        recipes_data = response.json()
        recipe_ids = [recipe.get("id") for recipe in recipes_data]
        
        # Get detailed information for each recipe
        recipes = []
        for recipe_id in recipe_ids:
            recipe = _spoonacular_get_recipes([], recipe_id)
            if recipe:
                recipes.append(recipe)
        
        return recipes
        
    except Exception as e:
        current_app.logger.error(f"Error using Spoonacular API: {str(e)}")
        return _mock_get_recipes(ingredients, recipe_id)

def _mock_generate_fusion(ingredients, cuisines):
    """
    Mock implementation of fusion recipe generation for development.
    
    Args:
        ingredients (list): List of available ingredient names
        cuisines (list): List of cuisine names to combine
        
    Returns:
        dict: Generated fusion recipe
    """
    # Ensure we have valid cuisines
    valid_cuisines = [c for c in cuisines if c in CUISINE_DATA]
    
    if not valid_cuisines:
        valid_cuisines = random.sample(list(CUISINE_DATA.keys()), min(2, len(CUISINE_DATA)))
    
    # Get cuisine data for the selected cuisines
    cuisine_ingredients = []
    cuisine_techniques = []
    cuisine_flavors = []
    
    for cuisine in valid_cuisines:
        cuisine_data = CUISINE_DATA.get(cuisine, {})
        cuisine_ingredients.extend(cuisine_data.get("ingredients", []))
        cuisine_techniques.extend(cuisine_data.get("techniques", []))
        cuisine_flavors.extend(cuisine_data.get("flavors", []))
    
    # Filter ingredients based on what's available
    available_ingredients = [ing for ing in ingredients if ing]
    fusion_ingredients = []
    
    # Add available ingredients first
    for ing in available_ingredients:
        if ing not in fusion_ingredients:
            fusion_ingredients.append(ing)
    
    # Add some cuisine-specific ingredients
    for ing in cuisine_ingredients:
        if ing not in fusion_ingredients and len(fusion_ingredients) < 10:
            fusion_ingredients.append(ing)
    
    # Generate a fusion recipe name
    cuisine_names = " and ".join(valid_cuisines)
    main_ingredients = ", ".join(fusion_ingredients[:3])
    recipe_title = f"Fusion {main_ingredients.title()} ({cuisine_names} Style)"
    
    # Generate instructions
    techniques = random.sample(cuisine_techniques, min(3, len(cuisine_techniques)))
    flavors = random.sample(cuisine_flavors, min(2, len(cuisine_flavors)))
    
    instructions = f"1. Prepare all ingredients.\n"
    
    if "simmer" in techniques:
        instructions += f"2. Heat oil in a pan and add aromatics.\n"
        instructions += f"3. Add main ingredients and simmer until cooked through.\n"
    elif "stir fry" in techniques:
        instructions += f"2. Heat oil in a wok or large pan until very hot.\n"
        instructions += f"3. Quickly stir fry ingredients in small batches, starting with aromatics.\n"
    elif "grill" in techniques:
        instructions += f"2. Marinate main ingredients with spices and oil.\n"
        instructions += f"3. Grill until cooked through with nice char marks.\n"
    else:
        instructions += f"2. Combine ingredients in a suitable cooking vessel.\n"
        instructions += f"3. Cook using your preferred method until done.\n"
    
    instructions += f"4. Season to taste, aiming for a {' and '.join(flavors)} flavor profile.\n"
    instructions += f"5. Garnish with fresh herbs and serve immediately."
    
    # Create the fusion recipe
    fusion_recipe = {
        "id": random.randint(1000, 9999),
        "title": recipe_title,
        "image_url": "https://spoonacular.com/recipeImages/fusion-recipe.jpg",
        "source_url": "https://fridgetoplate.app/fusion",
        "servings": 4,
        "ready_in_minutes": random.randint(20, 60),
        "instructions": instructions,
        "summary": f"A creative fusion dish combining elements of {cuisine_names} cuisines, using ingredients you already have.",
        "cuisines": valid_cuisines,
        "ingredients": fusion_ingredients,
        "is_fusion": True
    }
    
    return fusion_recipe

def _spoonacular_generate_fusion(ingredients, cuisines):
    """
    Generate a fusion recipe using Spoonacular API with custom logic.
    
    Args:
        ingredients (list): List of available ingredient names
        cuisines (list): List of cuisine names to combine
        
    Returns:
        dict: Generated fusion recipe
    """
    api_key = current_app.config.get('SPOONACULAR_API_KEY')
    
    if not api_key:
        current_app.logger.warning("Spoonacular API key not found, using mock data")
        return _mock_generate_fusion(ingredients, cuisines)
    
    try:
        # First, get recipes for each cuisine
        cuisine_recipes = []
        
        for cuisine in cuisines:
            base_url = "https://api.spoonacular.com"
            endpoint = "/recipes/complexSearch"
            params = {
                "apiKey": api_key,
                "cuisine": cuisine,
                "includeIngredients": ",".join(ingredients),
                "number": 3,
                "addRecipeInformation": True
            }
            
            response = requests.get(f"{base_url}{endpoint}", params=params)
            response.raise_for_status()
            
            results = response.json().get("results", [])
            cuisine_recipes.extend(results)
        
        if not cuisine_recipes:
            current_app.logger.warning("No recipes found for fusion, using mock data")
            return _mock_generate_fusion(ingredients, cuisines)
        
        # Extract techniques, ingredients, and flavors from the recipes
        all_ingredients = []
        all_instructions = []
        
        for recipe in cuisine_recipes:
            # Extract ingredients
            for ingredient in recipe.get("extendedIngredients", []):
                all_ingredients.append(ingredient.get("name"))
            
            # Extract instructions
            all_instructions.append(recipe.get("instructions", ""))
        
        # Create a fusion recipe
        cuisine_names = " and ".join(cuisines)
        main_ingredients = ", ".join(ingredients[:3])
        recipe_title = f"Fusion {main_ingredients.title()} ({cuisine_names} Style)"
        
        # Generate instructions by combining elements from different recipes
        instructions = "This fusion recipe combines elements from multiple cuisines:\n\n"
        
        # Add some instructions from each recipe
        for i, recipe_instructions in enumerate(all_instructions):
            if recipe_instructions:
                # Extract a few steps from each recipe
                import re
                steps = re.split(r'\d+\.', recipe_instructions)
                steps = [s.strip() for s in steps if s.strip()]
                
                if steps:
                    selected_steps = random.sample(steps, min(2, len(steps)))
                    instructions += f"From {cuisines[i % len(cuisines)]} cuisine:\n"
                    for j, step in enumerate(selected_steps):
                        instructions += f"{j+1}. {step}\n"
                    instructions += "\n"
        
        # Create the fusion recipe
        fusion_recipe = {
            "id": random.randint(1000, 9999),
            "title": recipe_title,
            "image_url": cuisine_recipes[0].get("image") if cuisine_recipes else "https://spoonacular.com/recipeImages/fusion-recipe.jpg",
            "source_url": "https://fridgetoplate.app/fusion",
            "servings": 4,
            "ready_in_minutes": random.randint(30, 60),
            "instructions": instructions,
            "summary": f"A creative fusion dish combining elements of {cuisine_names} cuisines, using ingredients you already have.",
            "cuisines": cuisines,
            "ingredients": list(set(all_ingredients)),
            "is_fusion": True
        }
        
        return fusion_recipe
        
    except Exception as e:
        current_app.logger.error(f"Error generating fusion recipe: {str(e)}")
        return _mock_generate_fusion(ingredients, cuisines)
