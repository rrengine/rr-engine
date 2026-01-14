# RR Engine

A deterministic 3D model generation and management system for footwear design. RR Engine enforces a strict **Specs → Geometry → AI** pipeline where specifications drive geometry generation, and AI assists only when explicitly invoked.

## Overview

RR Engine is a canonical handoff system built to manage immutable design generations with strict architectural principles:

- **Deterministic Geometry** — 3D models are reproducibly generated from parametric specifications
- **Immutable History** — Every change creates a new generation with full lineage tracking
- **AI-Assisted, User-Controlled** — AI never edits geometry-driving specs automatically
- **Role-Based Access** — Tailored views for owners, factories, suppliers, render teams, and QA
- **Clean Exports** — Geometry separated from human-readable overlays and tech pack data

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           RR ENGINE                                  │
├──────────────────────────────┬──────────────────────────────────────┤
│      RR System API           │       Event Stream API               │
│      (Design Management)     │       (Real-Time Processing)         │
├──────────────────────────────┼──────────────────────────────────────┤
│  • Projects                  │  • Event Ingestion                   │
│  • Generations               │  • Decision Engine (BetaSphere)      │
│  • Specifications            │  • State Snapshots                   │
│  • Geometry Assets           │  • Feedback Loop                     │
│  • Exports                   │  • WebSocket Support                 │
└──────────────────────────────┴──────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
               PostgreSQL 14                    Redis 7
               (Primary Store)                  (Cache/Rate Limit)
```

### Core Services

| Service | Port | Description |
|---------|------|-------------|
| RR System API | 8000 | Design generation, projects, exports |
| Event Stream API | 8000 | Real-time event processing, decisions |
| PostgreSQL | 5432 | Primary data store |
| Redis | 6379 | Caching and rate limiting |

## Tech Stack

- **Runtime**: Python 3.12
- **Framework**: FastAPI (async)
- **Database**: PostgreSQL 14 with asyncpg
- **ORM**: SQLAlchemy (async)
- **Cache**: Redis 7
- **Container**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)

### Run with Docker

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f api

# Stop services
docker compose down
```

### Local Development

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://bam@localhost:5432/rr_engine"
export REDIS_URL="redis://localhost:6379/0"
export API_KEYS="dev-key-change-me"

# Start the database and Redis
docker compose up -d db redis

# Run the API
uvicorn app.main:app --reload --port 8000
```

## API Reference

### RR System API

#### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/projects` | Create a new project |
| `GET` | `/projects/{id}` | Get project details |

#### Generations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/projects/{id}/generations` | Create immutable generation |
| `GET` | `/projects/{id}/generations/{gen_id}` | Get generation details |

#### Generate

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/generate` | Generate/regenerate 3D model |
| `POST` | `/validate` | Validate specifications |

#### Exports

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/export/projects/{id}/generations/{gen_id}` | Export with role-based profile |

#### Factory Integration

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/imports` | Import external designs |
| `POST` | `/factory_feedback` | Receive manufacturing feedback |

### Event Stream API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/events` | Ingest system events |
| `POST` | `/state` | Write state snapshots |
| `POST` | `/decide/{event_id}` | Generate decisions from events |
| `POST` | `/feedback` | Submit decision feedback |
| `WS` | `/ws` | WebSocket for real-time data |

### Health Check

```bash
curl http://localhost:8000/health
# {"ok": true}
```

## Data Model

### Specifications

RR Engine distinguishes between two types of specifications:

**Instrumental Specs** (Geometry-Driving)
- Overall dimensions (length, width, sole thickness)
- Last profile (arch height, toe spring)
- Collar geometry

**Non-Instrumental Specs** (Appearance)
- Materials (upper, lining, outsole)
- Colors (primary/secondary hex values)
- Branding (monogram, embroidery)
- Textures

### Generation Lifecycle

```
Create Generation
       │
       ▼
┌──────────────┐
│   Validate   │◄─── Instrumental specs required
│    Specs     │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌─────────────────┐
│   Missing    │────►│  Option Gate    │
│ Non-Instr?   │     │  1. Use defaults│
└──────┬───────┘     │  2. Cancel      │
       │             │  3. AI draft    │
       │             └─────────────────┘
       ▼
┌──────────────┐
│    Build     │◄─── Deterministic hash-based
│   Geometry   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Generation  │◄─── Immutable snapshot
│   Created    │
└──────────────┘
```

### Roles & Permissions

| Role | Permissions |
|------|-------------|
| `owner` | Full access: generate, regenerate, merge, export |
| `edit` | Create and modify generations |
| `view` | Read-only access |
| `factory` | View geometry + tech pack, submit feedback |
| `supplier` | View BOM, materials, textures only |
| `render` | Access render outputs only |
| `qa` | Validation and approval workflow |

## Project Structure

```
rr-engine/
├── api/                          # Event Stream API
│   ├── main.py                   # FastAPI application
│   ├── config.py                 # Settings & configuration
│   ├── routers/                  # API endpoints
│   │   ├── events.py             # Event ingestion
│   │   ├── state.py              # State snapshots
│   │   ├── decide.py             # Decision generation
│   │   ├── feedback.py           # Feedback submission
│   │   └── ws.py                 # WebSocket support
│   ├── services/
│   │   └── betasphere.py         # Decision engine
│   └── schemas/                  # Pydantic models
│
├── backend/                      # RR System API
│   └── app/
│       ├── main.py               # FastAPI application
│       ├── api/                  # Endpoints
│       │   ├── projects.py
│       │   ├── generations.py
│       │   ├── generate.py
│       │   ├── exports.py
│       │   ├── imports.py
│       │   ├── validate.py
│       │   └── factory_feedback.py
│       ├── models/               # SQLAlchemy ORM models
│       ├── schemas/              # Pydantic schemas
│       ├── core/                 # Business logic
│       ├── geometry/             # Geometry engine
│       ├── db/                   # Database setup
│       └── security/             # Auth & permissions
│
├── docs/                         # Documentation
│   ├── SYSTEM_SPEC_V1.md         # System specification
│   ├── CONTRACTS.md              # Data contracts
│   └── NEXT_STEPS.md             # Engineering roadmap
│
├── schema.sql                    # PostgreSQL schema
├── docker-compose.yml            # Docker services
├── Dockerfile                    # API container
└── README.md
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | Required |
| `API_KEYS` | Comma-separated API keys | Required |
| `DEBUG` | Enable debug mode | `false` |

### Authentication

All API requests require an API key via the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/projects
```

## Design Principles

### Immutability

Generations are never modified. All changes create new generations with parent tracking, enabling:
- Complete audit trail
- Easy rollback via generation switching
- Deterministic replay

### Determinism

Geometry builds use `specs + parent_hashes` for reproducible outputs:
- Same inputs always produce same geometry
- Content-addressed storage via SHA-256 hashing
- Cacheable and verifiable

### AI Boundaries

AI assistance is explicit, auditable, and constrained:
- **Never** edits instrumental (geometry-driving) specs
- **May** suggest non-instrumental (appearance) specs
- All AI actions logged with user context and field modifications
- User approval required before applying AI suggestions

### Separation of Concerns

| Layer | Responsibility |
|-------|---------------|
| Instrumental Specs | Geometry definition (locked from AI) |
| Non-Instrumental Specs | Appearance attributes (AI can suggest) |
| Geometry Assets | 3D model outputs |
| AI Actions | Audit trail of AI modifications |

## License

Proprietary. All rights reserved.
