from typing import Generic, TypeVar

from sqlmodel import Session, SQLModel, select

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    """
    Generic base repository providing CRUD operations.

    Type Parameters:
        T: SQLModel entity type
    """

    def __init__(self, session: Session, model_class: type[T]):
        """
        Initialize repository with database session and model class.

        Args:
            session: SQLModel database session
            model_class: The SQLModel entity class
        """
        self.session = session
        self.model_class = model_class

    def create(self, entity: T) -> T:
        """
        Create a new entity.

        Args:
            entity: The entity to create

        Returns:
            The created entity with ID
        """
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def read(self, entity_id: int) -> T | None:
        """
        Read an entity by ID.

        Args:
            entity_id: The entity ID

        Returns:
            The entity or None if not found
        """
        return self.session.get(self.model_class, entity_id)

    def read_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        """
        Read all entities with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of entities
        """
        statement = select(self.model_class).offset(skip).limit(limit)
        return self.session.exec(statement).all()

    def update(self, entity_id: int, entity_data: T) -> T | None:
        """
        Update an entity.

        Args:
            entity_id: The entity ID
            entity_data: Updated entity data

        Returns:
            The updated entity or None if not found
        """
        existing_entity = self.session.get(self.model_class, entity_id)
        if existing_entity is None:
            return None

        # Update fields from provided entity, excluding id
        update_data = entity_data.model_dump(exclude_unset=True, exclude={"id"})
        for key, value in update_data.items():
            setattr(existing_entity, key, value)

        self.session.add(existing_entity)
        self.session.commit()
        self.session.refresh(existing_entity)
        return existing_entity

    def delete(self, entity_id: int) -> bool:
        """
        Delete an entity.

        Args:
            entity_id: The entity ID

        Returns:
            True if deleted, False if not found
        """
        entity = self.session.get(self.model_class, entity_id)
        if entity is None:
            return False

        self.session.delete(entity)
        self.session.commit()
        return True
