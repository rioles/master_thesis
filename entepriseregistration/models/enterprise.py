import sqlalchemy
from sqlalchemy import Column, String, DateTime, Integer
from typing import TypeVar, List, Iterable
from os import path
from datetime import datetime
from models.basic_base import Base
from models.base import BaseModel
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"
class Enterprise(BaseModel, Base):
    """BasePerson class"""
    __tablename__ = 'person'

    enterprise_name = Column(String(128), nullable=False)
    client_id = Column(String(128), nullable=False)
    client_secret = Column(String(128), nullable=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       

