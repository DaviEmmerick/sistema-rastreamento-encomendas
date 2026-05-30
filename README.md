# Sistema de Rastreamento de Encomendas

## Estrutura de Arquivos Entregues

```
sistema-rastreamento-encomendas/
│
├── BACKEND (Implementado)
│   └── backend/
│       ├── __init__.py                  Pacote Python
│       ├── database.py                  SQLAlchemy + SQLite (323 linhas)
│       ├── models.py                    ORM + Schemas Pydantic (138 linhas)
│       └── main.py                      FastAPI App + 5 Endpoints (414 linhas)
│
├── EXISTENTES
│   ├── Relatorio_SD.pdf                 Especificações técnicas
│   ├── README.md                        Docs do projeto
│   ├── LICENSE                          Licença
│   └── .gitignore                       Git ignore rules
│
```

## Endpoints Implementados

```
┌─────────────────────────────────────────────────────────────────┐
│                    🚀 5 ENDPOINTS RESTFUL                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ✅ [201] POST   /encomendas                                     │
│         → Cria encomenda com código único                       │
│         → RF-001: Cadastro de Encomenda                         │
│                                                                  │
│ ✅ [200] POST   /encomendas/{codigo_rastreio}/atribuir         │
│         → Atribui entregador                                    │
│         → RF-002: Atribuição de Entregador                      │
│                                                                  │
│ ✅ [200] GET    /encomendas/{codigo_rastreio}                  │
│         → Busca pública (sem autenticação)                      │
│         → RF-003: Consulta de Status                            │
│                                                                  │
│ ✅ [200] GET    /entregadores/{id_entregador}/encomendas       │
│         → Lista encomendas do entregador                        │
│         → RF-006: Listagem por Entregador                       │
│                                                                  │
│ ✅ [200] PATCH  /encomendas/{codigo_rastreio}/status           │
│         → Atualiza status com máquina de estados                │
│         → RF-004 & RF-005: Atualização de Status                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Máquina de Estados

```
        ┌──────────────┐
        │ Criação POST │
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │  Pendente    │ ◄─── Status inicial (RF-001)
        └──────┬───────┘
               │ POST /atribuir ◄─── RF-002
               │ (com entregador)
               │
               ▼
        ┌──────────────┐
        │ Em Trânsito  │ ◄─── PATCH /status
        └──┬───────┬───┘
           │       │
     [RF-004] [RF-005]
           │       │
           ▼       ▼
      ┌────────┐ ┌───────┐
      │Entregue│ │Falhou │
      └────────┘ └───────┘
      (final)    (final)

 Transições válidas: 3
 Transições bloqueadas: tudo mais
 Validação: Servidor-side (obrigatória)
```

## Requisitos Atendidos

```
┌────────────────────────────────────────────────────────┐
│                   REQUISITOS NÃO-FUNCIONAIS             │
├────────────────────────────────────────────────────────┤
│                                                        │
│  [✅] RNF-001  Arquitetura Cliente-Servidor Estrita   │
│  [✅] RNF-002  Estilo RESTful                         │
│  [✅] RNF-003  Formato JSON                           │
│  [✅] RNF-004  Persistência SQLite + SQLAlchemy       │
│  [✅] RNF-005  Aplicação Stateless                    │
│                                                        │
├────────────────────────────────────────────────────────┤
│                   REQUISITOS FUNCIONAIS                │
├────────────────────────────────────────────────────────┤
│                                                        │
│  [✅] RF-001   Cadastro de Encomenda                  │
│  [✅] RF-002   Atribuição de Entregador               │
│  [✅] RF-003   Busca Pública de Status                │
│  [✅] RF-004   Atualização de Status                  │
│  [✅] RF-005   Máquina de Estados Rigorosa            │
│  [✅] RF-006   Listagem por Entregador                │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## 🛠️ Tecnologias Utilizadas

```
┌──────────────────────────────────────────────────────┐
│  Framework/Biblioteca    │ Versão │ Propósito       │
├──────────────────────────────────────────────────────┤
│  FastAPI                 │ 0.104  │ Web REST        │
│  Uvicorn                 │ 0.24   │ Servidor ASGI   │
│  SQLAlchemy              │ 2.0    │ ORM             │
│  Pydantic                │ 2.5    │ Validação JSON  │
│  SQLite                  │ Latest │ Banco de Dados  │
└─────────────────────────────────────────────────────┘
```

## 🎯 Caso de Uso Completo

```
1️⃣  CLIENTE CRIA ENCOMENDA
    POST /encomendas
    ├─ Status: 201 Created
    └─ Retorna: codigo_rastreio, status=Pendente

2️⃣  CLIENTE CONSULTA STATUS (PÚBLICO)
    GET /encomendas/{codigo_rastreio}
    ├─ Status: 200 OK
    └─ Sem autenticação!

3️⃣  ADMIN ATRIBUI ENTREGADOR
    POST /encomendas/{codigo_rastreio}/atribuir
    ├─ Valida: encomenda existe + está Pendente
    └─ Status: 200 OK

4️⃣  ENTREGADOR INICIA ENTREGA
    PATCH /encomendas/{codigo_rastreio}/status
    ├─ novo_status: "Em Trânsito"
    ├─ Valida: máquina de estados
    └─ Status: 200 OK

5️⃣  ENTREGADOR FINALIZA ENTREGA
    PATCH /encomendas/{codigo_rastreio}/status
    ├─ novo_status: "Entregue"
    ├─ Valida: transição válida
    └─ Status: 200 OK

6️⃣  ADMIN LISTA ENCOMENDAS DO ENTREGADOR
    GET /entregadores/{id}/encomendas
    └─ Retorna: apenas não-finalizadas
```

## Links Úteis

```
   Documentação
   ├─ FastAPI: https://fastapi.tiangolo.com
   ├─ SQLAlchemy: https://docs.sqlalchemy.org
   ├─ Pydantic: https://docs.pydantic.dev
   └─ Uvicorn: https://www.uvicorn.org

   Ferramentas Recomendadas
   ├─ Postman: API testing
   ├─ VS Code: Editor
   ├─ SQLiteBrowser: Database viewer
   └─ Git: Version control

   Padrões
   ├─ REST API Design: https://restfulapi.net
   ├─ HTTP Status Codes: https://httpwg.org/specs/
   └─ JSON Schema: https://json-schema.org
```