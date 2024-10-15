from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from models import User, db
from sqlalchemy.exc import IntegrityError  

class VistaLogIn(Resource):
    
    def post(self):
            username = request.json["username"]
            password = request.json["password"]
            # Encontrar usario en la base de datos
            
            usuario = User.query.filter_by(username=username, password=password).first()
            
            if usuario:
                # Generar el token de acceso usando el id del usuario ya guardado
                token_de_acceso = create_access_token(identity=usuario.id)
                
                return {'mensaje':'Inicio de sesión exitoso', 'token_de_acceso':token_de_acceso}, 200
            else:
                return {'mensaje':'Nombre de usuario o contraseña incorrectos'}, 401
            
class VistaSignUp(Resource):
    
    def post(self):
        try:
            # Crear el nuevo usuario
            nuevo_usuario = User(
                username=request.json["username"],
                password=request.json["password"],
                email=request.json["email"]
            )
            
            # Agregar el nuevo usuario a la sesión
            db.session.add(nuevo_usuario)
            
            # Guardar los cambios en la base de datos (esto asigna el id al nuevo usuario)
            db.session.commit()
            
            # Generar el token de acceso (opcional, si deseas incluirlo)
            # token_de_acceso = create_access_token(identity=nuevo_usuario.id)
            
            return {'mensaje': 'Usuario creado exitosamente'}
        
        except IntegrityError:
            db.session.rollback()  # Deshacer la sesión en caso de error de integridad
            return {'mensaje': 'Nombre de usuario o correo ya existen'}, 400
        except Exception as e:
            db.session.rollback()  # Deshacer la sesión en caso de cualquier otro error
            return {'mensaje': 'Error al crear el usuario', 'error': str(e)}, 400
