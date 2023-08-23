from sqlalchemy import Column, Integer, DECIMAL, Date, VARCHAR, Boolean
from sqlalchemy.dialects.mysql import MEDIUMINT, TINYINT
from app.database.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(VARCHAR)
    password = Column(VARCHAR)
    full_name = Column(VARCHAR)
    role = Column(VARCHAR)
    create_at = Column(Date)


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(VARCHAR)


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

<<<<<<< HEAD

class Video(Base):
    __tablename__ = "videos"

    idvideos = Column(Integer, primary_key=True, index=True)
    video_path = Column(VARCHAR)
    video_detection_path = Column(VARCHAR)
=======
class Video(Base):
    __tablename__ = "videos"

    id_video = Column(Integer, primary_key=True, index=True)
    image_path = Column(VARCHAR)
    video_path = Column(VARCHAR)
>>>>>>> main
    create_at = Column(Date)
