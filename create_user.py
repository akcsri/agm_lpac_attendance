import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(80), nullable=False)

def create_user(username, password, role):
    new_user = User(username=username, password=password, role=role)
    db.session.add(new_user)
    db.session.commit()
    print(f"User '{username}' created successfully.")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python create_user.py <username> <password> <role>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    role = sys.argv[3]

    with app.app_context():
        create_user(username, password, role)
