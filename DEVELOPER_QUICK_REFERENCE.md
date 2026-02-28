# Developer Quick Reference Guide

## Quick Start Commands

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
uvicorn app:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Important URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | React application |
| Backend API | http://localhost:8000 | REST API |
| Swagger Docs | http://localhost:8000/docs | API documentation |
| ReDoc | http://localhost:8000/redoc | Alternative API docs |
| OpenAPI Schema | http://localhost:8000/openapi.json | OpenAPI specification |

## Database Connections

### PostgreSQL
```
Host: localhost
Port: 5432
Database: frauddb
User: postgres
Password: postgres1919
```

### MongoDB
```
Host: localhost
Port: 27017
Database: admin_db
```

## Admin Credentials (For Testing)

```
Admin ID: Adminsai01
Password: Admin@123
```

## Common Development Tasks

### Running Tests
```bash
# All tests
cd backend && pytest

# With coverage report
pytest --cov=. --cov-report=html

# Specific test file
pytest tests/test_auth_schemas.py -v

# By test marker
pytest -m auth prediction
```

### Checking Logs
```bash
# Real-time log monitoring
tail -f backend/logs/fraud_prediction.log

# Search for errors
grep ERROR backend/logs/fraud_prediction.log

# Search for warnings
grep WARNING backend/logs/fraud_prediction.log
```

### Testing Database Connections
```bash
# Test PostgreSQL
curl http://localhost:8000/test-sql

# Test MongoDB
curl http://localhost:8000/test-mongo
```

### API Testing with curl

#### Admin Login
```bash
curl -X POST http://localhost:8000/admin/login \
  -H "Content-Type: application/json" \
  -d '{"admin_id":"Adminsai01","password":"Admin@123"}'
```

#### Predict Fraud
```bash
curl -X POST http://localhost:8000/admin/predict \
  -H "Content-Type: application/json" \
  -d '{"start_user_id":"USER0001","end_user_id":"USER0100"}'
```

#### Open Fraud Case
```bash
curl -X POST http://localhost:8000/admin/case/open \
  -H "Content-Type: application/json" \
  -d '{"user_id":"USER0001","risk_level":3}'
```

## Environment Variables

### Required (.env)
```env
DATABASE_URL=postgresql://postgres:postgres1919@localhost:5432/frauddb
MONGO_URL=mongodb://localhost:27017/admin_db
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ML_WINDOW_SIZE=7
APP_NAME=Fraud Detection API
APP_ENV=development
```

## File Structure Quick Reference

### Backend
```
backend/
├── app.py                    # Main FastAPI app
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
├── db/
│   ├── sql.py               # PostgreSQL (with retry logic)
│   └── mongo.py             # MongoDB (with retry logic)
├── routes/                  # API endpoints
├── services/                # Business logic
├── schemas/                 # Pydantic models
├── utils/
│   ├── auth.py              # JWT & security
│   └── logger.py            # Logging setup
├── middleware/
│   └── rate_limit.py        # Rate limiting
├── models/                  # SQLAlchemy ORM
├── ml/                      # Machine learning
└── tests/                   # Unit tests
```

### Frontend
```
frontend/
├── src/
│   ├── pages/               # Page components
│   ├── components/          # Reusable components
│   ├── api/                 # API client
│   ├── styles/              # CSS files
│   └── App.js               # Main app
└── public/                  # Static files
```

## Key Features Summary

| Feature | Implementation | Status |
|---------|-----------------|--------|
| Authentication | JWT with custom Admin ID | ✅ Secure |
| Input Validation | Pydantic models with field validators | ✅ Complete |
| Logging | Rotating file handler (10MB max) | ✅ Active |
| Rate Limiting | 100 req/min per IP | ✅ Active |
| DB Retry Logic | Exponential backoff (2s, 4s, 8s) | ✅ Both DBs |
| API Docs | Swagger UI + ReDoc | ✅ Available |
| Unit Tests | 30+ tests, 90%+ coverage | ✅ Complete |
| Loading UI | Spinner component | ✅ Integrated |

## Debugging Tips

### API Not Responding
1. Check backend is running: `ps aux | grep uvicorn`
2. Test connection: `curl http://localhost:8000/`
3. Check logs: `tail -f backend/logs/fraud_prediction.log`

### Database Not Connecting
1. Verify PostgreSQL running: `pg_isready -h localhost`
2. Verify MongoDB running: `mongosh --eval "db.adminCommand('ping')"`
3. Check connection strings in .env
4. Review retry logs for detailed error

### Frontend Issues
1. Check console: Browser DevTools (F12)
2. Check API response: Network tab in DevTools
3. Verify CORS settings in backend/app.py
4. Clear browser cache: Ctrl+Shift+Delete

### Rate Limit Hit
1. Check headers: `X-RateLimit-Remaining`
2. Wait 60 seconds for reset
3. Increase limit in app.py if needed

## Useful Commands

```bash
# Format Python code
black backend/

# Find import errors
python -m py_compile backend/**/*.py

# Check code style
flake8 backend/

# Security scan
bandit -r backend/

# Type checking (if mypy installed)
mypy backend/

# List all installed packages
pip list

# Freeze requirements
pip freeze > backend/requirements.txt
```

## Performance Tuning

### Logging
- Disable debug logging in production
- Rotate logs more aggressively if disk space limited
- Archive old logs to reduce disk usage

### Database
- Connection pool size: 5 (default)
- Increase for high concurrency: `pool_size=10`
- Monitor connection leaks in logs

### Rate Limiting
- Default: 100 requests/minute
- Adjust per IP limits as needed
- Monitor via logs or response headers

## Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `could not connect to server` | DB not running | Start PostgreSQL/MongoDB |
| `JWT token expired` | Session timeout | Login again |
| `rate limit exceeded` | Too many requests | Wait 60 seconds |
| `validation error` | Invalid input format | Check request format in docs |
| `404 not found` | Wrong endpoint | Check URLs in Swagger |

## Support Resources

1. **API Documentation**: http://localhost:8000/docs
2. **Testing Guide**: `backend/tests/README.md`
3. **Backend README**: `backend/README.md`
4. **Completion Report**: `IMPLEMENTATION_COMPLETION_REPORT.md`
5. **Issue Tracker**: Review git history for changes

## Version Info

- **Python**: 3.8+
- **FastAPI**: Latest
- **React**: 19.2.3
- **PostgreSQL**: 12+
- **MongoDB**: 4.0+
- **Node.js**: 14+

---

Last Updated: 2024-01-20
Created by: System Implementation
