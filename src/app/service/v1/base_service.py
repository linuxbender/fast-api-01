from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlmodel import SQLModel

from app.data.v1.base_repository import BaseRepository

T = TypeVar("T", bound=SQLModel)  # Entity type
D = TypeVar("D", bound=BaseModel)  # DTO type


class BaseService(Generic[T, D]):
    """
    Generic base service providing CRUD operations with DTO mapping.

    Type Parameters:
        T: SQLModel entity type
        D: Pydantic DTO type
    """

    def __init__(
        self,
        repository: BaseRepository[T],
        entity_class: type[T],
        dto_class: type[D],
    ):
        """
        Initialize service with repository and model classes.

        Args:
            repository: The repository instance
            entity_class: The SQLModel entity class
            dto_class: The Pydantic DTO class
        """
        self.repository = repository
        self.entity_class = entity_class
        self.dto_class = dto_class

    def dto_to_entity(self, dto: D) -> T:
        """
        Convert DTO to entity.

        Args:
            dto: The DTO object

        Returns:
            The entity object
        """
        return self.entity_class(**dto.model_dump())

    def entity_to_dto(self, entity: T) -> D:
        """
        Convert entity to DTO.

        Args:
            entity: The entity object

        Returns:
            The DTO object
        """
        return self.dto_class.model_validate(entity)

    def create(self, dto: D) -> D:
        """
        Create a new entity from DTO.

        Args:
            dto: The DTO with entity data

        Returns:
            The created entity as DTO
        """
        entity = self.dto_to_entity(dto)
        created_entity = self.repository.create(entity)
        return self.entity_to_dto(created_entity)

    def read(self, entity_id: int) -> D | None:
        """
        Read an entity by ID.

        Args:
            entity_id: The entity ID

        Returns:
            The entity as DTO or None if not found
        """
        entity = self.repository.read(entity_id)
        if entity is None:
            return None
        return self.entity_to_dto(entity)

    def read_all(self, skip: int = 0, limit: int = 100) -> list[D]:
        """
        Read all entities with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of entities as DTOs
        """
        entities = self.repository.read_all(skip, limit)
        return [self.entity_to_dto(entity) for entity in entities]

    def update(self, entity_id: int, dto: D) -> D | None:
        """
        Update an entity from DTO.

        Args:
            entity_id: The entity ID
            dto: The DTO with updated data

        Returns:
            The updated entity as DTO or None if not found
        """
        entity = self.dto_to_entity(dto)
        updated_entity = self.repository.update(entity_id, entity)
        if updated_entity is None:
            return None
        return self.entity_to_dto(updated_entity)

    def delete(self, entity_id: int) -> bool:
        """
        Delete an entity.

        Args:
            entity_id: The entity ID

        Returns:
            True if deleted, False if not found
        """
        return self.repository.delete(entity_id)
