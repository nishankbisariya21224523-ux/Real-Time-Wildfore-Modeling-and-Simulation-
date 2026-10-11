"""Base repository defining standard database access patterns."""

from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Generic base repository providing CRUD primitives."""

    def __init__(self, db: Session, model_cls: Type[ModelType]):
        self.db = db
        self.model_cls = model_cls

    def get_by_id(self, id_val: Any) -> Optional[ModelType]:
        return self.db.query(self.model_cls).filter(self.model_cls.id == id_val).first()

    def add(self, entity: ModelType) -> ModelType:
        self.db.add(entity)
        self.db.flush()
        return entity

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
