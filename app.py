from flask import Flask, request, redirect, url_for, render_template, Response
from flask_login import LoginManager, login_user, logout_user
from models import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            if user.role == 'user1':
                return redirect(url_for('user1_dashboard'))
            elif user.role == 'user2':
                return redirect(url_for('user2_dashboard'))
            else:
            return 'Invalid credentials', 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/user1_dashboard')
def user1_dashboard():
    return render_template('user1_dashboard.html')

@app.route('/user2_dashboard')
def user2_dashboard():
    return render_template('user2_dashboard.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/download_csv')
def download_csv():
    csv_data = "name,role\nAlice,user1\nBob,user2"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=users.csv"}
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
