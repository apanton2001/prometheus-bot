from datetime import datetime
from typing import Any, Dict
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class BaseModel(Base):
    """
    Base model class with common functionality for all database models.
    """
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default={})
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the model
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    @classmethod
    def create(cls, session: sessionmaker, **kwargs) -> 'BaseModel':
        """
        Create a new model instance.
        
        Args:
            session (sessionmaker): Database session
            **kwargs: Model attributes
            
        Returns:
            BaseModel: Created model instance
        """
        instance = cls(**kwargs)
        session.add(instance)
        session.commit()
        return instance
    
    @classmethod
    def get_by_id(cls, session: sessionmaker, id: int) -> 'BaseModel':
        """
        Get model instance by ID.
        
        Args:
            session (sessionmaker): Database session
            id (int): Model ID
            
        Returns:
            BaseModel: Model instance if found, None otherwise
        """
        return session.query(cls).filter(cls.id == id).first()
    
    @classmethod
    def get_all(cls, session: sessionmaker) -> list['BaseModel']:
        """
        Get all model instances.
        
        Args:
            session (sessionmaker): Database session
            
        Returns:
            list[BaseModel]: List of all model instances
        """
        return session.query(cls).all()
    
    def update(self, session: sessionmaker, **kwargs) -> None:
        """
        Update model instance attributes.
        
        Args:
            session (sessionmaker): Database session
            **kwargs: Attributes to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        session.commit()
    
    def delete(self, session: sessionmaker) -> None:
        """
        Delete model instance.
        
        Args:
            session (sessionmaker): Database session
        """
        session.delete(self)
        session.commit()
    
    @classmethod
    def bulk_create(cls, session: sessionmaker, instances: list['BaseModel']) -> list['BaseModel']:
        """
        Create multiple model instances.
        
        Args:
            session (sessionmaker): Database session
            instances (list[BaseModel]): List of model instances to create
            
        Returns:
            list[BaseModel]: List of created model instances
        """
        session.bulk_save_objects(instances)
        session.commit()
        return instances
    
    @classmethod
    def bulk_update(cls, session: sessionmaker, instances: list['BaseModel'], **kwargs) -> None:
        """
        Update multiple model instances.
        
        Args:
            session (sessionmaker): Database session
            instances (list[BaseModel]): List of model instances to update
            **kwargs: Attributes to update
        """
        for instance in instances:
            instance.update(session, **kwargs)
    
    @classmethod
    def bulk_delete(cls, session: sessionmaker, instances: list['BaseModel']) -> None:
        """
        Delete multiple model instances.
        
        Args:
            session (sessionmaker): Database session
            instances (list[BaseModel]): List of model instances to delete
        """
        for instance in instances:
            instance.delete(session) 