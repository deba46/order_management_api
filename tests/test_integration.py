"""Integration tests for database and order functionality."""
import pytest
import os
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db_connection


@pytest.fixture(scope="module")
def db_connection():
    """Create database connection for tests."""
    # These tests require actual PostgreSQL connection
    # Skip if PostgreSQL is not available
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create test table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                amount DECIMAL(10, 2) NOT NULL
            )
        """)
        conn.commit()
        
        yield conn
        
        # Cleanup
        cursor.execute("DROP TABLE IF EXISTS orders")
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        pytest.skip(f"PostgreSQL not available: {e}")


@pytest.fixture(scope="function")
def clean_db(db_connection):
    """Clean database before each test."""
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM orders")
    db_connection.commit()
    cursor.close()
    yield
    # Clean up after test
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM orders")
    db_connection.commit()
    cursor.close()


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_database_connection(db_connection):
    """Test database connection is working."""
    cursor = db_connection.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    assert result[0] == 1
    cursor.close()


def test_database_order_table_exists(db_connection):
    """Test that orders table exists."""
    cursor = db_connection.cursor()
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'orders'
        )
    """)
    exists = cursor.fetchone()[0]
    assert exists is True
    cursor.close()


def test_integration_create_and_retrieve_order(client, clean_db, db_connection):
    """Integration test: Create order via API and verify in database."""
    # Create order via API
    order_data = {"amount": 150.00}
    response = client.post("/orders", json=order_data)
    assert response.status_code == 201
    
    api_order = response.json()
    order_id = api_order["id"]
    
    # Verify order exists in database
    cursor = db_connection.cursor()
    cursor.execute("SELECT id, amount FROM orders WHERE id = %s", (order_id,))
    result = cursor.fetchone()
    cursor.close()
    
    assert result is not None
    assert result[0] == order_id
    assert float(result[1]) == 150.00


def test_integration_multiple_orders(client, clean_db, db_connection):
    """Integration test: Create multiple orders and verify persistence."""
    orders_to_create = [
        {"amount": 25.50},
        {"amount": 75.25},
        {"amount": 100.00}
    ]
    
    created_ids = []
    for order_data in orders_to_create:
        response = client.post("/orders", json=order_data)
        assert response.status_code == 201
        created_ids.append(response.json()["id"])
    
    # Verify all orders exist in database
    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]
    assert count == 3
    
    # Verify amounts match
    cursor.execute("SELECT amount FROM orders ORDER BY amount")
    db_amounts = [float(row[0]) for row in cursor.fetchall()]
    cursor.close()
    
    expected_amounts = sorted([order["amount"] for order in orders_to_create])
    assert db_amounts == expected_amounts


def test_integration_order_retrieval_consistency(client, clean_db, db_connection):
    """Integration test: Verify API retrieval matches database state."""
    # Create orders directly in database
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO orders (amount) VALUES (%s), (%s)", (50.00, 75.00))
    db_connection.commit()
    cursor.close()
    
    # Retrieve via API
    response = client.get("/orders")
    assert response.status_code == 200
    
    api_orders = response.json()
    assert len(api_orders) == 2
    
    # Verify data consistency
    api_amounts = sorted([order["amount"] for order in api_orders])
    assert api_amounts == [50.00, 75.00]


def test_integration_database_persistence(client, clean_db):
    """Integration test: Verify data persists across requests."""
    # Create an order
    response = client.post("/orders", json={"amount": 200.00})
    order_id = response.json()["id"]
    
    # Retrieve the order in a separate request
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    assert response.json()["amount"] == 200.00


def test_integration_order_id_autoincrement(client, clean_db):
    """Integration test: Verify order IDs auto-increment correctly."""
    # Create multiple orders
    response1 = client.post("/orders", json={"amount": 10.00})
    response2 = client.post("/orders", json={"amount": 20.00})
    response3 = client.post("/orders", json={"amount": 30.00})
    
    id1 = response1.json()["id"]
    id2 = response2.json()["id"]
    id3 = response3.json()["id"]
    
    # Verify IDs increment
    assert id2 > id1
    assert id3 > id2
