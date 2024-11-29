import sqlalchemy
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from typing import TypeVar, List, Iterable
from sqlalchemy.orm import relationship
from os import path
from datetime import datetime
from models.basic_base import Base
from models.base import BaseModel
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"
from sqlalchemy import event
class PermissionIdentity(BaseModel, Base):
    __tablename__ = 'permission_identity'

    id_data_subject = Column(String(255), nullable=False)
    erase = Column(Boolean, nullable=False)
    is_delete = Column(Boolean, nullable=False)
    beginning_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    consent_date = Column(DateTime, nullable=False)

    data_provider_id = Column(String(255), ForeignKey('data_provider.id'), nullable=False)
    data_controller_id = Column(String(255), ForeignKey('data_controller.id'), nullable=False)

    consent_attribute_id = Column(String(255), ForeignKey('consent_attribute.id'), nullable=False)
    data_controller = relationship('DataController', back_populates='permission_identities')
    data_provider   = relationship('DataProvider', back_populates='permission_identities')
   
    
@event.listens_for(PermissionIdentity, 'before_update')
def block_update(mapper, connection, target):
    raise Exception("Updating DataPurpose records is not allowed.")

@event.listens_for(PermissionIdentity, 'before_delete')
def block_delete(mapper, connection, target):
    raise Exception("Deleting DataPurpose records is not allowed.")
