"""
FastAPI REST API Backend for Package Tracking System.
Implements RNF-001 (Client-Server Architecture), RNF-002 (RESTful),
RNF-003 (JSON Format), RNF-004 (SQLite Persistence), RNF-005 (Stateless).

All endpoints implement strict server-side state machine validation (RF-005).
"""

import random
import string
from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import (
    Encomenda,
    EncomendaCreate,
    EncomendaAtribuirRequest,
    StatusUpdateRequest,
    EncomendaResponse,
    EncomendaPublicResponse,
)

# FastAPI App Initialization

app = FastAPI(
    title="API de Rastreamento de Encomendas",
    description="Backend REST para Sistema de Rastreamento de Encomendas em Logística Local",
    version="1.0.0"
)

# Create database tables on startup (RNF-004)
Base.metadata.create_all(bind=engine)
 
# CORS Middleware Configuration (RNF-001, RNF-002)
# Allow all origins, methods, and headers for frontend integration

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Utility Functions

def generate_tracking_code() -> str:
    """
    Generate a unique alphanumeric tracking code.
    Format: BR + 9 random digits + 1 letter check digit
    Example: BR123456789A
    
    Returns:
        str: Unique tracking code in format BR[9 digits][letter]
    """
    digits = ''.join(random.choices(string.digits, k=9))
    check_digit = random.choice(string.ascii_uppercase)
    return f"BR{digits}{check_digit}"


def validar_transicao_status(
    status_atual: str,
    novo_status: str,
    id_entregador: int | None = None
) -> None:
    """
    Strict server-side state machine validator (RF-005, RNF-005).
    Enforces valid status transitions and raises HTTP 400 for invalid transitions.
    
    Valid transitions:
    - Pendente → Em Trânsito (ONLY if delivery person assigned)
    - Em Trânsito → Entregue
    - Em Trânsito → Falhou
    - All other combinations are PROHIBITED
    
    Args:
        status_atual: Current package status
        novo_status: Requested new status
        id_entregador: Delivery person ID (required for Pendente → Em Trânsito)
        
    Raises:
        HTTPException: 400 Bad Request if transition is invalid
    """
    # Define valid transitions as tuples of (current_status, next_status)
    VALID_TRANSITIONS = {
        ("Pendente", "Em Trânsito"),
        ("Em Trânsito", "Entregue"),
        ("Em Trânsito", "Falhou"),
    }

    transition = (status_atual, novo_status)

    # Check if transition exists in valid transitions
    if transition not in VALID_TRANSITIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transição de status inválida: {status_atual} → {novo_status}. "
                   f"Apenas as seguintes transições são permitidas: "
                   f"Pendente → Em Trânsito, Em Trânsito → Entregue, Em Trânsito → Falhou."
        )

    # Additional validation: Pendente → Em Trânsito requires assigned delivery person
    if transition == ("Pendente", "Em Trânsito") and id_entregador is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível atualizar para 'Em Trânsito' sem um entregador atribuído. "
                   "Use o endpoint POST /encomendas/{codigo_rastreio}/atribuir primeiro."
        )


# Health Check Endpoint

@app.get("/", tags=["Health"])
def root():
    """Health check endpoint."""
    return {
        "mensagem": "API de Rastreamento de Encomendas - Sistema Online",
        "status": "operacional"
    }


# RF-001: Create Package / Cadastro de Encomenda

@app.post(
    "/encomendas",
    response_model=EncomendaResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Encomendas"],
    summary="RF-001: Cadastrar nova encomenda"
)
def criar_encomenda(
    encomenda_data: EncomendaCreate,
    db: Session = Depends(get_db)
) -> EncomendaResponse:
    """
    Create and register a new package (RF-001).
    Automatically generates unique tracking code and sets initial status to 'Pendente'.
    
    Returns:
        201 Created: Package created successfully with tracking code
        
    Request body:
        {
            "descricao": "Package description"
        }
    """
    # Generate unique tracking code (retry if collision)
    codigo_rastreio = generate_tracking_code()
    
    # Ensure uniqueness of tracking code
    max_retries = 10
    for _ in range(max_retries):
        existing = db.query(Encomenda).filter(
            Encomenda.codigo_rastreio == codigo_rastreio
        ).first()
        if not existing:
            break
        codigo_rastreio = generate_tracking_code()
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao gerar código de rastreio único"
        )

    # Create new package with Pendente status
    nova_encomenda = Encomenda(
        codigo_rastreio=codigo_rastreio,
        descricao=encomenda_data.descricao,
        status="Pendente",
        id_entregador=None
    )

    db.add(nova_encomenda)
    db.commit()
    db.refresh(nova_encomenda)

    return nova_encomenda



# RF-002: Assign Delivery Person / Atribuir Entregador

