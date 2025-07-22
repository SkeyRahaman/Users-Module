# FastAPI Users Module

&#x20;&#x20;

A production-ready, modular user management system with authentication, authorization (RBAC), and group management.

## Features

### 🔐 Authentication

- JWT token-based authentication
- OAuth2 password flow with refresh tokens
- Secure password hashing (Argon2)
- Token blacklist for immediate revocation
- Email verification workflow
- Password reset functionality

### 👥 User Management

- Complete CRUD operations
- Soft delete functionality
- Profile management endpoints
- Paginated listings with filtering
- Account verification system

### 🛡️ Authorization

- Role-Based Access Control (RBAC)
- Group management system
- Permission hierarchy
- Endpoint-level access control
- Scope verification middleware

### 📊 Operational Features

- Structured JSON logging
- Sentry error monitoring
- Prometheus metrics endpoint
- Health check system
- Request tracing support

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (SQLAlchemy/asyncpg)
- **Auth**: JWT, OAuth2
- **Security**: Argon2, CSRF protection
- **Monitoring**: Prometheus, Sentry
- **Infra**: Docker, Alembic

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Docker (recommended)

### Quick Start with Docker

```bash
git clone https://github.com/yourrepo/user-service.git
cd user-service
docker-compose up -d --build
```

### Manual Setup

Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure environment:

```bash
cp .env.example .env
# Edit .env with your settings
```

Run migrations:

```bash
alembic upgrade head
```

Start application:

```bash
uvicorn app.main:app --reload
```

## API Documentation

Interactive docs available at:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoints

#### Authentication

| Method | Endpoint              | Description             |
| ------ | --------------------- | ----------------------- |
| POST   | /auth/login           | Obtain JWT tokens       |
| POST   | /auth/logout          | Invalidate token        |
| POST   | /auth/verify          | Verify email address    |
| POST   | /auth/forgot-password | Initiate password reset |
| POST   | /auth/reset-password  | Complete password reset |

#### User Management

| Method | Endpoint  | Description        |
| ------ | --------- | ------------------ |
| POST   | /users/   | Register new user  |
| GET    | /users/me | Get current user   |
| PUT    | /users/me | Update profile     |
| GET    | /users/   | List users (Admin) |

#### Authorization

| Method | Endpoint              | Description         |
| ------ | --------------------- | ------------------- |
| POST   | /roles/               | Create role (Admin) |
| POST   | /groups/              | Create group        |
| POST   | /groups/{id}/add-user | Add member to group |

## Configuration

Essential environment variables:

```ini
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASSWORD=password
```

## Testing

Run the complete test suite:

```bash
pytest -v
```

Generate coverage report:

```bash
pytest --cov=app --cov-report=html
```

## Deployment

### Production Recommendations

- **Web Server:**

```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 4 app.main:app
```

- **Reverse Proxy**: Nginx/Traefik with HTTPS
- **Database**: Configure connection pooling
- **Monitoring**: Enable Sentry and Prometheus

### Kubernetes Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: user-service
        image: your-image:latest
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: user-service-secrets
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

## Support

For issues and feature requests, please open an issue.

---
