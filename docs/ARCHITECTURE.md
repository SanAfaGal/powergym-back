# System Architecture

This document provides an overview of the PowerGym Backend architecture, design patterns, and system design decisions.

## Table of Contents

- [Overview](#overview)
- [Architecture Layers](#architecture-layers)
- [Design Patterns](#design-patterns)
- [Technology Stack](#technology-stack)
- [Data Flow](#data-flow)
- [Security Architecture](#security-architecture)
- [Scalability Considerations](#scalability-considerations)

## Overview

PowerGym Backend follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │
│  - Request/Response Handling        │
│  - Authentication/Authorization     │
│  - Input Validation                 │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│       Service Layer (Business)       │
│  - Business Logic                   │
│  - Data Transformation              │
│  - Orchestration                    │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│    Repository Layer (Data Access)    │
│  - Database Operations              │
│  - Query Building                   │
│  - Data Persistence                 │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│      Database Layer (PostgreSQL)     │
│  - Relational Data                  │
│  - Vector Storage (pgvector)        │
└─────────────────────────────────────┘
```

## Architecture Layers

### 1. API Layer (`app/api/`)

**Responsibility**: HTTP request/response handling

**Components**:
- **Endpoints**: Route handlers for each resource
- **Dependencies**: Authentication, database session injection
- **Schemas**: Request/response validation (Pydantic)

**Key Features**:
- RESTful API design
- JWT authentication
- Request validation
- Error handling
- Rate limiting

**Example Flow**:
```
HTTP Request → Endpoint → Dependency Injection → Service Layer
```

### 2. Service Layer (`app/services/`)

**Responsibility**: Business logic and orchestration

**Components**:
- **Business Logic**: Domain-specific operations
- **Data Transformation**: Convert between models and schemas
- **Orchestration**: Coordinate multiple repository calls
- **Notifications**: Send async notifications

**Key Features**:
- Stateless services (static methods)
- Business rule enforcement
- Transaction management
- Error handling

**Example**:
```python
class ClientService:
    @staticmethod
    def create_client(db: Session, client_data: ClientCreate) -> ClientModel:
        # Business logic
        # Validation
        # Repository calls
        # Notifications
        return client
```

### 3. Repository Layer (`app/repositories/`)

**Responsibility**: Data access and persistence

**Components**:
- **CRUD Operations**: Create, Read, Update, Delete
- **Query Building**: Complex database queries
- **Data Mapping**: Model to database mapping

**Key Features**:
- Generic base repository
- Type-safe operations
- Query optimization
- No business logic

**Example**:
```python
class ClientRepository(BaseRepository[ClientModel, UUID]):
    def get_by_dni(self, dni_number: str) -> Optional[ClientModel]:
        return self.db.query(ClientModel).filter(
            ClientModel.dni_number == dni_number
        ).first()
```

### 4. Database Layer

**Responsibility**: Data persistence

**Components**:
- **PostgreSQL**: Relational database
- **pgvector**: Vector extension for face embeddings
- **SQLAlchemy ORM**: Object-relational mapping
- **Alembic**: Database migrations

## Design Patterns

### Repository Pattern

**Purpose**: Abstract database operations

**Implementation**:
- Base repository with generic CRUD
- Specialized repositories per entity
- Consistent interface across repositories

**Benefits**:
- Testability (easy to mock)
- Maintainability
- Database agnostic

### Service Pattern

**Purpose**: Encapsulate business logic

**Implementation**:
- Stateless service classes
- Static methods
- Orchestrate repository calls

**Benefits**:
- Separation of concerns
- Reusability
- Testability

### Dependency Injection

**Purpose**: Loose coupling and testability

**Implementation**:
- FastAPI's dependency system
- Database session injection
- Authentication dependency

**Benefits**:
- Testability
- Flexibility
- Maintainability

### Facade Pattern

**Purpose**: Simplify complex subsystems

**Implementation**:
- `NotificationService` as facade for notification handlers
- `FaceRecognitionService` orchestrates face recognition components

**Benefits**:
- Simplified interface
- Encapsulation
- Easier maintenance

## Technology Stack

### Backend Framework

- **FastAPI**: Modern, high-performance web framework
  - Async support
  - Automatic API documentation
  - Type validation with Pydantic

### Database

- **PostgreSQL 18**: Relational database
- **pgvector**: Vector extension for face embeddings
- **SQLAlchemy 2.0**: Modern ORM
- **Alembic**: Migration management

### Face Recognition

- **InsightFace**: Face recognition library
- **ONNX Runtime**: Model inference
- **OpenCV**: Image processing
- **NumPy**: Numerical operations

### Authentication & Security

- **PyJWT**: JWT token handling
- **pwdlib**: Password hashing (Argon2)
- **cryptography**: Encryption utilities

### Other Technologies

- **Pydantic**: Data validation
- **python-telegram-bot**: Telegram notifications
- **slowapi**: Rate limiting
- **httpx**: HTTP client

## Data Flow

### Request Flow

```
1. HTTP Request
   ↓
2. FastAPI Router
   ↓
3. Authentication Middleware
   ↓
4. Endpoint Handler
   ↓
5. Request Validation (Pydantic)
   ↓
6. Service Layer
   ↓
7. Repository Layer
   ↓
8. Database
   ↓
9. Response Serialization
   ↓
10. HTTP Response
```

### Face Recognition Flow

```
1. Image Upload (Base64)
   ↓
2. Image Processing
   ↓
3. Face Detection (InsightFace)
   ↓
4. Embedding Extraction (512-dim vector)
   ↓
5. Vector Storage (pgvector)
   ↓
6. Similarity Search (for authentication)
   ↓
7. Match Result
```

### Subscription Flow

```
1. Create Subscription Request
   ↓
2. Validate Plan & Client
   ↓
3. Calculate Dates & Price
   ↓
4. Create Subscription Record
   ↓
5. Send Notification
   ↓
6. Return Subscription
```

## Security Architecture

### Authentication

- **JWT Tokens**: Stateless authentication
- **Access Tokens**: Short-lived (5 hours default)
- **Refresh Tokens**: Longer-lived (12 hours default)
- **Token Rotation**: Refresh mechanism

### Authorization

- **Role-Based**: Admin and Employee roles
- **Resource-Based**: Permissions per resource
- **Dependency Injection**: Automatic authorization checks

### Data Security

- **Password Hashing**: Argon2 algorithm
- **Biometric Encryption**: Encrypted thumbnails
- **Environment Variables**: Secrets management
- **HTTPS**: Transport security (production)

### API Security

- **Rate Limiting**: Prevent abuse
- **CORS**: Restricted origins
- **Input Validation**: Pydantic schemas
- **SQL Injection Prevention**: SQLAlchemy ORM

## Scalability Considerations

### Horizontal Scaling

**Current Design**:
- Stateless API (JWT tokens)
- Shared database
- No session storage

**Scaling Strategy**:
1. **Load Balancer**: Distribute requests
2. **Multiple Instances**: Run multiple backend containers
3. **Database**: Use managed database service
4. **Caching**: Add Redis for frequently accessed data

### Vertical Scaling

**Current Design**:
- Single container deployment
- Resource limits configurable

**Scaling Strategy**:
1. **Increase Resources**: CPU, memory
2. **GPU Support**: For face recognition
3. **Database Optimization**: Indexes, query optimization

### Database Scaling

**Current Design**:
- Single PostgreSQL instance
- pgvector for vector operations

**Scaling Strategy**:
1. **Read Replicas**: For read-heavy workloads
2. **Connection Pooling**: Optimize connections
3. **Query Optimization**: Indexes, query tuning
4. **Partitioning**: For large tables

### Face Recognition Scaling

**Current Design**:
- Model loaded per instance
- CPU/GPU inference

**Scaling Strategy**:
1. **GPU Acceleration**: Use GPU for faster inference
2. **Model Caching**: Cache model in memory
3. **Batch Processing**: Process multiple faces
4. **Dedicated Service**: Separate face recognition service

## Component Interactions

### Client Registration Flow

```
API Endpoint
    ↓
ClientService.create_client()
    ↓
ClientRepository.create()
    ↓
Database (INSERT)
    ↓
NotificationService (async)
    ↓
Telegram Bot
```

### Face Authentication Flow

```
API Endpoint
    ↓
FaceRecognitionService.authenticate()
    ↓
EmbeddingService.extract_face_encoding()
    ↓
FaceDatabase.search_similar()
    ↓
PostgreSQL + pgvector (similarity search)
    ↓
Match Result
```

### Subscription Renewal Flow

```
GitHub Actions (scheduled)
    ↓
API Endpoint: /subscriptions/activate
    ↓
SubscriptionService.activate_scheduled()
    ↓
SubscriptionRepository.update()
    ↓
Database (UPDATE)
    ↓
NotificationService (async)
```

## Design Decisions

### Why FastAPI?

- **Performance**: High performance, async support
- **Type Safety**: Pydantic validation
- **Documentation**: Auto-generated OpenAPI docs
- **Modern**: Python 3.10+ features

### Why Repository Pattern?

- **Testability**: Easy to mock repositories
- **Flexibility**: Can swap database implementations
- **Maintainability**: Clear separation of concerns

### Why pgvector?

- **Performance**: Fast vector similarity search
- **Integration**: Native PostgreSQL extension
- **Scalability**: Efficient indexing
- **Simplicity**: No separate vector database needed

### Why Stateless Services?

- **Scalability**: Easy horizontal scaling
- **Testability**: No shared state
- **Simplicity**: No state management needed

## Future Considerations

### Potential Improvements

1. **Caching Layer**: Redis for frequently accessed data
2. **Message Queue**: For async task processing
3. **Microservices**: Split face recognition to separate service
4. **GraphQL**: Alternative API layer
5. **Event Sourcing**: For audit trail
6. **API Gateway**: For routing and rate limiting

### Migration Path

Current architecture supports:
- Adding caching layer
- Introducing message queue
- Splitting services
- Adding new features

---

**Next**: [Development Guide](DEVELOPMENT.md) | [Deployment Guide](DEPLOYMENT.md)

