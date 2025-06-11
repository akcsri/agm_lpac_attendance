import sys
from app_19_corrected import app
from models import db, User
from werkzeug.security import generate_password_hash

def create_user(username, password, role):
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()
    print(f"✅ User '{username}' created successfully.")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python create_user.py <username> <password> <role>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    role = sys.argv[3]

    with app.app_context():
        create_user(username, password, role)
