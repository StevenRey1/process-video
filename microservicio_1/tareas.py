from modelos import Video, db
from celery import Celery
from app import app
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips
import time
import os

def make_celery(app):
    celery = Celery(app.import_name, broker='redis://redis:6379/0')
    celery.conf.update(app.config)
    return celery

celery_app = make_celery(app)

@celery_app.task()
def procesar_video(video_id, url):
    with app.app_context():  # Usa el contexto de la aplicación para interactuar con la base de datos
        
        # Definir la ruta donde se guarda el video
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], url)
        
        # Cargar el video
        clip = VideoFileClip(video_path)
        
        # Recortar el video a 20 segundos
        clip = clip.subclip(0, min(20, clip.duration))  # Asegura que no se exceda la duración
        
        # Cargar la imagen que se quiere añadir
        image_path = 'static/img/drone.png'  # Cambia esto a la ruta real de tu imagen
        image_duration = 3  # Duración de la imagen al inicio y al final
        
        # Crear un clip de la imagen
        image_clip = ImageClip(image_path).set_duration(image_duration)
        
        # Concatenar la imagen al inicio y al final del video
        final_video = concatenate_videoclips([image_clip, clip, image_clip])
        
        # Actualizar el estado del video en la base de datos
        video = Video.query.get(video_id)
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{video.timeStamp}_processed.mp4')
        final_video.write_videofile(output_path, codec='libx264')
        video.status = 'processed'
        db.session.commit()
        
        
        # Liberar recursos
        clip.close()
        final_video.close()
