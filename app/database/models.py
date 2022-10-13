from sqlalchemy import Column, Integer, DECIMAL, Date, VARCHAR, Boolean 
from sqlalchemy.dialects.mysql import MEDIUMINT, TINYINT
from app.database.database import Base


class Camera(Base):
    __tablename__ = "cameras"

    idcameras = Column(Integer, primary_key=True, index=True)
    camera_url = Column(VARCHAR)
    ws_url = Column(VARCHAR)
    camera_name = Column(VARCHAR)
    camera_username = Column(VARCHAR)
    camera_password = Column(VARCHAR)

class Notification(Base):
    __tablename__ = "notifications"

    id_notification = Column(Integer, primary_key=True, index=True)
    image = Column(VARCHAR)
    create_at = Column(Date)
    confirmed = Column(Integer)
