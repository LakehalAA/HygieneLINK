from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class InventoryItem(BaseModel):
    id: str
    product_name: str
    category: str
    current_stock: float
    minimum_threshold: float
    maximum_capacity: float
    predicted_depletion_date: Optional[str] = None
    reorder_recommended: bool
    supplier_name: str
    facility_id: str

class ReorderRecommendation(BaseModel):
    product_id: str
    facility_id: str
    current_stock: float
    reorder_point: float
    recommended_quantity: float
    estimated_cost: float
    urgency: str = Field(..., description="Urgency: low, medium, high, critical")
    justification: str

class StockUpdateRequest(BaseModel):
    new_stock_level: float = Field(..., ge=0, description="New stock level")