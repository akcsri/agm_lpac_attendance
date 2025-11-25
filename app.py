from flask import Flask, request, redirect, url_for, render_template, flash, Response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import db, User, get_user_by_username, Participant
import os
import csv
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')

# データベース設定（PostgreSQL優先、フォールバックでSQLite）
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')

# DATABASE_URLの検証
if DATABASE_URL:
    print(f"📊 DATABASE_URL detected: {DATABASE_URL[:20]}...")
    if 'dpg-' in DATABASE_URL:
        print("✓ Render PostgreSQL detected")
        print("⚠️ IMPORTANT: Make sure you're using the INTERNAL Database URL")
        print("   (Not the External Database URL)")
else:
    print("⚠️ DATABASE_URL not set - using SQLite")
    print("⚠️ Data will NOT persist on Render with SQLite!")
    
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///agm_lpac.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DBとLoginManagerの初期化
db.init_app(app)

# アプリケーション起動時にテーブルを作成（既存のテーブル・データは保持される）
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created/verified successfully.")
        if DATABASE_URL:
            print(f"✅ Using PostgreSQL database")
        else:
            print("⚠️ Using SQLite database (data will not persist on Render)")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
        print("⚠️ App will continue but database operations may fail")
        print("⚠️ Please check your DATABASE_URL environment variable")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ユーザー読み込み関数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ログインルート
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            
            # ロールに応じてリダイレクト
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'user1':
                return redirect(url_for('user1_dashboard'))
            elif user.role == 'user2':
                return redirect(url_for('user2_dashboard'))
            else:
                return redirect(url_for('index'))
        flash('ログイン失敗：ユーザー名またはパスワードが正しくありません', 'error')
        return render_template('login.html')
    return render_template('login.html')

# ログイン後のトップページ
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# ログアウトルート
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ログアウトしました', 'success')
    return redirect(url_for('login'))

# User1ダッシュボード（AGMのみ）
@app.route('/user1_dashboard', methods=['GET', 'POST'])
@login_required
def user1_dashboard():
    if request.method == 'POST':
        position = request.form.get('position')
        name = request.form.get('name')
        email = request.form.get('email')
        questions = request.form.get('questions')
        agm_status = request.form.get('agm_status')

        # 既存の参加者をチェック
        participant = Participant.query.filter_by(name=name, user_id=current_user.id).first()
        
        if participant:
            # 更新
            participant.position = position
            participant.email = email
            participant.questions = questions
            participant.agm_status = agm_status
            flash('参加者情報を更新しました', 'success')
        else:
            # 新規追加
            participant = Participant(
                position=position,
                name=name,
                email=email,
                questions=questions,
                agm_status=agm_status,
                user_id=current_user.id
            )
            db.session.add(participant)
            flash('参加者を追加しました', 'success')
        
        db.session.commit()
        return redirect(url_for('user1_dashboard'))

    participants = Participant.query.filter_by(user_id=current_user.id).all()
    return render_template('user1_dashboard.html', participants=participants)

# User2ダッシュボード（AGMとLPAC）
@app.route('/user2_dashboard', methods=['GET', 'POST'])
@login_required
def user2_dashboard():
    if request.method == 'POST':
        position = request.form.get('position')
        name = request.form.get('name')
        email = request.form.get('email')
        questions = request.form.get('questions')
        agm_status = request.form.get('agm_status')
        lpac_status = request.form.get('lpac_status')

        # 既存の参加者をチェック
        participant = Participant.query.filter_by(name=name, user_id=current_user.id).first()
        
        if participant:
            # 更新
            participant.position = position
            participant.email = email
            participant.questions = questions
            participant.agm_status = agm_status
            participant.lpac_status = lpac_status
            flash('参加者情報を更新しました', 'success')
        else:
            # 新規追加
            participant = Participant(
                position=position,
                name=name,
                email=email,
                questions=questions,
                agm_status=agm_status,
                lpac_status=lpac_status,
                user_id=current_user.id
            )
            db.session.add(participant)
            flash('参加者を追加しました', 'success')
        
        db.session.commit()
        return redirect(url_for('user2_dashboard'))

    participants = Participant.query.filter_by(user_id=current_user.id).all()
    return render_template('user2_dashboard.html', participants=participants)

# 参加者更新
@app.route('/update_participant/<int:participant_id>', methods=['POST'])
@login_required
def update_participant(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    
    if participant.user_id != current_user.id and current_user.role != 'admin':
        flash('権限がありません', 'error')
        return redirect(url_for('index'))
    
    participant.position = request.form.get('position')
    participant.name = request.form.get('name')
    participant.email = request.form.get('email')
    participant.questions = request.form.get('questions')
    participant.agm_status = request.form.get('agm_status')
    participant.lpac_status = request.form.get('lpac_status')
    
    db.session.commit()
    flash('参加者情報を更新しました', 'success')
    return redirect(request.referrer or url_for('index'))

# 参加者削除
@app.route('/delete_participant/<int:participant_id>', methods=['POST'])
@login_required
def delete_participant(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    
    if participant.user_id != current_user.id and current_user.role != 'admin':
        flash('権限がありません', 'error')
        return redirect(url_for('index'))
    
    db.session.delete(participant)
    db.session.commit()
    flash('参加者を削除しました', 'success')
    return redirect(request.referrer or url_for('index'))

# 管理者用ダッシュボード
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('管理者のみアクセスできます', 'error')
        return redirect(url_for('index'))

    participants = Participant.query.all()
    
    # 出席者数をカウント
    agm_count = sum(1 for p in participants if p.agm_status == '出席')
    lpac_count = sum(1 for p in participants if p.lpac_status == '出席')
    
    return render_template('admin_dashboard.html', 
                          participants=participants, 
                          agm_count=agm_count,
                          lpac_count=lpac_count)

# CSVダウンロード
@app.route('/download_csv')
@login_required
def download_csv():
    if current_user.role != 'admin':
        flash('管理者のみアクセスできます', 'error')
        return redirect(url_for('index'))

    participants = Participant.query.all()

    output = io.StringIO()
    output.write('\ufeff')  # UTF-8 BOM を追加
    writer = csv.writer(output)
    writer.writerow(['ユーザー名', '役職', '名前', 'メール', '質問', 'AGMステータス', 'LPACステータス'])

    for p in participants:
        writer.writerow([
            p.user.username, 
            p.position, 
            p.name, 
            p.email, 
            p.questions or '', 
            p.agm_status or '', 
            p.lpac_status or ''
        ])

    output.seek(0)
    
    return Response(output, mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=agm_lpac_participants.csv"})

# アプリ起動時にDB作成（ローカル開発用）
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
