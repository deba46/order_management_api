"""Pydantic models for orders."""
from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    """Schema for creating an order."""
    amount: float = Field(..., description="Order amount", gt=0)


class Order(BaseModel):
    """Order model."""
    id: int
    amount: float
