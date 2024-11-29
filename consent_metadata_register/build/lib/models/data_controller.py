import sqlalchemy
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from typing import TypeVar, List, Iterable
from sqlalchemy.orm import relationship
from os import path
from datetime import datetime
from models.basic_base import Base
from models.base import BaseModel
from sqlalchemy import event
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"
class DataController(BaseModel, Base):
    __tablename__ = 'data_controller'
    data_controller_name = Column(String(255), nullable=False)
    data_controller_type = Column(String(255), nullable=False)
    permission_identities = relationship('PermissionIdentity', back_populates='data_controller')
    data_processors = relationship("DataProcessor", back_populates="data_controller")
    permission_identities = relationship(
        'PermissionIdentity', back_populates='data_controller'
    )
    
    

    	
@event.listens_for(DataController, 'before_update')
def block_update(mapper, connection, target):
    raise Exception("Updating DataPurpose records is not allowed.")

@event.listens_for(DataController, 'before_delete')
def block_delete(mapper, connection, target):
    raise Exception("Deleting DataPurpose records is not allowed.")
