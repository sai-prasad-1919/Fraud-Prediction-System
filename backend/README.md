# Fraud Detection Backend API

A robust FastAPI-based backend for fraud detection and prediction with machine learning integration.

## Features

- **FastAPI REST API** - High-performance async API with automatic Swagger documentation
- **PostgreSQL Database** - Relational database for transaction and case data
- **MongoDB** - Document database for admin credentials
- **XGBoost ML Model** - Fraud prediction with 3-level risk scoring
- **JWT Authentication** - Secure admin authentication with token-based access
- **Rate Limiting** - Middleware protection against API abuse (100 req/min per IP)
- **Comprehensive Logging** - Rotating file-based logging for production monitoring
- **Database Retry Logic** - Exponential backoff for connection resilience
- **Pydantic Validation** - Input validation on all endpoints

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- MongoDB 4.0+
- Virtual environment

### Installation

1. **Create and activate virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
# Copy and update .env file
cp .env.example .env
# Edit .env with your database credentials
```

4. **Start the server:**
```bash
uvicorn app:app --reload
```

Server runs at `http://localhost:8000`

## API Endpoints

### Health & Diagnostics
- `GET /` - Health check
- `GET /test-sql` - Test PostgreSQL connection
- `GET /test-mongo` - Test MongoDB connection

### Authentication
- `POST /admin/register` - Register new admin
- `POST /admin/login` - Admin login

### Fraud Prediction
- `POST /admin/predict` - Get fraud predictions for user range
- `GET /admin/predict-test` - Test prediction endpoint

### Case Management
- `POST /admin/cases/create` - Create a fraud case for a user
- `PUT /admin/cases/{case_id}/investigate` - Mark case as Under Investigation
- `PUT /admin/cases/{case_id}/resolve` - Resolve a fraud case with reason
- `GET /admin/cases/list/open` - List all open and under-investigation cases
- `GET /admin/cases/history/{user_id}` - Get case history for a specific user

## Documentation

### Interactive API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Endpoints Documentation

All endpoints include:
- Detailed descriptions
- Example requests/responses
- Parameter documentation
- Error code definitions
- Request/response schemas

## Configuration

### Environment Variables (.env)

```env
# Database Connections
DATABASE_URL=postgresql://postgres:postgres1919@localhost:5432/frauddb
MONGO_URL=mongodb://localhost:27017/admin_db

# Security
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256

# ML Configuration
ML_WINDOW_SIZE=7

# Server
APP_NAME=Fraud Detection API
APP_ENV=development
```

### Database Setup

**PostgreSQL Tables:**
- `transactions` - Transaction records (20,000 sample records), includes `fraud_case_id` and `is_resolved` columns for efficient case tracking
- `fraud_cases` - Fraud investigation cases with full audit trail

**MongoDB Collections:**
- `admins` - Admin account credentials

## Testing

### Run Unit Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth_schemas.py -v

# Run by marker
pytest -m prediction
```

### Test Categories
- **Authentication Tests** - Login/registration validation
- **Risk Scoring Tests** - ML model risk categorization
- **Prediction Tests** - Fraud prediction requests
- **Case Management Tests** - Case lifecycle validation
- **Data Processing Tests** - Feature engineering and preprocessing

See [tests/README.md](tests/README.md) for detailed testing guide.

## Architecture

### Project Structure
```
backend/
├── app.py                 # Main FastAPI application
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── db/                    # Database layers
│   ├── sql.py            # PostgreSQL connection with retry logic
│   └── mongo.py          # MongoDB connection with retry logic
├── models/                # SQLAlchemy ORM models
├── routes/                # API route handlers
├── services/              # Business logic layer
├── schemas/               # Pydantic validation models
├── middleware/            # Middleware components
├── utils/                 # Utilities (auth, logging)
├── ml/                    # Machine learning pipeline
│   ├── data/             # Data loading and processing
│   ├── features/         # Feature engineering
│   ├── inference/        # Risk scoring
│   ├── models/           # Trained XGBoost model
│   └── training/         # Model training scripts
└── tests/                 # Unit tests
```

### Data Flow

1. **User Request** → API Endpoint
2. **Validation** → Pydantic Schema
3. **Authentication** → JWT Token Verification
4. **Rate Limiting** → Middleware Check
5. **Database Query** → Repository Pattern
6. **Business Logic** → Service Layer
7. **ML Prediction** → XGBoost Model (if applicable)
8. **Response** → JSON Response

## Logging

### Log Levels
- **DEBUG** - Detailed diagnostic information
- **INFO** - General operational messages
- **WARNING** - Warning conditions
- **ERROR** - Error conditions

### Log Output
- **Console**: Real-time monitoring in terminal
- **File**: `backend/logs/fraud_prediction.log`
- **Rotation**: Max 10MB per file, 5 backup files

### Accessing Logs
```bash
# View logs in real-time
tail -f backend/logs/fraud_prediction.log

# Search for errors
grep ERROR backend/logs/fraud_prediction.log

# View last 100 lines
tail -100 backend/logs/fraud_prediction.log
```

## Performance & Rate Limiting

### Rate Limits
- **Default**: 100 requests per minute per IP
- **Configurable**: Edit `app.py` middleware configuration
- **Response Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`

### Database Connection Pooling
- **Pool Size**: 5 connections
- **Max Overflow**: 10 additional connections
- **Connection Timeout**: 5 seconds
- **Retry Logic**: 3 attempts with exponential backoff (2s, 4s, 8s)

## Security Features

### Authentication
- JWT token-based authentication
- Secure password hashing (bcrypt)
- Admin ID-based login system
- Token expiration handling

### Input Validation
- Email format validation
- Password strength requirements
- User ID format validation
- Risk level validation (1-3)

### Rate Limiting
- Per-IP rate limiting
- Automatic throttle detection
- Configurable limits

## Troubleshooting

### Database Connection Issues

```python
# Test PostgreSQL connection
$ curl http://localhost:8000/test-sql

# Test MongoDB connection
$ curl http://localhost:8000/test-mongo
```

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Import Errors
```bash
# Ensure backend is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Development

### Adding New Endpoints

1. Create route in `routes/`
2. Define Pydantic schema in `schemas/`
3. Implement service logic in `services/`
4. Add routes to `app.py` with tag and description
5. Write tests in `tests/`

### Example:
```python
# routes/new_route.py
from fastapi import APIRouter, Depends, HTTPException
from schemas.new import NewRequest

router = APIRouter(prefix="/admin/new", tags=["New Feature"])

@router.post("/action", summary="Do something")
def new_action(request: NewRequest, db: Session = Depends(get_sql_db)):
    """
    Description for Swagger documentation
    """
    # Implementation
    return result
```

## Deployment

### Production Checklist
- [ ] Change `JWT_SECRET_KEY` to secure random value
- [ ] Set `APP_ENV=production`
- [ ] Configure PostgreSQL with connection pooling
- [ ] Set up MongoDB replication
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up log rotation
- [ ] Run full test suite: `pytest`
- [ ] Run security check: `bandit -r .`

### Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Dependencies

- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM for databases
- **Pydantic** - Data validation
- **pymongo** - MongoDB driver
- **psycopg2** - PostgreSQL adapter
- **python-jose** - JWT handling
- **bcrypt** - Password hashing
- **xgboost** - ML model
- **pandas** - Data processing
- **pytest** - Testing framework

## Support

For issues or questions:
1. Check logs: `backend/logs/fraud_prediction.log`
2. Review API docs: http://localhost:8000/docs
3. Check test coverage: Run `pytest --cov`
4. Review configuration: Check `.env` file

## License

MIT License - See LICENSE file for details
