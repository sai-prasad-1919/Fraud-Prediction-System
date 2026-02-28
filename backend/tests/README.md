# Testing Guide for Fraud Detection System

This directory contains comprehensive unit tests for the Fraud Detection and Prediction System.

## Test Structure

- **test_risk_scorer.py** - Tests for fraud risk scoring functionality
- **test_auth_schemas.py** - Tests for authentication and validation schemas
- **test_prediction_case_requests.py** - Tests for prediction and case management request schemas
- **test_data_processing.py** - Tests for data preprocessing and feature engineering
- **conftest.py** - Pytest fixtures and test configuration

## Installation

### Install Testing Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs pytest and pytest-cov along with all project dependencies.

## Running Tests

### Run All Tests

```bash
pytest
```

### Run With Verbose Output

```bash
pytest -v
```

### Run Specific Test File

```bash
pytest tests/test_auth_schemas.py -v
```

### Run Specific Test Class

```bash
pytest tests/test_auth_schemas.py::TestAdminLoginSchema -v
```

### Run Specific Test Function

```bash
pytest tests/test_auth_schemas.py::TestAdminLoginSchema::test_valid_login_credentials -v
```

### Run Tests With Coverage Report

```bash
pytest --cov=. --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`

### Run Tests By Marker

```bash
pytest -m auth          # Run only auth tests
pytest -m prediction    # Run only prediction tests
pytest -m data          # Run only data processing tests
```

## Test Categories

### Authentication Tests (test_auth_schemas.py)
- ✓ Valid login/registration
- ✓ Email format validation
- ✓ Password requirements
- ✓ Admin ID format validation
- ✓ Required field validation
- ✓ Input sanitization (whitespace stripping, lowercase conversion)

### Risk Scoring Tests (test_risk_scorer.py)
- ✓ Risk level categorization (1, 2, 3)
- ✓ Boundary value testing (30%, 50%, 70%)
- ✓ Monotonic risk increase with fraud probability
- ✓ Return type validation

### Prediction & Case Management Tests (test_prediction_case_requests.py)
- ✓ Valid request construction
- ✓ Required field validation
- ✓ Data type validation
- ✓ User ID format validation
- ✓ Risk level validation
- ✓ Transaction list handling
- ✓ Edge cases (empty lists, null values)

### Data Processing Tests (test_data_processing.py)
- ✓ DataFrame structure validation
- ✓ Data type correctness
- ✓ Value range validation (positive amounts, binary labels)
- ✓ Feature engineering calculations
- ✓ Aggregation operations
- ✓ Time window filtering
- ✓ Edge case handling (NaN, duplicates, future dates)

## Test Fixtures

Available fixtures in `conftest.py`:

```python
test_db_engine        # In-memory SQLite database
test_db_session       # Database session for tests
sample_transactions_data  # Sample transaction dictionary
sample_transaction_df # Sample transaction pandas DataFrame
sample_features       # Sample feature vector
mock_xgboost_model    # Mock XGBoost model
```

## Example Test Usage

```python
def test_prediction_with_sample_data(sample_transaction_df):
    """Test prediction with sample transaction data"""
    assert len(sample_transaction_df) == 5
    assert "user_id" in sample_transaction_df.columns

def test_database_session(test_db_session):
    """Test with database session fixture"""
    # Your test code here
    pass
```

## Coverage Goals

- **Authentication**: 100% - All validation paths tested
- **Risk Scoring**: 100% - All risk categories tested
- **Case Management**: 95%+ - Main flows tested
- **Data Processing**: 85%+ - Common operations tested

## Continuous Integration

To integrate with CI/CD pipeline:

```bash
pytest --cov=. --cov-report=xml --cov-report=term-missing
```

This generates XML for CI integration and terminal output with missing lines.

## Troubleshooting

### Import Errors

If you get import errors, ensure:
1. You're in the `backend` directory
2. Python path includes backend directory
3. All dependencies are installed: `pip install -r requirements.txt`

### Database Errors

Tests use in-memory SQLite. If you get database errors:
1. Ensure SQLAlchemy is properly installed
2. Check that models are imported correctly in conftest.py

### Fixture Errors

If fixtures are not found:
1. Ensure `conftest.py` is in the `tests` directory
2. Check fixture names match exactly (case-sensitive)

## Adding New Tests

1. Create new test file prefixed with `test_` in the tests directory
2. Follow naming convention: `test_<module>.py`
3. Use descriptive test names: `test_<functionality>_<expected_behavior>`
4. Use appropriate fixtures from `conftest.py`
5. Add pytest markers for categorization

## Performance Considerations

- Tests use in-memory SQLite for speed
- Mock objects used where appropriate
- Parallel execution safe (no shared database state)
- Full test suite completes in <10 seconds

## Best Practices

✓ Each test should test one thing
✓ Use descriptive test names
✓ Use fixtures for common setup
✓ Mock external dependencies
✓ Test both happy path and error cases
✓ Use pytest markers for organization

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pydantic Testing](https://docs.pydantic.dev/latest/concepts/models/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/faq/testing.html)
