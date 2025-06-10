
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from models import db, Participant

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/user1_dashboard', methods=['GET', 'POST'])
@login_required
def user1_dashboard():
    if request.method == 'POST':
        participant = Participant.query.filter_by(name=request.form.get('name'), user_id=current_user.id).first()
        if not participant:
            participant = Participant(user_id=current_user.id)
            db.session.add(participant)
        participant.name = request.form.get('name')
        participant.email = request.form.get('email')
        participant.position = request.form.get('position')
        participant.questions = request.form.get('questions')
        participant.agm_status = request.form.get('agm_status')
        db.session.commit()
        return redirect(url_for('user1_dashboard'))

    participants = Participant.query.filter_by(user_id=current_user.id).all()
    return render_template('user1_dashboard.html', username=current_user.username, participants=participants)

@app.route('/user2_dashboard', methods=['GET', 'POST'])
@login_required
def user2_dashboard():
    if request.method == 'POST':
        participant = Participant.query.filter_by(name=request.form.get('name'), user_id=current_user.id).first()
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
    app.run(debug=True)
