
from flask import Flask
from werkzeug.security import generate_password_hash
import sys

from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)

def create_user(username, password, role):
    if role not in ['user1', 'user2']:
        print("Error: role must be 'user1' or 'user2'")
        return

    with app.app_context():
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"Error: User '{username}' already exists.")
            return

        password_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=password_hash, role=role)
        db.session.add(new_user)
        db.session.commit()
        print(f"User '{username}' with role '{role}' created successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: create_user.py <username> <password> <role>")
    else:
        _, username, password, role = sys.argv
        create_user(username, password, role)
