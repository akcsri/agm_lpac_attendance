from flask import Flask, request, redirect, url_for, render_template, flash, Response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash
from models import db, User, get_user_by_username, Participant
import os
import csv
import io
from datetime import datetime

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

# メール設定
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', os.environ.get('MAIL_USERNAME'))
# 通知先メールアドレス（カンマ区切りで複数指定可能）
app.config['NOTIFICATION_EMAILS'] = os.environ.get('NOTIFICATION_EMAILS', '').split(',') if os.environ.get('NOTIFICATION_EMAILS') else []

# DBとLoginManagerの初期化
db.init_app(app)
mail = Mail(app)

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

# メール通知関数
def send_notification_email(subject, body):
    """管理者に通知メールを送信（複数アドレス対応）"""
    if not app.config['NOTIFICATION_EMAILS'] or not app.config['NOTIFICATION_EMAILS'][0]:
        print("⚠️ NOTIFICATION_EMAILS not configured. Email not sent.")
        return
    
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        print("⚠️ Mail credentials not configured. Email not sent.")
        return
    
    try:
        # 空文字列を除外してクリーンアップ
        recipients = [email.strip() for email in app.config['NOTIFICATION_EMAILS'] if email.strip()]
        
        if not recipients:
            print("⚠️ No valid email addresses configured.")
            return
        
        msg = Message(
            subject=f"[AGM/LPAC Attendance] {subject}",
            recipients=recipients,
            body=body
        )
        mail.send(msg)
        print(f"✅ Email sent to {len(recipients)} recipient(s): {subject}")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")

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
            
            # ログイン通知メール
            send_notification_email(
                subject="ユーザーログイン",
                body=f"ユーザー: {username}\n時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nロール: {user.role}"
            )
            
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
    username = current_user.username
    logout_user()
    
    # ログアウト通知メール
    send_notification_email(
        subject="ユーザーログアウト",
        body=f"ユーザー: {username}\n時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
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
            old_data = f"{participant.position} - {participant.name} - {participant.email} - AGM:{participant.agm_status}"
            participant.position = position
            participant.email = email
            participant.questions = questions
            participant.agm_status = agm_status
            action = "更新"
            
            # 更新通知メール
            send_notification_email(
                subject="参加者情報更新",
                body=f"操作: 参加者情報更新\n"
                     f"ユーザー: {current_user.username}\n"
                     f"時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                     f"【変更前】\n{old_data}\n\n"
                     f"【変更後】\n{position} - {name} - {email} - AGM:{agm_status}\n"
                     f"質問: {questions or '（なし）'}"
            )
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
            action = "追加"
            
            # 追加通知メール
            send_notification_email(
                subject="参加者追加",
                body=f"操作: 参加者追加\n"
                     f"ユーザー: {current_user.username}\n"
                     f"時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                     f"役職: {position}\n"
                     f"氏名: {name}\n"
                     f"メール: {email}\n"
                     f"AGMステータス: {agm_status}\n"
                     f"質問: {questions or '（なし）'}"
            )
        
        db.session.commit()
        flash(f'参加者を{action}しました', 'success')
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
            old_data = f"{participant.position} - {participant.name} - {participant.email} - AGM:{participant.agm_status} LPAC:{participant.lpac_status}"
            participant.position = position
            participant.email = email
            participant.questions = questions
            participant.agm_status = agm_status
            participant.lpac_status = lpac_status
            action = "更新"
            
            # 更新通知メール
            send_notification_email(
                subject="参加者情報更新",
                body=f"操作: 参加者情報更新\n"
                     f"ユーザー: {current_user.username}\n"
                     f"時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                     f"【変更前】\n{old_data}\n\n"
                     f"【変更後】\n{position} - {name} - {email}\n"
                     f"AGM: {agm_status}, LPAC: {lpac_status}\n"
                     f"質問: {questions or '（なし）'}"
            )
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
            action = "追加"
            
            # 追加通知メール
            send_notification_email(
                subject="参加者追加",
                body=f"操作: 参加者追加\n"
                     f"ユーザー: {current_user.username}\n"
                     f"時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                     f"役職: {position}\n"
                     f"氏名: {name}\n"
                     f"メール: {email}\n"
                     f"AGMステータス: {agm_status}\n"
                     f"LPACステータス: {lpac_status}\n"
                     f"質問: {questions or '（なし）'}"
            )
        
        db.session.commit()
        flash(f'参加者を{action}しました', 'success')
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
    
    # 変更前のデータを保存
    old_agm = participant.agm_status
    old_lpac = participant.lpac_status
    
    participant.position = request.form.get('position')
    participant.name = request.form.get('name')
    participant.email = request.form.get('email')
    participant.questions = request.form.get('questions')
    participant.agm_status = request.form.get('agm_status')
    participant.lpac_status = request.form.get('lpac_status')
    
    # ステータス更新通知メール
    status_change = []
    if old_agm != participant.agm_status:
        status_change.append(f"AGM: {old_agm} → {participant.agm_status}")
    if old_lpac != participant.lpac_status:
        status_change.append(f"LPAC: {old_lpac} → {participant.lpac_status}")
    
    if status_change:
        send_notification_email(
            subject="参加者ステータス更新",
            body=f"操作: ステータス更新\n"
                 f"ユーザー: {current_user.username}\n"
                 f"時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                 f"参加者: {participant.position} - {participant.name}\n"
                 f"変更内容:\n" + "\n".join(status_change)
        )
    
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
    
    participant_info = f"{participant.position} - {participant.name} - {participant.email}"
    
    db.session.delete(participant)
    db.session.commit()
    
    # 削除通知メール
    send_notification_email(
        subject="参加者削除",
        body=f"操作: 参加者削除\n"
             f"ユーザー: {current_user.username}\n"
             f"時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
             f"削除された参加者: {participant_info}"
    )
    
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
    
    # 出席者数をカウント（対面+オンライン）
    agm_present_inperson = sum(1 for p in participants if p.agm_status == '出席（対面）')
    agm_present_online = sum(1 for p in participants if p.agm_status == '出席（オンライン）')
    agm_count = agm_present_inperson + agm_present_online
    
    lpac_present_inperson = sum(1 for p in participants if p.lpac_status == '出席（対面）')
    lpac_present_online = sum(1 for p in participants if p.lpac_status == '出席（オンライン）')
    lpac_count = lpac_present_inperson + lpac_present_online
    
    return render_template('admin_dashboard.html', 
                          participants=participants, 
                          agm_count=agm_count,
                          agm_present_inperson=agm_present_inperson,
                          agm_present_online=agm_present_online,
                          lpac_count=lpac_count,
                          lpac_present_inperson=lpac_present_inperson,
                          lpac_present_online=lpac_present_online)

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

# CSVインポート機能（管理者のみ）
@app.route('/import_csv', methods=['GET', 'POST'])
@login_required
def import_csv():
    if current_user.role != 'admin':
        flash('管理者のみがインポートできます', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('ファイルが選択されていません', 'error')
            return redirect(url_for('import_csv'))
        
        file = request.files['csv_file']
        
        if file.filename == '':
            flash('ファイルが選択されていません', 'error')
            return redirect(url_for('import_csv'))
        
        if not file.filename.endswith('.csv'):
            flash('CSVファイルを選択してください', 'error')
            return redirect(url_for('import_csv'))
        
        try:
            # CSVを読み込む
            stream = io.StringIO(file.stream.read().decode("UTF-8-SIG"), newline=None)
            csv_reader = csv.DictReader(stream)
            
            imported_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):  # ヘッダーの次から
                try:
                    # 必須フィールドのチェック
                    username = row.get('ユーザー名', '').strip()
                    position = row.get('役職', '').strip()
                    name = row.get('名前', '').strip()
                    email = row.get('メール', '').strip()
                    agm_status = row.get('AGMステータス', '').strip()
                    lpac_status = row.get('LPACステータス', '').strip()
                    questions = row.get('質問', '').strip()
                    
                    if not all([username, position, name, email]):
                        errors.append(f"行{row_num}: 必須項目が不足しています")
                        continue
                    
                    # ユーザーを検索
                    user = User.query.filter_by(username=username).first()
                    if not user:
                        errors.append(f"行{row_num}: ユーザー '{username}' が見つかりません")
                        continue
                    
                    # 既存の参加者をチェック
                    participant = Participant.query.filter_by(name=name, user_id=user.id).first()
                    
                    if participant:
                        # 更新
                        participant.position = position
                        participant.email = email
                        participant.questions = questions
                        participant.agm_status = agm_status
                        participant.lpac_status = lpac_status
                    else:
                        # 新規追加
                        participant = Participant(
                            position=position,
                            name=name,
                            email=email,
                            questions=questions,
                            agm_status=agm_status,
                            lpac_status=lpac_status,
                            user_id=user.id
                        )
                        db.session.add(participant)
                    
                    imported_count += 1
                
                except Exception as e:
                    errors.append(f"行{row_num}: {str(e)}")
            
            db.session.commit()
            
            # インポート通知メール
            error_details = ""
            if errors:
                error_details = "\nエラー詳細:\n" + "\n".join(errors)
            else:
                error_details = "\n全て正常にインポートされました"
            
            send_notification_email(
                subject="CSVインポート実行",
                body=f"操作: CSVインポート\n"
                     f"実行ユーザー: {current_user.username}\n"
                     f"時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                     f"インポート成功: {imported_count}件\n"
                     f"エラー: {len(errors)}件"
                     f"{error_details}"
            )
            
            if imported_count > 0:
                flash(f'{imported_count}件のデータをインポートしました', 'success')
            if errors:
                flash(f'{len(errors)}件のエラーがありました: ' + '; '.join(errors[:5]), 'error')
            
            return redirect(url_for('admin_dashboard'))
        
        except Exception as e:
            flash(f'インポートエラー: {str(e)}', 'error')
            return redirect(url_for('import_csv'))
    
    return render_template('import_csv.html')

# ユーザーインポート機能（管理者のみ）
@app.route('/import_users', methods=['GET', 'POST'])
@login_required
def import_users():
    if current_user.role != 'admin':
        flash('管理者のみがインポートできます', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('ファイルが選択されていません', 'error')
            return redirect(url_for('import_users'))
        
        file = request.files['csv_file']
        
        if file.filename == '' or not file.filename.endswith('.csv'):
            flash('CSVファイルを選択してください', 'error')
            return redirect(url_for('import_users'))
        
        try:
            from werkzeug.security import generate_password_hash
            
            stream = io.StringIO(file.stream.read().decode("UTF-8-SIG"), newline=None)
            csv_reader = csv.DictReader(stream)
            
            imported_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    username = row.get('ユーザー名', '').strip()
                    password = row.get('パスワード', '').strip()
                    role = row.get('ロール', 'user1').strip()
                    
                    if not all([username, password]):
                        errors.append(f"行{row_num}: ユーザー名とパスワードは必須です")
                        continue
                    
                    # ロールの検証
                    if role not in ['admin', 'user1', 'user2']:
                        errors.append(f"行{row_num}: ロールは admin, user1, user2 のいずれかである必要があります")
                        continue
                    
                    # 既存ユーザーチェック
                    existing_user = User.query.filter_by(username=username).first()
                    if existing_user:
                        errors.append(f"行{row_num}: ユーザー '{username}' は既に存在します")
                        continue
                    
                    # 新規ユーザー作成
                    new_user = User(
                        username=username,
                        password_hash=generate_password_hash(password),
                        role=role
                    )
                    db.session.add(new_user)
                    imported_count += 1
                
                except Exception as e:
                    errors.append(f"行{row_num}: {str(e)}")
            
            db.session.commit()
            
            # ユーザーインポート通知メール
            send_notification_email(
                subject="ユーザーCSVインポート実行",
                body=f"操作: ユーザーインポート\n"
                     f"実行ユーザー: {current_user.username}\n"
                     f"時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                     f"インポート成功: {imported_count}件\n"
                     f"エラー: {len(errors)}件"
            )
            
            if imported_count > 0:
                flash(f'{imported_count}件のユーザーをインポートしました', 'success')
            if errors:
                flash(f'{len(errors)}件のエラー: ' + '; '.join(errors[:5]), 'error')
            
            return redirect(url_for('admin_dashboard'))
        
        except Exception as e:
            flash(f'インポートエラー: {str(e)}', 'error')
            return redirect(url_for('import_users'))
    
    return render_template('import_users.html')

# アドミ業務ポータル用API（出席者の一覧をJSONで返す）
# Fly.io の secrets に ATTENDANCE_API_TOKEN を設定し、ポータルの「出欠アプリの設定」に同じトークンを入れる。
# 未設定のときは常に 401（APIは使えない）。
@app.route('/api/participants')
def api_participants():
    import hmac
    token = os.environ.get('ATTENDANCE_API_TOKEN', '')
    given = request.headers.get('X-API-Token', '')
    if not token or not hmac.compare_digest(token, given):
        return {'error': 'unauthorized'}, 401
    rows = []
    for p in Participant.query.all():
        rows.append({
            'username': p.user.username if p.user else '',
            'company': '',
            'position': p.position or '',
            'name': p.name or '',
            'email': p.email or '',
            'questions': p.questions or '',
            'agm_status': p.agm_status or '',
            'lpac_status': p.lpac_status or '',
        })
    return {'participants': rows}


# アプリ起動時にDB作成（ローカル開発用）
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
