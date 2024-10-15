from flask import request
from flask_restful import Resource
import os
from moviepy.editor import VideoFileClip
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime

class VistaCargaVideos(Resource):
    @jwt_required()
    def post(self):
        from tareas import procesar_video  # Importa aquí para evitar ciclos
        from app import app
        from modelos import db, Video
        
        # Lógica de recuperación de tareas del usuario autenticado
        user_id = get_jwt_identity()
        print(user_id)

        # Verificamos que el archivo exista
        if 'file' not in request.files:
            return {'mensaje': 'No se ha enviado el archivo'}, 400
        
        archivo = request.files['file']
        
        # Crear un nombre único usando el timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

       # Extraer la extensión del archivo original
        _, extension = os.path.splitext(archivo.filename)
        
        # Crear el nombre del video solo con el timestamp y la extensión
        nombre_video = f"{timestamp}{extension}"  # por ejemplo, "20231014123456.mp4"

        # Guardamos el archivo en el directorio de videos
        ruta_video = os.path.join(app.config['UPLOAD_FOLDER'], nombre_video)
        archivo.save(ruta_video)  # Guardamos el archivo

        try:
            # Usamos un bloque 'with' para manejar automáticamente el cierre de VideoFileClip
            with VideoFileClip(ruta_video) as clip:
                duracion = clip.duration

                # Verificamos la duración del video
                if duracion < 5 or duracion > 60:
                    os.remove(ruta_video)  # Eliminamos el archivo si no cumple con la duración
                    return {'mensaje': 'El video debe durar al menos 5 segundos y no más de 60'}, 400

        except Exception as e:
            # Eliminamos el archivo si no es válido
            os.remove(ruta_video)
            return {'mensaje': 'El archivo no es un video válido', 'error': str(e)}, 400

        # Lanzamos la tarea de guardar el video en la base de datos
        nuevo_video = Video(user_id = user_id, status='uploaded', timeStamp = timestamp)
        db.session.add(nuevo_video)
        db.session.commit()

        # Retornamos la respuesta al usuario antes de procesar el video
        response = {'mensaje': 'Video cargado con éxito', 'tarea_id': nuevo_video.id}

        # Procesamos el video en segundo plano
        procesar_video.delay(nuevo_video.id, ruta_video)

        return response, 200
    
    
    @jwt_required()
    def get(self):
        from modelos import Video,VideoSchema
        
        # Lógica de recuperación de tareas del usuario autenticado
        user_id = get_jwt_identity()
     
        # Obtener parámetros opcionales de la consulta
        max_resultados = request.args.get('max', default=None, type=int)
        order = request.args.get('order', default=1, type=int)  # 0 para ascendente, 1 para descendente

        # Consultar las tareas de edición del usuario autenticado
        query = Video.query.filter_by(user_id=user_id)

        # Ordenar los resultados según el parámetro 'order'
        if order == 0:
            query = query.order_by(Video.id.asc())  # Orden ascendente
        else:
            query = query.order_by(Video.id.desc())  # Orden descendente

        # Limitar la cantidad de resultados según el parámetro 'max'
        if max_resultados:
            query = query.limit(max_resultados)

        # Ejecutar la consulta
        videos = query.all()

        # Serializar los resultados
        video_schema = VideoSchema(many=True)
        return video_schema.dump(videos), 200
    
    
    
class VistaInformacionTarea(Resource):
    @jwt_required()
    def get(self, tarea_id):
        from modelos import Video, VideoSchema
        from app import app
        
        # Lógica de recuperación de tareas del usuario autenticado
        user_id = get_jwt_identity()
        
        # Consultar la tarea de edición del usuario autenticado
        video = Video.query.filter_by(id=tarea_id, user_id=user_id).first()

        if not video:
            return {'mensaje': 'La tarea no existe o no pertenece al usuario autenticado'}, 404
        
        
        #  Inicializar la ruta como None por defecto
        video.ruta = None

        # Buscar en el directorio de videos el archivo que contiene en su nombre el mismo timestamp que el video
        if video.status == 'processed':
            for archivo in os.listdir(app.config['UPLOAD_FOLDER']):
                if video.timeStamp in archivo and 'processed' in archivo:
                    # Construir la ruta completa del archivo
                    video.ruta = os.path.join(app.config['UPLOAD_FOLDER'], archivo)
                    break
       
            
            
        

        # Serializar el resultado
        video_schema = VideoSchema()

        # Serialize the video including the added 'ruta'
        return video_schema.dump(video), 200