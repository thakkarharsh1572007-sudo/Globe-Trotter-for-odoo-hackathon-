from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# 1. Initialize extensions first
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "123456"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # 2. Bind them to the app
    db.init_app(app)
    login_manager.init_app(app)
    
    # 3. Update this to 'auth.login' since login is inside the auth blueprint
    login_manager.login_view = 'auth.login' 
    login_manager.login_message_category = 'info'
    
    # 4. IMPORT HERE to avoid the circular import!
    from app.routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    return app