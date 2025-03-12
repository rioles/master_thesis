#!/usr/bin/env python
import sqlalchemy
from os import getenv
from sqlalchemy import Column, String, DateTime, Boolean
import uuid
from typing import TypeVar, List, Iterable
from os import path
from datetime import datetime
from decimal import Decimal
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"
import models


class BaseModel:
    
    """BaseModel class"""

    id = Column(String(60), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    def __init__(self, *args: list, **kwargs: dict) -> None:
        """Initialization of the base model"""
        if kwargs:
            self.id = str(uuid.uuid4())
            for key, value in kwargs.items():
                if key != "__class__":
                    self.__dict__[key] = value
                if kwargs.get("created_at", None) and type(self.created_at) is str:
                    self.created_at = datetime.strptime(kwargs["created_at"], TIMESTAMP_FORMAT)
                else:
                    self.created_at = datetime.utcnow()

                if kwargs.get("updated_at", None) and type(self.updated_at) is str:
                    self.updated_at = datetime.strptime(kwargs["updated_at"], TIMESTAMP_FORMAT)
                else:
                    self.updated_at = datetime.utcnow()
        else:
            self.id = str(uuid.uuid4())
            self.created_at = datetime.utcnow()
            self.updated_at = self.created_at

    def __str__(self)-> str:
        classe_name = self.__class__.__name__
        return f"[{classe_name}] ({self.id}) {self.__dict__}"
    
    def convert_decimal_to_float(self, value):
        if isinstance(value, Decimal):
            return float(value)
        return value

    def to_dict(self):
        """creates dictionary of the class  and returns
        Return:
            returns a dictionary of all the key values in __dict__
        """
        my_dict = dict(self.__dict__)
        
        my_dict["__class__"] = str(type(self).__name__)
        my_dict["created_at"] = self.created_at.isoformat()
        my_dict["updated_at"] = self.updated_at.isoformat()
        
        if "start_date" in my_dict:
            my_dict["start_date"] = self.start_date.isoformat()
            
        if "end_date" in my_dict:
            my_dict["end_date"] = self.end_date.isoformat()
            
        if "date_of_birth" in my_dict and my_dict["date_of_birth"] is not None:
            if isinstance(self.date_of_birth, datetime):
                my_dict["date_of_birth"] = self.date_of_birth.isoformat()
        
        if "date_of_birth" in my_dict and my_dict["date_of_birth"] is None:
            my_dict["date_of_birth"] = datetime.utcnow()    
        
        # Convert Decimal values to float
        my_dict = {
            k: self.convert_decimal_to_float(v) for k, v in my_dict.items()
        }

        # Remove keys that start with an uppercase letter
        my_dict = {
            k: v for k, v in my_dict.items() if not k[0].isupper()
        }
        
        if "_sa_instance_state" in my_dict:
            del my_dict["_sa_instance_state"]
        return my_dict
    
    def save(self) -> None:
        self.updated_at = datetime.utcnow()
        models.storage.new(self)
        models.storage.save()
    
    def delete(self):
        """delete the current instance from the storage"""
        models.storage.delete(self)
       

if __name__=="__main__":
    my_model = BaseModel()
    my_model.name = "My First Model"
    my_model.my_number = 89
    print(my_model)
    #dico = my_model.new(my_model)
    print(my_model.__str__())