@app.post(
    "/encomendas/{codigo_rastreio}/atribuir",
    response_model=EncomendaResponse,
    status_code=status.HTTP_200_OK,
    tags=["Encomendas"],
    summary="RF-002: Atribuir entregador a encomenda pendente"
)
def atribuir_entregador(
    codigo_rastreio: str,
    request_data: EncomendaAtribuirRequest,
    db: Session = Depends(get_db)
) -> EncomendaResponse:
    """
    Assign a delivery person to a pending package (RF-002).
    Only allows assignment if package exists and is in 'Pendente' status.
    
    Returns:
        200 OK: Delivery person assigned successfully
        404 Not Found: Package not found
        400 Bad Request: Package is not in 'Pendente' status
        
    URL parameters:
        codigo_rastreio: Package tracking code
        
    Request body:
        {
            "id_entregador": 1
        }
    """
    # Fetch package by tracking code
    encomenda = db.query(Encomenda).filter(
        Encomenda.codigo_rastreio == codigo_rastreio
    ).first()

    if not encomenda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Encomenda com código '{codigo_rastreio}' não encontrada"
        )

    # Validate package is in Pendente status
    if encomenda.status != "Pendente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível atribuir entregador a encomenda em status '{encomenda.status}'. "
                   f"A encomenda deve estar em status 'Pendente'."
        )

    # Assign delivery person
    encomenda.id_entregador = request_data.id_entregador
    encomenda.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(encomenda)

    return encomenda


# RF-003: Get Package Status / Buscar Status de Encomenda (PUBLIC - NO AUTH)

@app.get(
    "/encomendas/{codigo_rastreio}",
    response_model=EncomendaPublicResponse,
    status_code=status.HTTP_200_OK,
    tags=["Encomendas"],
    summary="RF-003: Buscar status de encomenda (Público - sem autenticação)"
)
def buscar_encomenda(
    codigo_rastreio: str,
    db: Session = Depends(get_db)
) -> EncomendaPublicResponse:
    """
    Retrieve package status by tracking code (RF-003).
    PUBLIC ENDPOINT - No authentication required.
    Allows customers to track their packages using only the tracking code.
    
    Returns:
        200 OK: Package found with status and description
        404 Not Found: Package not found
        
    URL parameters:
        codigo_rastreio: Package tracking code
    """
    # Fetch package by tracking code
    encomenda = db.query(Encomenda).filter(
        Encomenda.codigo_rastreio == codigo_rastreio
    ).first()

    if not encomenda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Encomenda com código '{codigo_rastreio}' não encontrada"
        )

    return encomenda


# RF-006: Get Delivery Person's Packages / Listar Encomendas do Entregador

@app.get(
    "/entregadores/{id_entregador}/encomendas",
    response_model=List[EncomendaResponse],
    status_code=status.HTTP_200_OK,
    tags=["Entregadores"],
    summary="RF-006: Listar encomendas não-finalizadas do entregador"
)
def listar_encomendas_entregador(
    id_entregador: int,
    db: Session = Depends(get_db)
) -> List[EncomendaResponse]:
    """
    List all packages assigned to a delivery person, excluding completed packages (RF-006).
    Returns only packages with status NOT 'Entregue' and NOT 'Falhou'.
    
    Returns:
        200 OK: List of active packages (may be empty)
        
    URL parameters:
        id_entregador: Delivery person ID
    """
    # Query all packages for delivery person excluding Entregue and Falhou statuses
    encomendas = db.query(Encomenda).filter(
        Encomenda.id_entregador == id_entregador,
        Encomenda.status.notin_(["Entregue", "Falhou"])
    ).all()

    return encomendas


# RF-004 & RF-005: Update Package Status / Atualizar Status de Encomenda

@app.patch(
    "/encomendas/{codigo_rastreio}/status",
    response_model=EncomendaResponse,
    status_code=status.HTTP_200_OK,
    tags=["Encomendas"],
    summary="RF-004 & RF-005: Atualizar status com validação de máquina de estados"
)
def atualizar_status_encomenda(
    codigo_rastreio: str,
    request_data: StatusUpdateRequest,
    db: Session = Depends(get_db)
) -> EncomendaResponse:
    """
    Update package status with strict server-side state machine validation (RF-004 & RF-005).
    
    Valid transitions:
    - Pendente → Em Trânsito (requires assigned delivery person)
    - Em Trânsito → Entregue
    - Em Trânsito → Falhou
    
    All other transitions are PROHIBITED and return HTTP 400 Bad Request.
    
    Returns:
        200 OK: Status updated successfully
        404 Not Found: Package not found
        400 Bad Request: Invalid status transition
        
    URL parameters:
        codigo_rastreio: Package tracking code
        
    Request body:
        {
            "novo_status": "Em Trânsito"
        }
    """
    # Fetch package by tracking code
    encomenda = db.query(Encomenda).filter(
        Encomenda.codigo_rastreio == codigo_rastreio
    ).first()

    if not encomenda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Encomenda com código '{codigo_rastreio}' não encontrada"
        )

    # Validate state machine transition (RF-005)
    validar_transicao_status(
        status_atual=encomenda.status,
        novo_status=request_data.novo_status,
        id_entregador=encomenda.id_entregador
    )

    # Update status
    encomenda.status = request_data.novo_status
    encomenda.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(encomenda)

    return encomenda

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
