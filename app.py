
from flask import Flask, request, redirect, url_for, render_template, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import db, User, get_user_by_username, Participant
import io
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.role == 'user1':
                return redirect(url_for('user1_dashboard'))
            elif user.role == 'user2':
                return redirect(url_for('user2_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        return 'ログイン失敗'
    return render_template('login.html')

@app.route('/')
@login_required
def index():
    return render_template('index.html', username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/attendance', methods=['GET', 'POST'], endpoint='user_dashboard')
@login_required
def user_dashboard():
    if request.method == 'POST':
        participant = Participant.query.filter_by(name=request.form['name'], user_id=current_user.id).first()
        if not participant:
            participant = Participant(user_id=current_user.id)
            db.session.add(participant)
        participant.name = request.form['name']
        participant.email = request.form['email']
        participant.position = request.form['position']
        participant.questions = request.form['questions']
        participant.agm_status = request.form['agm_status']
        participant.lpac_status = request.form['lpac_status']
        db.session.commit()
        return redirect(url_for('user_dashboard'))
    participants = Participant.query.filter_by(user_id=current_user.id).all()
    return render_template('user_dashboard.html', username=current_user.username, participants=participants)

@app.route('/update/<int:participant_id>', methods=['POST'])
@login_required
def update_participant(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    participant.agm_status = request.form['agm_status']
    participant.lpac_status = request.form['lpac_status']
    db.session.commit()
    return redirect(url_for('user_dashboard'))

@app.route('/delete/<int:participant_id>', methods=['POST'])
@login_required
def delete_participant(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    db.session.delete(participant)
    db.session.commit()
    return redirect(url_for('user_dashboard'))

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    participants = Participant.query.all()
    present_count = Participant.query.filter_by(agm_status='出席').count()
    return render_template('admin_dashboard.html', participants=participants, present_count=present_count)

@app.route('/download_csv')
@login_required
def download_csv():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    participants = Participant.query.all()
    output = io.StringIO()
    output.write('﻿')
    writer = csv.writer(output)
    writer.writerow(['名前', 'メール', '質問', '役職', 'AGM出欠', 'LPAC出欠'])
    for p in participants:
        writer.writerow([p.name, p.email, p.questions, p.position, p.agm_status, p.lpac_status])
    output.seek(0)
    return Response(output, mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=participants.csv"})

@app.route('/user1_dashboard')
@login_required
def user1_dashboard():
    return render_template('user1_dashboard.html', username=current_user.username)

@app.route('/user2_dashboard')
@login_required
def user2_dashboard():
    return render_template('user2_dashboard.html', username=current_user.username)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
