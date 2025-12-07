from typing import TypeVar, Generic, Type, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlmodel import SQLModel
from app.service.v1.base_service import BaseService

T = TypeVar("T", bound=SQLModel)  # Entity type
D = TypeVar("D", bound=BaseModel)  # DTO type


class BaseController(Generic[T, D]):
    """
    Generic base controller providing FastAPI routes for CRUD operations.
    
    Type Parameters:
        T: SQLModel entity type
        D: Pydantic DTO type
    
    Subclasses should call register_routes() to set up the CRUD endpoints.
    """

    def __init__(
        self,
        router: APIRouter,
        service: BaseService[T, D],
        dto_class: Type[D],
    ):
        """
        Initialize controller with router and service.
        
        Args:
            router: FastAPI router instance
            service: The service instance
            dto_class: The DTO class for responses
        """
        self.router = router
        self.service = service
        self.dto_class = dto_class

    def register_routes(self) -> None:
        """Register all CRUD routes. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement register_routes()")
