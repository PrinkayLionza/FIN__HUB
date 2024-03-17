from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()
DB_NAME = "finhub_db.db"

UPLOAD_FOLDER = '/static/uploads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'f874c887-66a5-401f-a7ec-1771f2d85050'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .admin import admin

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/')

    from .models import User
    from werkzeug.security import generate_password_hash

    with app.app_context():

        db.create_all()
        admin_email = "admin@finhub.com"
        password = generate_password_hash(
            "admin@123", method='pbkdf2:sha256')

        check_admin = User.query.filter_by(email=admin_email).first()

        if check_admin == None:
            admin_logins = User(
                email=admin_email,
                password=password,
                is_admin=True,
                first_name="Admin",
            )
            db.session.add(admin_logins)
            db.session.commit()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
