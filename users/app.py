from flask import Flask
from flask_restful import Api
from vistas import VistaSignUp, VistaLogIn
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models import db


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Mismo valor en ambos servicios
app.config['PROPAGATE_EXCEPTIONS'] = True
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()
cors=CORS(app)

api = Api(app)

api.add_resource(VistaSignUp, '/signup')
api.add_resource(VistaLogIn, '/login')

jwt = JWTManager(app)

    
    
    