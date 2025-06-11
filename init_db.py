
from app_19_corrected import app
from models import db

with app.app_context():
    db.create_all()
    print("Database initialized.")
