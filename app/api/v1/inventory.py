import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.hygiene_products import ConsumptionData, Inventory, HygieneProduct, Supplier
from app.services.inventory_optimization import InventoryOptimizationService
from app.services.sarimax_forecasting import SarimaxForecastingService
from pydantic import BaseModel
from typing import List, Optional
import redis

router = APIRouter()

class InventoryItem(BaseModel):
    id: str
    product_name: str
    category: str
    current_stock: float
    minimum_threshold: float
    maximum_capacity: float
    predicted_depletion_date: Optional[str]
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
    urgency: str
    justification: str

def convert_decimal_to_float(value) -> float:
    """Helper function to convert Decimal to float"""
    if isinstance(value, Decimal):
        return float(value)
    elif value is None:
        return 0.0
    else:
        return float(value)

@router.get("/status", response_model=List[InventoryItem])
async def get_inventory_status(
    facility_id: Optional[str] = None,
    low_stock_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get current inventory status across facilities"""
    
    query = db.query(Inventory, HygieneProduct, Supplier).join(
        HygieneProduct, Inventory.product_id == HygieneProduct.id
    ).join(
        Supplier, HygieneProduct.supplier_id == Supplier.id
    )
    
    if facility_id:
        query = query.filter(Inventory.facility_id == facility_id)
    
    if low_stock_only:
        query = query.filter(Inventory.current_stock <= Inventory.minimum_threshold)
    
    results = query.all()
    
    inventory_items = []
    for inventory, product, supplier in results:
        # Convert Decimal types to float for JSON serialization
        current_stock_float = convert_decimal_to_float(inventory.current_stock)
        minimum_threshold_float = convert_decimal_to_float(inventory.minimum_threshold)
        maximum_capacity_float = convert_decimal_to_float(inventory.maximum_capacity) or 1000.0
        
        inventory_items.append(InventoryItem(
            id=str(inventory.id),
            product_name=product.name,
            category=product.category,
            current_stock=current_stock_float,
            minimum_threshold=minimum_threshold_float,
            maximum_capacity=maximum_capacity_float,
            predicted_depletion_date=inventory.predicted_depletion_date.isoformat() if inventory.predicted_depletion_date else None,
            reorder_recommended=current_stock_float <= minimum_threshold_float,
            supplier_name=supplier.name,
            facility_id=str(inventory.facility_id)
        ))
    
    return inventory_items

@router.get("/reorder-recommendations", response_model=List[ReorderRecommendation])
async def get_reorder_recommendations(
    facility_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get AI-powered reorder recommendations"""
    
    # Initialize services
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    forecasting_service = SarimaxForecastingService(redis_client)
    optimization_service = InventoryOptimizationService(forecasting_service)
    
    # Get low stock items
    query = db.query(Inventory, HygieneProduct).join(
        HygieneProduct, Inventory.product_id == HygieneProduct.id
    ).filter(Inventory.current_stock <= Inventory.minimum_threshold * 1.5)  # Include items approaching threshold
    
    if facility_id:
        query = query.filter(Inventory.facility_id == facility_id)
    
    low_stock_items = query.all()
    
    recommendations = []
    for inventory, product in low_stock_items:
        try:
            # Calculate optimal reorder point
            reorder_analysis = optimization_service.calculate_optimal_reorder_point(
                product.id, inventory.facility_id
            )
            
            # Determine urgency - Handle Decimal types properly
            current_stock_float = convert_decimal_to_float(inventory.current_stock)
            minimum_threshold_float = convert_decimal_to_float(inventory.minimum_threshold)
            stock_ratio = current_stock_float / minimum_threshold_float if minimum_threshold_float > 0 else 0
            
            if stock_ratio <= 0.5:
                urgency = "critical"
            elif stock_ratio <= 0.8:
                urgency = "high"
            else:
                urgency = "medium"
            
            # Calculate recommended quantity (Economic Order Quantity simplified)
            # Handle Decimal types properly
            maximum_capacity_float = convert_decimal_to_float(inventory.maximum_capacity) or 1000.0
            
            recommended_quantity = max(
                maximum_capacity_float - current_stock_float,
                reorder_analysis['reorder_point'] * 1.5  # 1.5x reorder point
            )
            
            # Handle cost calculation with proper type conversion
            cost_per_unit_float = convert_decimal_to_float(product.cost_per_unit) or 10.0
            estimated_cost = recommended_quantity * cost_per_unit_float
            
            justification = f"Stock level at {stock_ratio:.1%} of minimum threshold. "
            justification += f"SARIMAX predicts {reorder_analysis['lead_time_consumption']:.1f} units needed during lead time."
            
            recommendations.append(ReorderRecommendation(
                product_id=str(product.id),
                facility_id=str(inventory.facility_id),
                current_stock=current_stock_float,
                reorder_point=reorder_analysis['reorder_point'],
                recommended_quantity=round(recommended_quantity, 2),
                estimated_cost=round(estimated_cost, 2),
                urgency=urgency,
                justification=justification
            ))
            
        except Exception as e:
            # If SARIMAX calculation fails, use simple reorder logic
            current_stock_float = convert_decimal_to_float(inventory.current_stock)
            minimum_threshold_float = convert_decimal_to_float(inventory.minimum_threshold)
            maximum_capacity_float = convert_decimal_to_float(inventory.maximum_capacity) or 1000.0
            cost_per_unit_float = convert_decimal_to_float(product.cost_per_unit) or 10.0
            
            recommended_quantity = maximum_capacity_float - current_stock_float
            estimated_cost = recommended_quantity * cost_per_unit_float
            
            recommendations.append(ReorderRecommendation(
                product_id=str(product.id),
                facility_id=str(inventory.facility_id),
                current_stock=current_stock_float,
                reorder_point=minimum_threshold_float,
                recommended_quantity=round(recommended_quantity, 2),
                estimated_cost=round(estimated_cost, 2),
                urgency="high" if current_stock_float <= minimum_threshold_float else "medium",
                justification="Basic reorder calculation - insufficient data for AI prediction"
            ))
    
    return sorted(recommendations, key=lambda x: {"critical": 0, "high": 1, "medium": 2}[x.urgency])

@router.put("/update-stock/{inventory_id}")
async def update_stock_level(
    inventory_id: str,
    new_stock_level: float,
    db: Session = Depends(get_db)
):
    """Update inventory stock level"""
    
    inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    # Store old stock level for comparison
    old_stock_level = convert_decimal_to_float(inventory.current_stock)
    
    # Update stock level
    setattr(inventory, "current_stock", new_stock_level)
    setattr(inventory, "updated_at", datetime.datetime.now())
    
    # Check if this is a restock (new level > old level)
    if new_stock_level > old_stock_level:
        setattr(inventory, "last_restocked", datetime.datetime.now())
    
    db.commit()
    
    return {
        "message": "Stock level updated successfully",
        "inventory_id": inventory_id,
        "old_stock_level": old_stock_level,
        "new_stock_level": new_stock_level
    }

@router.get("/optimization-analysis")
async def get_inventory_optimization_analysis(
    facility_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get comprehensive inventory optimization analysis"""
    
    # Query consumption data for analysis
    consumption_query = db.query(ConsumptionData)
    if facility_id:
        consumption_query = consumption_query.filter(ConsumptionData.facility_id == facility_id)
    
    consumption_data = consumption_query.all()
    
    # Initialize optimization service
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    forecasting_service = SarimaxForecastingService(redis_client)
    optimization_service = InventoryOptimizationService(forecasting_service)
    
    # Generate sustainability metrics
    sustainability_metrics = optimization_service.generate_sustainability_metrics(consumption_data)
    
    # Calculate carrying costs and optimization opportunities
    # Fix: Handle Decimal types properly
    inventory_value_result = db.query(
        func.sum(Inventory.current_stock * HygieneProduct.cost_per_unit)
    ).join(HygieneProduct, Inventory.product_id == HygieneProduct.id).scalar()
    
    # Convert to float and handle None case
    total_inventory_value = float(inventory_value_result) if inventory_value_result else 0.0

    # Use Decimal for precise calculations
    carrying_cost_rate = Decimal('0.25')
    excess_inventory_rate = Decimal('0.15')
    
    # Convert total_inventory_value to Decimal for calculations
    total_inventory_decimal = Decimal(str(total_inventory_value))

    analysis = {
        "inventory_value": round(float(total_inventory_decimal), 2),
        "carrying_cost_percentage": 25.0,
        "annual_carrying_cost": round(float(total_inventory_decimal * carrying_cost_rate), 2),
        "optimization_opportunities": {
            "excess_inventory_value": round(float(total_inventory_decimal * excess_inventory_rate), 2),
            "potential_cost_reduction": round(float(total_inventory_decimal * excess_inventory_rate * carrying_cost_rate), 2),
            "storage_space_savings": "12%",
            "cash_flow_improvement": round(float(total_inventory_decimal * excess_inventory_rate), 2)
        },
        "sustainability_metrics": sustainability_metrics,
        "recommendations": [
            "Implement ABC analysis for inventory prioritization",
            "Set up automated reorder points based on AI predictions",
            "Consolidate suppliers to reduce variety and improve bulk discounts",
            "Implement Just-In-Time delivery for high-turnover items"
        ]
    }
    
    return analysis