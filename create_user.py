
import sys
from models import db, User
from app import app
from werkzeug.security import generate_password_hash

def create_user(username, password, role):
    if role not in ['user1', 'user2', 'admin']:
        print("Error: role must be 'user1', 'user2', or 'admin'")
        return

    with app.app_context():
        user = User(username=username, password_hash=generate_password_hash(password), role=role)
        db.session.add(user)
        db.session.commit()
        print(f"User {username} with role {role} created successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: create_user.py <username> <password> <role>")
    else:
        create_user(sys.argv[1], sys.argv[2], sys.argv[3])
