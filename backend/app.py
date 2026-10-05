import os
from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mailman import Mail
from flask_caching import Cache
from celery import Celery
from dotenv import load_dotenv
import jwt
import click

# Load variables from .env file
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
jwt_manager = JWTManager()
mail = Mail()
cache = Cache()


def make_dynamic_cache_key(*args, **kwargs):
    path = request.path
    query_params = request.query_string.decode('utf-8')

    auth_header = request.headers.get('Authorization', '')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ', 1)[1].strip()
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = str(payload.get('sub') or payload.get('user_id') or 'anonymous')
            role = payload.get('role') or (g.current_user.role if getattr(g, 'current_user', None) else 'user')
            cache_type = "user"
            return f"{cache_type}:{role}:{user_id}:{path}:{query_params}"
        except Exception:
            pass

    cache_type = "public"
    return f"{cache_type}:public:anonymous:{path}:{query_params}"


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    )
    celery_keys = {k.lower(): v for k, v in app.config.items() if k.islower()}
    celery.conf.update(celery_keys)
    # celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app(config=None):
    app = Flask(__name__)

    basedir = os.path.abspath(os.path.dirname(__file__))
    db_name = os.environ.get('DB_NAME', 'default.db')

    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY'),
        JWT_ACCESS_TOKEN_EXPIRES=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES')),
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{os.path.join(basedir, db_name)}',
        SQLALCHEMY_TRACK_MODIFICATIONS=os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS') == 'True',
        CELERY_BROKER_URL=os.environ.get('CELERY_BROKER_URL'),
        CELERY_RESULT_BACKEND=os.environ.get('CELERY_RESULT_BACKEND'),
        REDIS_URL=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
        CACHE_TYPE=os.environ.get('CACHE_TYPE', 'RedisCache'),
        CACHE_REDIS_URL=os.environ.get('CACHE_REDIS_URL', 'redis://localhost:6379/0'),
        CACHE_DEFAULT_TIMEOUT=int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300)),
        # Mail config
        MAIL_SERVER=os.environ.get('MAIL_SERVER'),
        MAIL_PORT=int(os.environ.get('MAIL_PORT', 587)),
        MAIL_USE_TLS=os.environ.get('MAIL_USE_TLS') == 'True',
        MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
        MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
        MAIL_DEFAULT_SENDER=os.environ.get('MAIL_DEFAULT_SENDER'), 
    )

    if config:
        app.config.update(config)

    # CORS — allow frontend on port 8081
    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://localhost:8081", "http://127.0.0.1:8081"]}},
        supports_credentials=True,
    )

    db.init_app(app)
    migrate.init_app(app, db)
    jwt_manager.init_app(app)
    mail.init_app(app)

    try:
        cache.init_app(app)
    except Exception:
        app.config['CACHE_TYPE'] = 'SimpleCache'
        cache.init_app(app)

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.admin_routes import admin_bp
    from routes.staff_routes import staff_bp
    from routes.user_routes import user_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(staff_bp, url_prefix='/api/staff')
    app.register_blueprint(user_bp, url_prefix='/api/user')


    from models import User

    @app.cli.command("create-admin")
    @click.option("--username", prompt=True, help="Administrator username")
    @click.option("--full_name", prompt=True, help="Administrator full name")
    @click.option("--email", prompt=True, help="Administrator email address")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Administrator password")
    def create_admin(username, full_name, email, password):
        """Creates a new administrator user."""
        # Check if the user already exists
        if User.query.filter_by(username=username).first():
            click.echo("Error: A user with this username already exists.")
            return
        if User.query.filter_by(email=email).first():
            click.echo("Error: A user with this email already exists.")
            return

        admin_user = User(
            username=username,
            full_name=full_name, 
            email=email,
            role='admin',
            is_active=True
        )

        try:
            admin_user.set_password(password)
            db.session.add(admin_user)
            db.session.commit()
            click.echo(f"Success: Administrator '{username}' created successfully!")
        except Exception as e:
            db.session.rollback()
            click.echo(f"Error creating admin: {e}")

    return app