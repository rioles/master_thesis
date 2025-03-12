import sqlalchemy
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import  relationship
from typing import TypeVar, List, Iterable
from os import path
from datetime import datetime
from models.basic_base import Base
from models.base import BaseModel
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"
class Personne(BaseModel, Base):
    """BasePerson class"""
    __tablename__ = 'personne'

    nom = Column(String(128), nullable=False)
    prenom = Column(String(128), nullable=False)
    address = Column(String(128), nullable=False)
    telphone = Column(String(128), nullable=False)
    reclamations = relationship("Reclamation", back_populates="personne")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       

