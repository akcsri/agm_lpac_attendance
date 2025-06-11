from flask import Flask, request, redirect, url_for, render_template, Response
from flask_login import LoginManager, login_user, logout_user, current_user
from models import db, User, Participant

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
        User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            if user.role == 'user1':
                return redirect(url_for('user1_dashboard'))
            elif user.role == 'user2':
                return redirect(url_for('user2_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return 'Unknown role', 403
        else:
            return 'Invalid credentials', 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/user1_dashboard', methods=['GET', 'POST'])
def user1_dashboard():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        position = request.form.get('position')
        questions = request.form.get('questions')
        agm_status = request.form.get('agm_status')
        new_participant = Participant(
            name=name,
            email=email,
            position=position,
            questions=questions,
            agm_status=agm_status,
            user_id=current_user.id
        )
        db.session.add(new_participant)
        db.session.commit()
    participants = Participant.query.filter_by(user_id=current_user.id).all()
    return render_template('user1_dashboard.html', participants=participants)

@app.route('/user2_dashboard', methods=['GET', 'POST'])
def user2_dashboard():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        position = request.form.get('position')
        questions = request.form.get('questions')
        agm_status = request.form.get('agm_status')
        lpac_status = request.form.get('lpac_status')
        new_participant = Participant(
            name=name,
            email=email,
            position=position,
            questions=questions,
            agm_status=agm_status,
            lpac_status=lpac_status,
            user_id=current_user.id
        )
        db.session.add(new_participant)
        db.session.commit()
    participants = Participant.query.filter_by(user_id=current_user.id).all()
    return render_template('user2_dashboard.html', participants=participants)

@app.route('/update_participant/<int:participant_id>', methods=['POST'])
def update_participant(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    if participant.user_id != current_user.id:
        return "Unauthorized", 403
    participant.agm_status = request.form.get('agm_status')
    participant.lpac_status = request.form.get('lpac_status')  # user2 only
    db.session.commit()
    return redirect(request.referrer)

@app.route('/delete_participant/<int:participant_id>', methods=['POST'])
def delete_participant(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    if participant.user_id != current_user.id:
        return "Unauthorized", 403
    db.session.delete(participant)
    db.session.commit()
    return redirect(request.referrer)

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
