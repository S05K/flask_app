from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_bcrypt import Bcrypt 
from flask_mail import Mail
import os
from dotenv import load_dotenv
from celery import Celery


# Initialize Flask extensions
app = Flask(__name__,template_folder='template')

load_dotenv()

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)

api = Api(app)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# For becrypt Password
bcrypt = Bcrypt(app)

# For initializing JWT Manager
jwt = JWTManager(app)


# Celery configuration (Broker and Backend)
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

# Initialize Celery
def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    # celery.conf.update(app.config)
    
    # Allow Celery tasks to use Flask application context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

celery = make_celery(app)


# Import your API routes here
from .routes import PlayerView




def create_app():
    return app
