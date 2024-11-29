#!/usr/bin/env python3
import os
from sqlalchemy import asc, Column, String, DateTime, func, create_engine, Numeric, ForeignKey, Text, or_, and_
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, joinedload
from typing import Any, Dict, List, Optional, TypeVar, Union
from sqlalchemy.orm.exc import NoResultFound
from models.basic_base import Base
from models.base import BaseModel
from models.consent_attribut import ConsentAttribute
from models.data_controller import DataController
from models.data_provider import DataProvider
from models.permission_identity import PermissionIdentity
from models.data_processor import DataProcessor
from models.data_purpose import DataPurpose
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"
load_dotenv()
T = TypeVar('T')

class DBSManager():
    """interaacts with the MySQL database"""
    __engine = None
    __session = None

    def __init__(self):
        """Instantiate a DBStorage object"""
        self.__engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'.
                                            format(os.environ.get('USER'),
                                                   os.environ.get('PASSWORD'),
                                                   os.environ.get('DB_HOST', 'localhost'),
                                                   os.environ.get('DB'),                                                   
                                                   ), echo=True)
  
    def reload(self):
        """reloads data from the database"""
        Base.metadata.create_all(self.__engine)
        sess_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(sess_factory)
        self.__session = Session

    def new(self, obj)-> None :
        """add object to current session
        """
        self.__session.add(obj)

    def save(self):
        """commit current done work
        """
        self.__session.commit()
        
    
    @property
    def get_session(self):
        """
        getter function for W
        Returns weights
        """
        return self.__session

    def find_by(self, target_class: T,  **kwargs) -> Optional[T]:
        """
        Find a object by the given criteria
        Args:
            **kwargs: The criteria to search for
        Returns:
            T: The found object_t
        """

        try:
            object_t = self.__session.query(target_class).filter_by(**kwargs).first()
            if not object_t:
                raise NoResultFound("No object found")
            return object_t
        except NoResultFound:
            return None


    def find_all_by(self, target_class: T,  **kwargs) -> T:
        """
        Find a object by the given criteria
        Args:
            **kwargs: The criteria to search for
        Returns:
            T: The found object_t
        """

        try:
            object_t = self.__session.query(target_class).filter_by(**kwargs).all()
            if not object_t:
                raise NoResultFound("No object found")
            return object_t
        except NoResultFound:
            return []

    
    def find_all_with_join(self, prim_class: T, join_class: T , **kwargs) -> T:
        """
        Find a object by the given criteria
        Args:
            **kwargs: The criteria to search for
            prim_class: mother class,
            join_class: child class
        Returns:
            T: The found object_t
        """

        try:
            object_t = self.__session.query(prim_class).join(join_class).filter_by(**kwargs).all()
            if not object_t:
                raise NoResultFound("No object found")
            return object_t
        except NoResultFound:
            return []
        
    def find_all_with_joins(self, prim_class: T, join_class: T) -> T:
        """
        Join two classes without filtering
        Args:
            prim_class: mother class
            join_class: child class
        Returns:
            T: The joined object_t
        """

        try:
            object_t = self.__session.query(prim_class).join(join_class).order_by(asc(prim_class.created_at)).all()
            if not object_t:
                raise NoResultFound("No object found")
            return object_t
        except NoResultFound:
            return []
        
    def find_all_with__twow_class_join(self, prim_class: T, join_class: T, relationship_attr: str) -> T:
        """
        Find all objects with a simple join
        Args:
            prim_class: Mother class (Customer)
            join_class: Child class (Invoice)
            relationship_attr: Name of the relationship attribute in prim_class
        Returns:
            T: List of found objects
        """
        try:
            relationship_attr_obj = getattr(prim_class, relationship_attr)
            object_t = (
                self.__session.query(prim_class)
                .join(join_class)
                .options(joinedload(relationship_attr_obj))  # Use the actual attribute object
                .all()
            )
            if not object_t:
                raise NoResultFound("No object found")
            return object_t
        except NoResultFound:
            return []


    def get_sum_with_filter(
        self, 
        target_class: T,
        sum_param1: str,
        sum_param2: str = None,
        **kwargs:Dict[str, Any]
        ):
        
        """
        Calculate the sum based on the provided sum parameters and filter conditions.
    
        Args:
            target_class (type): The class representing the database table.
            sum_param1 (str, required): The first sum parameter attribute name.
            sum_param2 (str, optional): The second sum parameter attribute name. Defaults to None.
            **kwargs: Additional filter conditions as keyword arguments.

        Returns:
            int: The calculated sum based on the sum parameters and filter conditions.
        """
        
        if not hasattr(target_class, sum_param1) and not hasattr(target_class, sum_param2):
            raise AttributeError(f"{target_class.__name__} does not have attribute '{sum_param1}' or '{sum_param2}'.")
    
        if sum_param2 and not hasattr(target_class, sum_param2):
            raise AttributeError(f"{target_class.__name__} does not have attribute '{sum_param2}'.")
        if sum_param2:
            total_sum = self.__session.query(func.sum(getattr(target_class, sum_param1) * getattr(target_class, sum_param2))).filter_by(**kwargs).scalar()
        else:
            total_sum = self.__session.query(func.sum(getattr(target_class, sum_param1))).filter_by(**kwargs).scalar()
        return total_sum
    
    def update_object(self, target_class: T, value : str, **kwargs) -> None:
        """
        Update the given object
        Args:
            value (string): The id or another attribut of the class to update
            **kwargs: The fields to update
            target_class: the class over the update is made

        Returns:
            None
        """
        try:
            current_object = self.find_by(target_class, id = value)
            for key, value in kwargs.items():
                if hasattr(current_object, key):
                    setattr(current_object, key, value)
                else:
                    raise ValueError(f"{target_class.__name__} does not have attribute {key}")
            self.__session.commit()
        except (NoResultFound, ValueError):
            raise NoResultFound(f"No {target_class.__name__} found with id {id}")

    def get_all(self, target_class: T) -> T:
        """query on the current database session"""
        #session.query(Patient).filter(Patient.is_deleted == False).all()
        objs = self.__session.query(target_class).filter(target_class.is_deleted == False).order_by(asc(target_class.created_at)).all()

        #objs = self.__session.query(target_class).filter(target_class.is_deleted == False).all()
        return objs


    def delete(self, target_obj: T):
        """delete from the current database session obj if not None
        Args
            target_object (current_object type): object that is implied in delete operation
        Return
            None if object is None else current_object
        """
        if target_obj is not None:
            self.__session.delete(target_obj)
    
    def get_room_with_date_interval(
        self,
        target_class: T,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime]
    ) -> list[T]:
        if isinstance(start_date, str):
            start_date = convert_to_timestamp(start_date)
        if isinstance(end_date, str):
            end_date = convert_to_timestamp(end_date)

        try:
            results = self.__session.query(target_class).filter(
            or_(
                and_(target_class.start_date >= start_date, target_class.start_date < end_date),
                and_(target_class.end_date > start_date, target_class.end_date <= end_date),
                and_(target_class.start_date <= start_date, target_class.end_date >= end_date),
                and_(target_class.start_date <= start_date, target_class.end_date >= end_date, target_class.start_date >= start_date, target_class.end_date <= end_date)
                )
        ).order_by(asc(target_class.created_at)).all()
           
            return results
        except NoResultFound:
            return []

    def close(self)-> None :
        """call remove() method on the private session attribute"""
        self.__session.remove()
    
    def get_curent_occupied_room(
            self,
            target_class: T,
            current_date: date,
            order_by: str = 'asc',
            date_attribute: str = "created_at"
    ) -> List[T]:
        # Specify order based on the 'order_by' parameter
        order_clause = getattr(target_class.created_at, order_by)()

        # Query for rows created on the current date and is_deleted=False
        query_result = self.__session.query(target_class).filter(
            getattr(target_class, date_attribute) >= current_date,
            getattr(target_class, date_attribute) < current_date + timedelta(days=1),
            target_class.is_deleted == False
        ).order_by(order_clause).all()

        return query_result

    def get_curent_occupieds_room(
            self,
            target_class: T,
            order_by: str = 'asc',
            **kwargs: Dict[str, Any],
    ) -> List[T]:
        # Specify order based on the 'order_by' parameter
        order_clause = getattr(target_class, order_by)()

        filter_criteria = {
            getattr(target_class, key): getattr(target_class, value) if isinstance(value, str) else value
            for key, value in kwargs.items()
        }

        # Check if either 'created_at' or 'ended_at' is provided in kwargs
        attribute_name = next((key for key in {'created_at', 'updated_at', 'end_date', 'start_date'} if key in kwargs), None)

        # Construct filter criteria based on the provided kwargs
        if attribute_name:
            filter_criteria.update({
                getattr(target_class, attribute_name) >= datetime.utcnow().date(),
                getattr(target_class, attribute_name) < datetime.utcnow().date() + timedelta(days=1),
            })

        
        
        

        # Query for rows based on filter criteria
        query_result = self.__session.query(target_class).filter(**filter_criteria.values()).order_by(order_clause).all()

        return query_result
    
    
    
    def get_sum_with_filter_and_interval(
        self, 
        target_class: T,
        start_date: datetime,
        end_date: datetime,
        sum_param1: str,
        sum_param2: str = None,
        **kwargs: Dict[str, Any],
        ) -> Any:
        """
        Calculate the sum based on the provided sum parameters and filter conditions.
    
        Args:
            target_class (Type[YourClass]): The class representing the database table.
            sum_param1 (str, required): The first sum parameter attribute name.
            sum_param2 (str, optional): The second sum parameter attribute name. Defaults to None.
            start_date (datetime, optional): The start of the day for date_column filtering.
            end_date (datetime, optional): The current date and time for date_column filtering.
            **kwargs: Additional filter conditions as keyword arguments.

        Returns:
            Any: The calculated sum based on the sum parameters and filter conditions.
        """
        if not hasattr(target_class, sum_param1) or (sum_param2 and not hasattr(target_class, sum_param2)):
            raise AttributeError(f"{target_class.__name__} does not have attribute '{sum_param1}' or '{sum_param2}'.")

        query_params = [getattr(target_class, sum_param1)]
        if sum_param2:
            query_params.append(getattr(target_class, sum_param2))

        query = self.__session.query(func.sum(*query_params))

        # Add date_column filtering conditions
        if start_date and end_date:
            query = query.filter(
                target_class.created_at >= start_date,
                target_class.created_at <= end_date
            )

        # Add additional filter conditions
        query = query.filter_by(**kwargs)

        total_sum = query.scalar()
        return total_sum
    
    
    def get_object_by_date_interval_and_filter(
        self,
        target_class: T,
        start_date: datetime,
        end_date: datetime,
        order_by: str = 'created_at',
        **kwargs: Dict[str, Any]
    ) -> List:
        """
        Get settlements objects by interval and filter.

        Parameters:
        - target_class (Type): The class of the target object.
        - start_date (datetime): The start date of the interval.
        - end_date (datetime): The end date of the interval.
        - order_by (str): The field to order the results by (default: 'created_at').
        - kwargs (Dict[str, Any]): Additional filters.

        Returns:
        - List: A list of SQLAlchemy objects.
        """
        order_clause = getattr(target_class, order_by)
        
        conditions = [
            target_class.created_at >= start_date  if start_date is not None else True,
            target_class.created_at <= end_date
        ]
        
        if target_class == Invoice:
            conditions.append(target_class.invoice_amount > 0)
        
        #conditions = [
            #or_(
                #and_(target_class.created_at >= start_date, target_class.created_at < end_date),
                #and_(target_class.created_at > start_date, target_class.created_at <= end_date),
                #and_(target_class.created_at <= start_date, target_class.created_at >= end_date),
                #and_(target_class.created_at <= start_date, target_class.created_at >= end_date, target_class.created_at >= start_date, target_class.created_at <= end_date)
                #)
        #]
        
        
        for key, value in kwargs.items():
            conditions.append(getattr(target_class, key) == value)

        query_result = (
            self.__session.query(target_class)
            .filter(and_(*conditions))
            .order_by(order_clause)
            .all()
        )
        return query_result
    
    def get_object_by_date_interval_and_filters(
        self,
        target_class: T,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        **additional_filters
    ) -> List[T]:
        if isinstance(start_date, str):
            start_date = convert_to_timestamp(start_date)
        if isinstance(end_date, str):
            end_date = convert_to_timestamp(end_date)

        try:
            filter_conditions = [
                or_(
                    and_(target_class.start_date >= start_date, target_class.start_date < end_date),
                    and_(target_class.end_date > start_date, target_class.end_date <= end_date),
                    and_(target_class.start_date <= start_date, target_class.end_date >= end_date),
                    and_(target_class.start_date <= start_date, target_class.end_date >= end_date, target_class.start_date >= start_date, target_class.end_date <= end_date)
                )
            ]

            for key, value in additional_filters.items():
                filter_conditions.append(getattr(target_class, key) == value)

            results = self.__session.query(target_class).filter(
                *filter_conditions
            ).order_by(asc(target_class.created_at)).all()

            return results
        except NoResultFound:
            return []
        
        
    
    def get_objects_with_positive_attribute(
        self,
        target_class: T,
        attribute: Any,
        **filter
    ) -> List:
        """
        Get objects with a specified attribute greater than 0.

        Parameters:
        - target_class (Type): The class of the target object.
        - attribute (Any): The attribute to filter on.

        Returns:
        - List: A list of SQLAlchemy objects.
        """
        query_result = (
            self.__session.query(target_class)
            .filter(getattr(target_class, attribute) > 0)
            .filter_by(**filter)
            .all()
        )
        return query_result

def convert_to_timestamp(date_str: str) -> Union[None, datetime]:
    try:
        return datetime.strptime(date_str, TIMESTAMP_FORMAT)
    except ValueError:
        return None
    
    """
    
    def get_object_by_date_interval_and_filter(
        self,
        target_class: T,
        start_date: datetime,
        end_date: datetime,
        order_by: str = 'created_at',
        **kwargs: Dict[str, Any]
    ) -> List:
        
        #Get settlements objects by interval and filter.

        #Parameters:
        #- target_class (Type): The class of the target object.
        #- start_date (datetime): The start date of the interval.
        #- end_date (datetime): The end date of the interval.
        #- order_by (str): The field to order the results by (default: 'created_at').
        #- kwargs (Dict[str, Any]): Additional filters.

        #Returns:
        #- List: A list of SQLAlchemy objects.
        
        order_clause = getattr(target_class, order_by)
        
        conditions = [
            target_class.created_at >= start_date  if start_date is not None else True,
            target_class.created_at <= end_date
        ]
        
        for key, value in kwargs.items():
            conditions.append(getattr(target_class, key) == value)

        query_result = (
            self.__session.query(target_class)
            .filter(and_(*conditions))
            .order_by(order_clause)
            .all()
        )
        return query_result  

    """
