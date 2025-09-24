from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from .auth import auth_bp
from .routes.admin_routes import admin_bp
from .routes.user_routes import user_bp
from .models import create_db, SessionLocal, User, UserRole
from werkzeug.security import generate_password_hash
# Celery is now handled separately in celery_worker.py

def create_app():
    app = Flask(__name__)
    # Allow credentials and specify allowed origin for dev
    CORS(app, 
         supports_credentials=True, 
         origins=["http://localhost:5173"],  # Vite dev server
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"])

    # Config
    app.config['SECRET_KEY'] = 'your_secret_key_here'

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login'

    @login_manager.user_loader
    def load_user(user_id):
        session = SessionLocal()
        user = session.query(User).filter_by(id=user_id).first()
        session.close()
        return user

    # Ensure DB and tables are created
    create_db()

    # Ensure at least one teacher exists
    session = SessionLocal()
    try:
        teacher = session.query(User).filter_by(role=UserRole.TEACHER).first()
        if not teacher:
            user = User(
                id='Sidhaarth007',
                username='Sidhaarth007',
                password=generate_password_hash('sid*2004'),
                name='Sidhaarth',
                role=UserRole.TEACHER
            )
            session.add(user)
            session.commit()
    except Exception as e:
        session.rollback()
        print('Error creating default teacher:', e)
    finally:
        session.close()


    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    # Ensure CORS is applied to user_bp as well
    from flask_cors import CORS as BlueprintCORS
    BlueprintCORS(user_bp, supports_credentials=True, origins=["http://localhost:5173"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], allow_headers=["Content-Type", "Authorization", "X-Requested-With"])
    app.register_blueprint(user_bp, url_prefix='/api/user')

    # Celery is now handled separately in celery_worker.py

    return app