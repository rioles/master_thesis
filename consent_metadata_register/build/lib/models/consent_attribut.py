import sqlalchemy
from sqlalchemy import Column, String, DateTime, Integer, Boolean
from sqlalchemy.orm import relationship
from typing import TypeVar, List, Iterable
from os import path
from datetime import datetime
from models.basic_base import Base
from models.base import BaseModel
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"
from sqlalchemy import event


class ConsentAttribute(BaseModel, Base):
    __tablename__ = 'consent_attribute'
    contains_personal_data = Column(Boolean, nullable=False)
    data_attribute = Column(String(255), nullable=False)
    data_purpose = relationship("DataPurpose", back_populates="consent_attribute")
    #data_purpose = relationship("DataPurpose", back_populates="consent_attribute")

    

@event.listens_for(ConsentAttribute, 'before_update')
def block_update(mapper, connection, target):
    raise Exception("Updating DataPurpose records is not allowed.")

@event.listens_for(ConsentAttribute, 'before_delete')
def block_delete(mapper, connection, target):
    raise Exception("Deleting DataPurpose records is not allowed.")
