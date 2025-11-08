"""FastAPI Application for Order Management."""
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from psycopg2.extras import RealDictCursor
from app.database import get_db, init_db
from app.schemas import OrderCreate, Order
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Simple html UI to display orders."""
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT id, amount FROM orders")
            orders = cursor.fetchall()

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "orders": orders}
    )


@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity check."""
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
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"
        health_status["error"] = str(e)

    return health_status


@app.post("/orders", response_model=Order, status_code=201)
async def create_order(order: OrderCreate):
    """Create a new order."""
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "INSERT INTO orders (amount) VALUES (%s) RETURNING id, amount",
                (order.amount,)
            )
            result = cursor.fetchone()

    return Order(**result)


@app.get("/orders", response_model=List[Order])
async def get_orders():
    """Retrieve all orders."""
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT id, amount FROM orders")
            orders = cursor.fetchall()

    return [Order(**order) for order in orders]


@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: int):
    """Retrieve a specific order by ID."""
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT id, amount FROM orders WHERE id = %s",
                (order_id,)
            )
            result = cursor.fetchone()

    if result is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return Order(**result)
