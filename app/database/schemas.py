from datetime import date, datetime
from decimal import Decimal
import time
from typing import Optional
from pydantic import BaseModel, validator


class LoginSchema(BaseModel):
    username: str
    password: str
    class Config:
        orm_mode = True


class UserSchema(BaseModel):
    username: str
    password: str
    full_name: str
    role: str
    create_at: datetime
    class Config:
        orm_mode = True


class RoleSchema(BaseModel):
    role_name: str
    class Config:
        orm_mode = True


class CameraSchema(BaseModel):
    camera_url: str
    ws_url: Optional[str]
    camera_name: str
    camera_username: str
    camera_password: str
    class Config:
        orm_mode = True


class NotificationSchema(BaseModel):
    image: str
    create_at: datetime
    confirmed: Optional[int]
    id_notification: int

    class Config:
        orm_mode = True
