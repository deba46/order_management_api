"""Unit tests for the FastAPI application."""
import pytest
import psycopg2
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app


@pytest.fixture
def mock_db():
    """Mock database connection."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None
    return mock_conn, mock_cursor


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@patch('app.main.get_db')
def test_health_check_success(mock_get_db, client, mock_db):
    """Test health check endpoint with successful DB connection."""
    mock_conn, mock_cursor = mock_db
    mock_get_db.return_value = mock_conn
    
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "service" in data
    assert "version" in data


@patch('app.main.get_db')
def test_health_check_db_failure(mock_get_db, client):
    """Test health check when database fails."""
    mock_get_db.side_effect = Exception("Connection failed")
    
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unhealthy"
    assert data["database"] == "disconnected"


@patch('app.main.get_db')
def test_create_order(mock_get_db, client, mock_db):
    """Test creating an order."""
    mock_conn, mock_cursor = mock_db
    mock_get_db.return_value = mock_conn
    mock_cursor.fetchone.return_value = {"id": 1, "amount": 99.99}
    
    order_data = {"amount": 99.99}
    response = client.post("/orders", json=order_data)
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 99.99
    assert data["id"] == 1


def test_create_order_invalid_amount(client):
    """Test creating an order with invalid amount."""
    order_data = {"amount": -10.0}
    response = client.post("/orders", json=order_data)
    assert response.status_code == 422  # Validation error


@patch('app.main.get_db')
def test_get_orders_empty(mock_get_db, client, mock_db):
    """Test retrieving orders when none exist."""
    mock_conn, mock_cursor = mock_db
    mock_get_db.return_value = mock_conn
    mock_cursor.fetchall.return_value = []
    
    response = client.get("/orders")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@patch('app.main.get_db')
def test_get_orders(mock_get_db, client, mock_db):
    """Test retrieving all orders."""
    mock_conn, mock_cursor = mock_db
    mock_get_db.return_value = mock_conn
    mock_cursor.fetchall.return_value = [
        {"id": 1, "amount": 10.50},
        {"id": 2, "amount": 25.75}
    ]
    
    response = client.get("/orders")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["amount"] == 10.50
    assert data[1]["amount"] == 25.75


@patch('app.main.get_db')
def test_get_order_by_id(mock_get_db, client, mock_db):
    """Test retrieving a specific order."""
    mock_conn, mock_cursor = mock_db
    mock_get_db.return_value = mock_conn
    mock_cursor.fetchone.return_value = {"id": 1, "amount": 50.00}
    
    response = client.get("/orders/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["amount"] == 50.00


@patch('app.main.get_db')
def test_get_order_not_found(mock_get_db, client, mock_db):
    """Test retrieving a non-existent order."""
    mock_conn, mock_cursor = mock_db
    mock_get_db.return_value = mock_conn
    mock_cursor.fetchone.return_value = None
    
    response = client.get("/orders/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@patch('app.main.get_db')
def test_home_page(mock_get_db, client, mock_db):
    """Test home page renders."""
    mock_conn, mock_cursor = mock_db
    mock_get_db.return_value = mock_conn
    mock_cursor.fetchall.return_value = []
    
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
