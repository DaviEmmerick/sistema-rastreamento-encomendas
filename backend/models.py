"""
Data models module for package tracking system.
Includes SQLAlchemy ORM models and Pydantic validation schemas (RNF-003, RNF-004).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, func
from pydantic import BaseModel, Field
from typing import Optional

from database import Base


class Encomenda(Base):
    """
    ORM model representing a package in the tracking system.
    Implements the package data structure with tracking code, status, and delivery person assignment.
    """
    __tablename__ = "encomendas"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    codigo_rastreio = Column(String(50), unique=True, index=True, nullable=False)
    descricao = Column(String(500), nullable=False)
    id_entregador = Column(Integer, nullable=True)
    status = Column(String(20), default="Pendente", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


# Pydantic Validation Schemas (Request/Response Models)

class EncomendaCreate(BaseModel):
    """
    Schema for creating a new package (RFC-001).
    Validates incoming JSON request body.
    """
    descricao: str = Field(..., min_length=1, max_length=500, description="Package description")

    class Config:
        json_schema_extra = {
            "example": {
                "descricao": "Eletrônicos - Notebook"
            }
        }


class EncomendaAtribuirRequest(BaseModel):
    """
    Schema for assigning a delivery person to a package (RFC-002).
    Validates the delivery person ID in the request body.
    """
    id_entregador: int = Field(..., gt=0, description="Delivery person ID (must be positive)")

    class Config:
        json_schema_extra = {
            "example": {
                "id_entregador": 1
            }
        }


class StatusUpdateRequest(BaseModel):
    """
    Schema for updating package status (RFC-004 & RFC-005).
    Validates the new status value in the request body.
    """
    novo_status: str = Field(..., description="New package status")

    class Config:
        json_schema_extra = {
            "example": {
                "novo_status": "Em Trânsito"
            }
        }


class EncomendaResponse(BaseModel):
    """
    Schema for returning package data in responses (RNF-003 JSON format).
    Includes all package information: tracking code, description, status, and delivery person.
    """
    id: int
    codigo_rastreio: str
    descricao: str
    id_entregador: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "codigo_rastreio": "BR123456789A",
                "descricao": "Eletrônicos - Notebook",
                "id_entregador": None,
                "status": "Pendente",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }


class EncomendaPublicResponse(BaseModel):
    """
    Schema for public package tracking endpoint (RFC-003).
    Returns only essential information (tracking code, status, description).
    No authentication required.
    """
    codigo_rastreio: str
    descricao: str
    status: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "codigo_rastreio": "BR123456789A",
                "descricao": "Eletrônicos - Notebook",
                "status": "Em Trânsito"
            }
        }
