from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_bcrypt import Bcrypt 

# Initialize Flask extensions
app = Flask(__name__)
api = Api(app)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# For becrypt Password
bcrypt = Bcrypt(app)

# For initializing JWT Manager
jwt = JWTManager(app)

# Import your API routes here
from .routes import PlayerView


def create_app():
    return app
