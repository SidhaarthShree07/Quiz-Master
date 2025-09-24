from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from .models import User, SessionLocal

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    # Debug: print incoming request data and headers
    print("[DEBUG] /login request headers:", dict(request.headers))
    print("[DEBUG] /login request data:", request.data)
    print("[DEBUG] /login request json:", request.json)
    data = request.json
    if not data:
        return jsonify({'message': 'No JSON body received'}), 400
    username = data.get('username')
    password = data.get('password')
    remember = data.get('remember')
    if not username or not password:
        return jsonify({'message': 'Username and password required'}), 400
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            print(f"[DEBUG] No user found for username: {username}")
            return jsonify({'message': 'Invalid username or password'}), 401
        if not check_password_hash(user.password, password):
            print(f"[DEBUG] Password mismatch for user: {username}")
            return jsonify({'message': 'Invalid username or password'}), 401
        if not remember:
            logout_user()  # This will clear any existing remember me cookie
        login_user(user, remember=remember)
        return jsonify({'message': 'Login successful', 'username': user.username, 'name': user.name, 'role': user.role.value}), 200
    finally:
        session.close()

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    return jsonify({'username': current_user.username, 'role': current_user.role.value, 'name': current_user.name}), 200

@auth_bp.route('/remembered', methods=['GET'])
@login_required
def remembered():
    # Try to check if login is via remember me (persistent cookie)
    # Flask-Login stores _fresh in session
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        is_fresh = session.get('_fresh', True)
        if not is_fresh:
            return jsonify({'remembered': True}), 200
    return jsonify({'remembered': False}), 401

@auth_bp.route('/force-remember-login', methods=['POST'])
def force_remember_login():
    from flask_login import logout_user, current_user
    logout_user()
    return jsonify({'message': 'Session cleared, please check dashboard for remember me login.'}), 200

@auth_bp.route('/logout-session-only', methods=['POST'])
def logout_session_only():
    from flask import session as flask_session, jsonify
    flask_session.clear()  # This clears the session cookie only
    return jsonify({'message': 'Session cleared, remember token remains.'}), 200