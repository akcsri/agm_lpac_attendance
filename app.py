
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from models import db, Participant, User

app = Flask(__name__)

# 🔧 Flaskアプリの設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  # 必要に応じて変更
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # セッション管理に必要

# 🔗 SQLAlchemyとアプリを接続
db.init_app(app)

# 🔐 ログインマネージャーの設定
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
        user = User.query.filter_by(username=username).first()
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
        login_user(user)
            if user.role == 'user1':    
            return redirect(url_for('user1_dashboard'))
            elif user.role == 'user2':
            return redirect(url_for('user2_dashboard'))
            elif user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
            else:
            return "Unknown role", 403
                elif user.role == 'user2':
                return redirect(url_for('user2_dashboard'))
                elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
                else:
                return "Unknown role", 403
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/user1_dashboard', methods=['GET', 'POST'])
@login_required
def user1_dashboard():
        if request.method == 'POST':
        participant = Participant.query.filter_by(
            name=request.form.get('name'), user_id=current_user.id).first()
            if not participant:
            participant = Participant(user_id=current_user.id)
            db.session.add(participant)
        participant.name = request.form.get('name')
        participant.email = request.form.get('email')
        participant.position = request.form.get('position')
        participant.questions = request.form.get('questions')
        participant.agm_status = request.form.get('agm_status')
        db.session.commit()
            if user.role == 'user1':
            if user.role == 'user1':
            return redirect(url_for('user1_dashboard'))
            elif user.role == 'user2':
            return redirect(url_for('user2_dashboard'))
            elif user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
            else:
            return "Unknown role", 403
                elif user.role == 'user2':
                return redirect(url_for('user2_dashboard'))
                elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
                else:
                return "Unknown role", 403
    participants = Participant.query.filter_by(user_id=current_user.id).all()
    return render_template('user1_dashboard.html', username=current_user.username, participants=participants)


@app.route('/user2_dashboard', methods=['GET', 'POST'])
@login_required
def user2_dashboard():
        if request.method == 'POST':
        participant = Participant.query.filter_by(
            name=request.form.get('name'), user_id=current_user.id).first()
            if not participant:
            participant = Participant(user_id=current_user.id)
            db.session.add(participant)
        participant.name = request.form.get('name')
        participant.email = request.form.get('email')
        participant.position = request.form.get('position')
        participant.questions = request.form.get('questions')
        participant.agm_status = request.form.get('agm_status')
        participant.lpac_status = request.form.get('lpac_status')
        db.session.commit()
        return redirect(url_for('user2_dashboard'))
    participants = Participant.query.filter_by(user_id=current_user.id).all()
    return render_template('user2_dashboard.html', username=current_user.username, participants=participants)


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    participants = Participant.query.all()
    return render_template('admin_dashboard.html', participants=participants)


    if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 初回実行時にテーブルを作成
    app.run(debug=True)
