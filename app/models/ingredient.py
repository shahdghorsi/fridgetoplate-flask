"""
Ingredient model for the FridgeToPlate application.
"""
from app import db
from datetime import datetime

class Ingredient(db.Model):
    """Ingredient model representing food items recognized from images or added manually."""
    
    __tablename__ = 'ingredients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        """String representation of the Ingredient object."""
        return f'<Ingredient {self.name}>'
    
    def to_dict(self):
        """Convert the Ingredient object to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
