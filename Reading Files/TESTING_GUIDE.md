# 🧪 Quick Testing Guide

## Scenario 1: End-to-End Fraud Case Creation
**What this tests:** Database + Frontend Auth + API Integration

### Steps:
1. **Login**
   - URL: http://localhost:3000/login
   - User: Adminsai01
   - Pass: Admin@123
   - ✅ Should see Dashboard

2. **Create Prediction**
   - Tab: "Individual Search"
   - User ID: 113
   - Click: "Check Risk"
   - ✅ Should show risk card

3. **Take Action**
   - Click: "⚡ Take Action" button
   - ✅ Modal appears (NOT "Admin ID not found error")

4. **Confirm Case**
   - Risk Level: (auto-selected)
   - Reason: "Suspicious activity detected"
   - Click: "✓ Create Case"
   - ✅ Alert: "Case #X created successfully"

### Expected Results:
- ✅ No SQL errors in backend logs
- ✅ No localStorage errors
- ✅ Case created in database

---

## Scenario 2: View Fraud Cases
**What this tests:** Database query + Fraud Cases page

### Steps:
1. **Navigate to Fraud Cases**
   - Click: "🚨 Fraud Cases" in navbar
   - ✅ Page loads without error

2. **View Cases**
   - ✅ Should see table with columns:
     - User ID
     - Risk Level
     - Status
     - Created By
     - Date Created
   - ✅ Cases from Scenario 1 should appear

3. **Open Case Details**
   - Click: User ID in any row
   - ✅ Modal shows full case details
   - ✅ Shows timestamps and admin info

---

## Scenario 3: Resolve a Case
**What this tests:** Update API + Database write

### Steps:
1. **From Fraud Cases page**
   - Find: Any "OPEN" case
   - Click: "✓ Resolve" button
   - ✅ Modal appears

2. **Enter Resolution**
   - Reason: "False positive - legitimate user"
   - Click: "✓ Confirm"
   - ✅ Alert: "Case resolved successfully"

3. **Verify**
   - ✅ Case status changes to "RESOLVED"
   - ✅ No error messages

---

## Scenario 4: Logout and Login Again
**What this tests:** Session management + localStorage cleanup

### Steps:
1. **Logout**
   - Click: User icon/menu in navbar
   - Click: "Logout"
   - ✅ Redirects to Login page

2. **Check localStorage is clean**
   - Open DevTools (F12)
   - Application → Local Storage → localhost:3000
   - ✅ Should NOT see old adminId
   - ✅ admin_token should be gone

3. **Login Again**
   - Same credentials as before
   - ✅ Should login successfully
   - ✅ New token generated
   - ✅ New adminId stored

---

## Scenario 5: View Case History
**What this tests:** Complex query + User-specific data

### Steps:
1. **From Fraud Cases page**
   - Click: Any User ID
   - ✅ History modal opens

2. **Verify History**
   - ✅ Show "OPEN" cases
   - ✅ Show "RESOLVED" cases
   - ✅ Show timestamps
   - ✅ Show resolution reasons

3. **Close Modal**
   - Click: X or outside modal
   - ✅ Returns to cases list

---

## Quick Verification Commands

### Check Database Columns:
```bash
cd backend
python -c "from sqlalchemy import inspect; from db.sql import engine; print('Columns:', [col['name'] for col in inspect(engine).get_columns('fraud_cases')])"
```
✅ Should show all 11 columns

### Check Database Connection:
```bash
cd backend
python -c "from db.sql import engine; print('Connected:', engine.connect().info)"
```
✅ Should show connection details

### Check Frontend Build:
```bash
cd frontend
npm run build
```
✅ Should build without errors

---

## Backend Logs to Monitor

### Watch backend for errors:
```
ERROR: UndefinedColumn → Database still has old schema
ERROR: Admin ID not found → localStorage not set
ERROR: Cases query failed → Permission or connection issue
```

---

## Browser DevTools Checks

### Console (F12):
- ✅ No red errors
- ✅ No 404s for API calls
- ✅ No localStorage warnings

### Network Tab:
- ✅ POST /admin/login → 200 (returns token + adminId)
- ✅ GET /admin/cases/list/open → 200 (returns cases)
- ✅ POST /admin/cases/create → 201 (case created)
- ✅ PUT /admin/cases/{id}/resolve → 200 (case resolved)

### Application → Local Storage:
```
✅ isAdminLoggedIn: "true"
✅ admin_token: "eyJ..."
✅ adminId: "Adminsai01"
```

---

## Success Criteria ✅

All scenarios pass if:
1. ✅ No SQL "UndefinedColumn" errors
2. ✅ No "Admin ID not found" alerts
3. ✅ Cases page loads and displays data
4. ✅ Can create case from Take Action
5. ✅ Can resolve cases
6. ✅ Auth data properly stored/cleared
7. ✅ All API calls return 200/201 status

---

## If Something Fails 🔧

### Database Error on Cases Page?
```bash
# Verify columns exist
cd backend
python update_database.py  # Re-run if needed
```

### "Admin ID not found"?
```bash
# Clear cache and login again
1. Browser: Ctrl+F5 (hard refresh)
2. Logout and login
3. Check localStorage in DevTools
```

### API Call Failing?
```bash
# Check backend logs for details
# Run: tail -f backend/app.log
# Look for: ERROR or Exception messages
```

### Still Broken?
```
1. Fully restart backend: pkill -f uvicorn && cd backend && uvicorn app:app --reload
2. Clear frontend: rm -rf node_modules/react && npm install && npm start
3. Restart PostgreSQL if needed
```

---

## Expected Output Examples

### Successful Login:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Case Created:
```json
{
  "id": 1,
  "user_id": "USER113",
  "status": "OPEN",
  "risk_level": 3,
  "created_by_admin_id": "Adminsai01",
  "created_at": "2025-01-26T10:30:45"
}
```

### Cases List:
```json
[
  {
    "id": 1,
    "user_id": "USER113",
    "status": "OPEN",
    "risk_level": 3,
    "created_at": "2025-01-26T10:30:45",
    "created_by_admin": "Adminsai01"
  }
]
```

---

## Checklist Before Testing

- [ ] Backend running: `cd backend && uvicorn app:app --reload`
- [ ] Frontend running: `cd frontend && npm start`
- [ ] PostgreSQL running: Check connection in backend logs
- [ ] Database migration run: `python update_database.py` ✅ Done
- [ ] Frontend Login.jsx updated: ✅ Done
- [ ] Frontend Navbar.jsx updated: ✅ Done
- [ ] Browser Developer Tools open: Ready to check localStorage
- [ ] Backend logs visible: Ready to catch errors

---

**Ready to test? Start with Scenario 1!** 🧪
