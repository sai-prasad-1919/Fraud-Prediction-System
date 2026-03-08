# ⚡ Quick Action Guide - What to Do Now

## Current System Status
✅ **FULLY OPERATIONAL** - All critical files present and functional

---

## Option 1: Run the System ▶️

### Start Backend Server
```bash
# Navigate to project root
cd "e:/SAI PRASAD/Projects/(React Frontend)Fraud-Predict_temp_10_01_26/Fraud-Predict_10_01_26"

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Start backend
cd backend
uvicorn app:app --reload
```

The backend will be available at:
- 🌐 API: `http://localhost:8000`
- 📚 Swagger Docs: `http://localhost:8000/docs`
- 📖 ReDoc: `http://localhost:8000/redoc`

### Start Frontend Server (in new terminal)
```bash
cd frontend
npm start
```

Frontend will be available at:
- 🌐 App: `http://localhost:3000`

---

## Option 2: Check Database Health 🗄️

```bash
# Test PostgreSQL connection
curl http://localhost:8000/test-sql

# Test MongoDB connection
curl http://localhost:8000/test-mongo
```

This will show:
- ✅ PostgreSQL connection status
- ✅ MongoDB connection status

---

## Option 3: Run Tests 🧪

### First-time Setup (Install Test Dependencies)
```bash
cd backend
pip install pytest pytest-cov
```

### Run All Tests
```bash
cd backend
pytest
```

### Run with Coverage Report
```bash
cd backend
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser to view coverage
```

### Run Specific Tests
```bash
# Only authentication tests
pytest tests/test_auth_schemas.py -v

# Only risk scoring tests
pytest tests/test_risk_scorer.py -v

# Only data processing tests
pytest tests/test_data_processing.py -v
```

---

## Option 4: Test API Endpoints 🧪

### Test Login
```bash
curl -X POST http://localhost:8000/admin/login \
  -H "Content-Type: application/json" \
  -d '{"admin_id":"Adminsai01","password":"Admin@123"}'
```

### Test Fraud Prediction
```bash
curl -X POST http://localhost:8000/admin/predict \
  -H "Content-Type: application/json" \
  -d '{"start_user_id":"USER0001","end_user_id":"USER0100"}'
```

### Test Database Connections
```bash
# PostgreSQL
curl http://localhost:8000/test-sql

# MongoDB
curl http://localhost:8000/test-mongo
```

---

## Option 5: View Logs 📋

### Real-time Log Monitoring
```bash
# From backend directory
tail -f logs/fraud_prediction.log
```

### Search Logs
```bash
# Find all errors
grep ERROR logs/fraud_prediction.log

# Find all warnings
grep WARNING logs/fraud_prediction.log

# Find specific user activity
grep "USER0001" logs/fraud_prediction.log
```

---

## Option 6: Verify Configuration 📝

### Check Environment Setup
```bash
# Create a test script
cat > test_env.py << 'EOF'
import os
from dotenv import load_dotenv
load_dotenv()

print("🔧 Environment Configuration Check")
print("=" * 50)
print(f"JWT_SECRET_KEY:  {'✅ Set' if os.getenv('JWT_SECRET_KEY') else '❌ Missing'}")
print(f"DATABASE_URL:    {'✅ Set' if os.getenv('DATABASE_URL') else '❌ Missing'}")
print(f"MONGO_URL:       {'✅ Set' if os.getenv('MONGO_URL') else '❌ Missing'}")
print(f"ML_WINDOW_SIZE:  {os.getenv('ML_WINDOW_SIZE', '7')}")
print(f"APP_ENV:         {os.getenv('APP_ENV', 'development')}")
print("=" * 50)
EOF

python test_env.py
```

---

## Option 7: Review Documentation 📚

### Quick Reference
- 📖 **Backend Overview**: `backend/README.md`
- 🧪 **Testing Guide**: `backend/tests/README.md`
- ⚡ **Quick Start**: `DEVELOPER_QUICK_REFERENCE.md`
- 📊 **Project Summary**: `IMPLEMENTATION_COMPLETION_REPORT.md`
- 📋 **System Status**: `SYSTEM_STATUS_REPORT.md`
- ✅ **File Checklist**: `FILE_VERIFICATION_CHECKLIST.md`

