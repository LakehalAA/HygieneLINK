from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date

class DashboardMetrics(BaseModel):
    active_products: int = Field(..., description="Number of active products")
    total_facilities: int = Field(..., description="Total facilities monitored")
    active_suppliers: int = Field(..., description="Number of active suppliers")
    pending_reorders: int = Field(..., description="Items requiring reorder")
    monthly_consumption: float = Field(..., description="Total monthly consumption")
    avg_consumption_per_employee: float = Field(..., description="Average consumption per employee")
    sustainability_score: float = Field(..., description="Overall sustainability score")
    cost_savings_percentage: float = Field(..., description="Cost savings percentage")

class ConsumptionTrend(BaseModel):
    date: str = Field(..., description="Date in ISO format")
    consumption: float = Field(..., description="Actual consumption")
    predicted: float = Field(..., description="Predicted consumption")
    facility_count: int = Field(..., description="Number of facilities")

class AlertItem(BaseModel):
    id: str
    type: str = Field(..., description="Alert type: reorder, anomaly, compliance")
    severity: str = Field(..., description="Severity: low, medium, high, critical")
    title: str
    description: str
    facility_id: str
    product_name: Optional[str] = None
    created_at: str

class AIInsight(BaseModel):
    type: str = Field(..., description="Insight type: optimization, prediction, risk")
    title: str
    description: str
    impact: str
    confidence: float = Field(..., ge=0, le=100, description="Confidence percentage")
    action_required: bool

class SustainabilityMetrics(BaseModel):
    carbon_footprint: dict
    waste_reduction: dict
    sustainable_products: dict
    certifications: dict
    cost_savings: dict