from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class InventoryBase(BaseModel):
    product_id: str
    facility_id: str
    current_stock: float = Field(..., ge=0)
    minimum_threshold: float = Field(..., ge=0)
    maximum_capacity: Optional[float] = Field(None, ge=0)
    predicted_depletion_date: Optional[datetime] = None

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    current_stock: Optional[float] = Field(None, ge=0)
    minimum_threshold: Optional[float] = Field(None, ge=0)
    maximum_capacity: Optional[float] = Field(None, ge=0)
    predicted_depletion_date: Optional[datetime] = None

class InventoryInDBBase(InventoryBase):
    id: str
    created_at: datetime
    updated_at: datetime
    last_restocked: Optional[datetime] = None

    class Config:
        orm_mode = True

class Inventory(InventoryInDBBase):
    pass

class InventoryInDB(InventoryInDBBase):
    pass

class InventoryOut(BaseModel):
    id: UUID  # Instead of str
    product_id: UUID  # Instead of str
    facility_id: UUID  # Instead of str
    current_stock: float
    minimum_threshold: float
    maximum_capacity: Optional[float]
    predicted_depletion_date: Optional[datetime]
    supplier_name: Optional[str]
    product_name: Optional[str]
    category: Optional[str]
    last_restocked: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

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