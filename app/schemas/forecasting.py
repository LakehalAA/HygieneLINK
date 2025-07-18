from pydantic import BaseModel, Field
from typing import List, Optional

class ForecastRequest(BaseModel):
    product_id: str
    facility_id: str
    days_ahead: int = Field(default=30, ge=1, le=365)
    include_confidence_intervals: bool = True

class TrainModelRequest(BaseModel):
    product_id: str
    facility_id: str
    retrain: bool = False

class ForecastPrediction(BaseModel):
    date: str
    predicted_consumption: float
    lower_bound: float
    upper_bound: float
    confidence_level: int = 95

class ForecastResponse(BaseModel):
    product_id: str
    facility_id: str
    forecast_horizon: int
    generated_at: str
    predictions: List[ForecastPrediction]
    total_predicted_consumption: float
    depletion_date: Optional[str] = None