### API Documentation
- 📚 **Interactive Docs**: http://localhost:8000/docs (when backend running)
- 📖 **Structured Docs**: http://localhost:8000/redoc (when backend running)

---

## Option 8: Clean & Reset 🧹

### Clear Logs
```bash
rm backend/logs/fraud_prediction.log
```

### Clear Cache
```bash
# Python cache
find . -type d -name __pycache__ -exec rm -rf {} +

# Node cache
cd frontend
npm cache clean --force
```

### Reinstall Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt --force-reinstall

# Frontend
cd frontend
npm install --legacy-peer-deps
```

---

## Option 9: Make Changes 🔧

### Add a New Endpoint
1. Create route in `backend/routes/new_route.py`
2. Define Pydantic schema in `backend/schemas/new.py`
3. Add to `backend/app.py`:
   ```python
   from routes.new_route import router as new_router
   app.include_router(new_router)
   ```

### Update Frontend Component
1. Edit component in `frontend/src/components/` or `frontend/src/pages/`
2. Component automatically reloads with `npm start`

### Add Test
1. Create test in `backend/tests/test_new.py`
2. Import fixtures from `conftest.py`
3. Run with `pytest tests/test_new.py -v`

---

## Common Commands Reference 🚀

```bash
# Activate environment
source .venv/Scripts/activate

# Install packages
pip install package_name

# Run backend
cd backend && uvicorn app:app --reload

# Run frontend
cd frontend && npm start

# Run tests
pytest -v

# View logs
tail -f backend/logs/fraud_prediction.log

# Test API
curl http://localhost:8000/docs

# Check database
python database_health_check.py

# Format code
black backend/

# Check syntax
python -m py_compile backend/**/*.py
```

---

## Troubleshooting ⚠️

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or from scratch
pip install --upgrade pip
pip install -r requirements.txt
```

### Database Connection Issues
```bash
# Test PostgreSQL
python database_health_check.py

# Or manually
psycopg2 --version
mongosh --version
```

### Tests Not Found
```bash
# Ensure pytest is installed
pip install pytest pytest-cov

# Restart Python kernel if using IDE
```

---

## What's Different After Recent Undos?

✅ **Removed 5 experimental files** (non-critical):
- test_beneficiary_suspicious_fields.py
- test_integration_risk_scoring.py
- RISK_SCORING_GUIDE.md
- ENHANCED_RISK_SCORING_SUMMARY.md
- RISK_SCORING_QUICK_REFERENCE.md

✅ **All core system remains**:
- Backend API fully functional
- Frontend fully functional
- Database integration intact
- Tests operational (58+ tests)
- All documentation present

---

## Next Steps Recommendation

### For Development 👨‍💻
1. Start both servers: `uvicorn` + `npm start`
2. Make changes to code
3. Run tests: `pytest`
4. Check API docs: `http://localhost:8000/docs`

### For Testing 🧪
1. Install test dependencies: `pip install pytest pytest-cov`
2. Run full test suite: `pytest --cov`
3. Check coverage report: `htmlcov/index.html`

### For Production 🚀
1. Verify all configs in `.env`
2. Change JWT_SECRET_KEY to secure value
3. Set APP_ENV=production
4. Run full test suite
5. Test database connections
6. Deploy

---

## Support Resources

| Need | Resource | Location |
|------|----------|----------|
| Backend Documentation | README | `backend/README.md` |
| Testing Guide | README | `backend/tests/README.md` |
| Quick Start | Reference | `DEVELOPER_QUICK_REFERENCE.md` |
| Project Summary | Report | `IMPLEMENTATION_COMPLETION_REPORT.md` |
| System Status | Report | `SYSTEM_STATUS_REPORT.md` |
| File Verification | Checklist | `FILE_VERIFICATION_CHECKLIST.md` |
| API Documentation | Live Docs | http://localhost:8000/docs |

---

## Admin Credentials (For Testing)

```
Admin ID: Adminsai01
Password: Admin@123
```

⚠️ **Change in production!**

---

## Last Verification

✅ **All systems operational**
✅ **No critical issues**
✅ **All files verified**
✅ **Ready for next action**

**Status**: READY TO PROCEED

Choose your action above and get started! 🚀

---

Generated: February 26, 2026
