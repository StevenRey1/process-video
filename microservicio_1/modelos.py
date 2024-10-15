from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
import datetime

db = SQLAlchemy() 

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timeStamp = db.Column(db.String(64))
    status = db.Column(db.String(64) )
    user_id = db.Column(db.Integer)
    
class VideoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Video
        load_instance = True
    
    ruta = fields.String()



        