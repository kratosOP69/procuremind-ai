import pytest
from src.main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_low_risk_fraud_score(client):
    payload = {
        "invoice_data": {
            "invoice_number": "INV-200",
            "vendor_name": "Office Supplies Inc",
            "gross_amount": 500.0,
            "vendor_id": "V-123"
        },
        "vendor_data": {
            "vendor_id": "V-123",
            "vendor_name": "Office Supplies Inc",
            "is_active": True,
            "historical_invoice_numbers": ["INV-198", "INV-199"],
            "average_invoice_amount": 450.0
        }
    }
    response = client.post("/score", json=payload)
    assert response.status_code == 200
    data = response.json
    assert data["risk_level"] == "LOW"
    assert data["fraud_score"] == 0

def test_duplicate_invoice(client):
    payload = {
        "invoice_data": {
            "invoice_number": "INV-199",
            "vendor_name": "Office Supplies Inc",
            "gross_amount": 500.0,
            "vendor_id": "V-123"
        },
        "vendor_data": {
            "vendor_id": "V-123",
            "vendor_name": "Office Supplies Inc",
            "is_active": True,
            "historical_invoice_numbers": ["INV-198", "INV-199"],
            "average_invoice_amount": 450.0
        }
    }
    response = client.post("/score", json=payload)
    data = response.json
    assert data["fraud_score"] == 70
    assert data["risk_level"] == "HIGH"
    assert "Duplicate invoice number detected for this vendor." in data["fraud_indicators"]
