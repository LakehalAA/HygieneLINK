import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.sarimax_forecasting import SarimaxForecastingService
from app.models.hygiene_products import ConsumptionData, PredictionModel
from pydantic import BaseModel
from typing import List, Optional
import redis

router = APIRouter()

class ForecastRequest(BaseModel):
    product_id: str
    facility_id: str
    days_ahead: int = 30
    include_confidence_intervals: bool = True

class TrainModelRequest(BaseModel):
    product_id: str
    facility_id: str
    retrain: bool = False

@router.post("/train-model")
async def train_forecasting_model(
    request: TrainModelRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Train SARIMAX model for specific product/facility"""
    
    # Get consumption data
    consumption_data = db.query(ConsumptionData).filter(
        ConsumptionData.product_id == request.product_id,
        ConsumptionData.facility_id == request.facility_id
    ).order_by(ConsumptionData.consumption_date).all()
    
    if len(consumption_data) < 30:
        raise HTTPException(
            status_code=400,
            detail="Insufficient data for training (minimum 30 data points required)"
        )
    
    # Initialize forecasting service
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    forecasting_service = SarimaxForecastingService(redis_client)
    
    try:
        # Train model in background
        background_tasks.add_task(
            train_model_background,
            forecasting_service,
            request.product_id,
            request.facility_id,
            consumption_data,
            db
        )
        
        return {
            "message": "Model training started",
            "product_id": request.product_id,
            "facility_id": request.facility_id,
            "status": "training"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def train_model_background(
    forecasting_service: SarimaxForecastingService,
    product_id: str,
    facility_id: str,
    consumption_data: List[ConsumptionData],
    db: Session
):
    """Background task for model training"""
    try:
        model_info = forecasting_service.train_sarimax_model(
            product_id, facility_id, consumption_data
        )
        
        # Save model metadata to database
        prediction_model = PredictionModel(
            model_name=f"SARIMAX_{product_id}_{facility_id}",
            product_category="toilet_paper",
            facility_id=facility_id,
            model_parameters=str(model_info['best_params']),
            accuracy_score=model_info['accuracy_score'],
            last_trained=datetime.datetime.now(),
            is_active=True
        )
        
        db.add(prediction_model)
        db.commit()
        
    except Exception as e:
        print(f"Model training failed: {str(e)}")

@router.post("/forecast")
async def generate_forecast(
    request: ForecastRequest,
    db: Session = Depends(get_db)
):
    """Generate consumption forecast using SARIMAX"""
    
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    forecasting_service = SarimaxForecastingService(redis_client)
    
    try:
        forecast = forecasting_service.generate_forecast(
            request.product_id,
            request.facility_id,
            request.days_ahead
        )
        
        return forecast
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def get_trained_models(
    facility_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of trained forecasting models"""
    
    query = db.query(PredictionModel).filter(PredictionModel.is_active == True)
    
    if facility_id:
        query = query.filter(PredictionModel.facility_id == facility_id)
    
    models = query.order_by(PredictionModel.last_trained.desc()).all()
    
    return [
        {
            "id": model.id,
            "model_name": model.model_name,
            "facility_id": model.facility_id,
            "accuracy_score": model.accuracy_score,
            "last_trained": model.last_trained.isoformat(),
            "is_active": model.is_active
        }
        for model in models
    ]
