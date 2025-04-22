"""
Recipe model for the FridgeToPlate application.
"""
from app import db
from datetime import datetime

class Recipe(db.Model):
    """Recipe model representing cooking recipes."""
    
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500))
    source_url = db.Column(db.String(500))
    servings = db.Column(db.Integer)
    ready_in_minutes = db.Column(db.Integer)
    instructions = db.Column(db.Text)
    summary = db.Column(db.Text)
    is_fusion = db.Column(db.Boolean, default=False)
    cuisines = db.Column(db.String(200))  # Comma-separated list of cuisines
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        """String representation of the Recipe object."""
        return f'<Recipe {self.title}>'
    
    def to_dict(self):
        """Convert the Recipe object to a dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'image_url': self.image_url,
            'source_url': self.source_url,
            'servings': self.servings,
            'ready_in_minutes': self.ready_in_minutes,
            'instructions': self.instructions,
            'summary': self.summary,
            'is_fusion': self.is_fusion,
            'cuisines': self.cuisines.split(',') if self.cuisines else [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
