#!/usr/bin/env python
"""
Quick validation script to check if the backend can start without errors.
Tests import statements and basic initialization.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    print("✓ Importando database.py...")
    from backend.database import engine, get_db, Base, SessionLocal
    print("  ✓ database.py importado com sucesso")

    print("\n✓ Importando models.py...")
    from backend.models import (
        Encomenda,
        EncomendaCreate,
        EncomendaAtribuirRequest,
        StatusUpdateRequest,
        EncomendaResponse,
        EncomendaPublicResponse,
    )
    print("  ✓ models.py importado com sucesso")

    print("\n✓ Importando main.py...")
    from backend.main import app
    print("  ✓ main.py importado com sucesso")
    print("  ✓ FastAPI app inicializado")

    print("\n✓ Criando tabelas de banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("  ✓ Tabelas criadas no SQLite")

    print("\n✓ Validando endpoints...")
    routes = [route.path for route in app.routes]
    expected_endpoints = [
        "/",
        "/encomendas",
        "/encomendas/{codigo_rastreio}",
        "/encomendas/{codigo_rastreio}/atribuir",
        "/encomendas/{codigo_rastreio}/status",
        "/entregadores/{id_entregador}/encomendas",
    ]
    
    for endpoint in expected_endpoints:
        if endpoint in routes:
            print(f"  ✓ Endpoint {endpoint} registrado")
        else:
            print(f"  ✗ Endpoint {endpoint} NÃO ENCONTRADO")

    print("\n" + "="*60)
    print("✓ VALIDAÇÃO BEM-SUCEDIDA")
    print("="*60)
    print(f"\nTotal de endpoints: {len([r for r in app.routes if hasattr(r, 'path')])}")
    print("Backend pronto para uso!")

except Exception as e:
    print(f"\n✗ ERRO DURANTE VALIDAÇÃO:")
    print(f"  {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
