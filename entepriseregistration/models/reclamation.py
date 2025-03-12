import sqlalchemy
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import  relationship
from typing import TypeVar, List, Iterable
from os import path
from datetime import datetime
from models.basic_base import Base
from models.base import BaseModel
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"
class Reclamation(BaseModel, Base):
    """BasePerson class"""
    __tablename__ = 'reclamation'

    type_reclamtion = Column(String(128), nullable=False)
    reclamation = Column(String(128), nullable=False)
    personne_id = Column(String(128), ForeignKey("personne.id")) # Foreign key

    personne = relationship("Personne", back_populates="reclamations")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       

