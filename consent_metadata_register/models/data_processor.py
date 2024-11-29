import sqlalchemy
from sqlalchemy import Column, String, DateTime, Integer,ForeignKey
from sqlalchemy.orm import relationship
from typing import TypeVar, List, Iterable
from os import path
from datetime import datetime
from models.basic_base import Base
from models.base import BaseModel
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"
from sqlalchemy import event
class DataProcessor(BaseModel, Base):
    __tablename__ = 'data_processor'
    data_process_name = Column(String(255), nullable=False)
    data_process_type = Column(String(255), nullable=False)
    data_controller_id = Column(String(255), ForeignKey('data_controller.id'), nullable=False)
    
    # Relationships
    data_controller = relationship(
        "DataController", back_populates="data_processors"
    )

	

@event.listens_for(DataProcessor, 'before_update')
def block_update(mapper, connection, target):
    raise Exception("Updating DataPurpose records is not allowed.")

@event.listens_for(DataProcessor, 'before_delete')
def block_delete(mapper, connection, target):
    raise Exception("Deleting DataPurpose records is not allowed.")
