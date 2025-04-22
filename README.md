# FridgeToPlate Python

A Python-based web application that takes pictures of ingredients in your fridge and suggests recipes, including fusion cuisine options.

## Features

- **Ingredient Recognition**: Upload photos of ingredients using Google Cloud Vision API
- **Recipe Suggestions**: Find recipes that match your available ingredients
- **Fusion Cuisine Generator**: Create unique recipes combining different culinary traditions
- **Responsive Web Interface**: Works on desktop, tablet, and mobile devices

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML, CSS, JavaScript with Bootstrap
- **Image Recognition**: Google Cloud Vision API
- **Recipe Data**: Spoonacular API (with fallback to mock data)
- **Database**: SQLite (for development), PostgreSQL (for production)

## Project Structure

```
FridgeToPlate-Python/
├── app/
│   ├── __init__.py           # Flask application initialization
│   ├── config.py             # Configuration settings
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py           # Main routes
│   │   ├── ingredients.py    # Ingredient-related routes
│   │   └── recipes.py        # Recipe-related routes
│   ├── services/
│   │   ├── __init__.py
│   │   ├── image_recognition.py  # Google Cloud Vision integration
│   │   └── recipe_service.py     # Recipe suggestion and generation
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ingredient.py     # Ingredient data model
│   │   └── recipe.py         # Recipe data model
│   ├── static/
│   │   ├── css/              # Stylesheets
│   │   ├── js/               # JavaScript files
│   │   └── images/           # Static images
│   └── templates/            # Jinja2 HTML templates
│       ├── base.html         # Base template
│       ├── index.html        # Home page
│       ├── capture.html      # Image capture page
│       ├── ingredients.html  # Ingredients management page
│       └── recipes.html      # Recipe suggestions page
├── tests/                    # Unit and integration tests
├── .env.example              # Example environment variables
├── .gitignore                # Git ignore file
├── requirements.txt          # Python dependencies
├── run.py                    # Application entry point
└── README.md                 # Project documentation
```

## Setup and Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up environment variables (copy `.env.example` to `.env` and fill in values)
6. Run the application: `python run.py`

## API Keys Required

- Google Cloud Vision API key
- Spoonacular API key (optional, falls back to mock data)

## Development Guidelines

- Follow PEP 8 style guidelines
- Write unit tests for new functionality
- Use meaningful commit messages
- Document code using docstrings
