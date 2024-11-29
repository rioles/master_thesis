import sqlalchemy
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from typing import TypeVar, List, Iterable
from os import path
from datetime import datetime
from models.basic_base import Base
from models.base import BaseModel
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"
from sqlalchemy import event

class DataPurpose(BaseModel, Base):
    __tablename__ = 'data_purpose'
    purpose_description = Column(String(255), nullable=True)
    purpose_basic_specification = Column(String(255), nullable=False)
    data_processing_activity = Column(String(255), nullable=True)
    consent_attribute_id = Column(String(255), ForeignKey('consent_attribute.id'), nullable=False)
    consent_attribute = relationship("ConsentAttribute", back_populates="data_purpose")
    
    
    
@event.listens_for(DataPurpose, 'before_update')
def block_update(mapper, connection, target):
    raise Exception("Updating DataPurpose records is not allowed.")

@event.listens_for(DataPurpose, 'before_delete')
def block_delete(mapper, connection, target):
    raise Exception("Deleting DataPurpose records is not allowed.")
