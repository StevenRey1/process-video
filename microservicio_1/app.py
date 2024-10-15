from flask import Flask
from flask_restful import Api
from vistas import VistaCargaVideos, VistaInformacionTarea
from flask_cors import CORS
from modelos import db
import os
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/fpv'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

# Obtener la ruta absoluta a la carpeta del proyecto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))  # Subir un nivel
app.config['UPLOAD_FOLDER'] = os.path.join(project_root, 'videos')  # Ruta a la carpeta 'videos'

# Clave secreta para firmar y validar los tokens JWT
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Mismo valor en ambos servicios
jwt = JWTManager(app)

# Crear la carpeta 'videos' si no existe
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

app_context = app.app_context()
app_context.push()

# Crear un bloque try-except para manejar errores al conectar a la base de datos
db.init_app(app)
db.create_all()

cors = CORS(app)
api = Api(app)
api.add_resource(VistaCargaVideos, '/tasks')
api.add_resource(VistaInformacionTarea, '/tasks/<int:tarea_id>')  # Update this line




