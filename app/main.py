"""FastAPI Application for Order Management."""
import logging
import sys
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from psycopg2.extras import RealDictCursor
from app.database import get_db, init_db
from app.schemas import OrderCreate, Order
from app.config import settings

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)
# -----------------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting up application...")
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.exception("Database initialization failed: %s", e)
        raise


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Simple html UI to display orders."""
    logger.info("Fetching all orders for root view.")
    try:
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id, amount FROM orders")
                orders = cursor.fetchall()
        logger.debug("Fetched %d orders.", len(orders))
    except Exception:
        logger.exception("Error fetching orders from database.")
        raise HTTPException(status_code=500, detail="Database query failed")

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "orders": orders}
    )


@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity check."""
    logger.info("Performing health check...")
    health_status = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "unknown"
    }

    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
        health_status["database"] = "connected"
        health_status["database_type"] = "postgresql"
        logger.info("Health check OK.")
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"
        health_status["error"] = str(e)
        logger.exception("Health check failed: %s", e)

    return health_status


@app.post("/orders", response_model=Order, status_code=201)
async def create_order(order: OrderCreate):
    """Create a new order."""
    logger.info("Creating a new order: %s", order)
    try:
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "INSERT INTO orders (amount) VALUES (%s) RETURNING id, amount",
                    (order.amount,)
                )
                result = cursor.fetchone()
        logger.info("Created order with ID %s", result["id"])
    except Exception:
        logger.exception("Error creating order.")
        raise HTTPException(status_code=500, detail="Failed to create order")

    return Order(**result)


@app.get("/orders", response_model=List[Order])
async def get_orders():
    """Retrieve all orders."""
    logger.info("Retrieving all orders.")
    try:
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id, amount FROM orders")
                orders = cursor.fetchall()
        logger.debug("Fetched %d orders.", len(orders))
    except Exception:
        logger.exception("Error retrieving orders.")
        raise HTTPException(status_code=500, detail="Database query failed")

    return [Order(**order) for order in orders]


@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: int):
    """Retrieve a specific order by ID."""
    logger.info("Retrieving order ID: %d", order_id)
    try:
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT id, amount FROM orders WHERE id = %s",
                    (order_id,)
                )
                result = cursor.fetchone()
        if result is None:
            logger.warning("Order ID %d not found.", order_id)
            raise HTTPException(status_code=404, detail="Order not found")
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error retrieving order ID %d", order_id)
        raise HTTPException(status_code=500, detail="Database query failed")

    return Order(**result)
