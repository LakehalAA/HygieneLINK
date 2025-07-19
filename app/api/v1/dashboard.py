from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.schemas.dashboard import (
    DashboardMetrics, 
    ConsumptionTrend, 
    AlertItem, 
    AIInsight,
    SustainabilityMetrics
)
from app.dependencies import get_current_facility_id

router = APIRouter()

@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    facility_id: Optional[str] = Depends(get_current_facility_id),
    db: Session = Depends(get_db)
):
    """Get main dashboard KPI metrics"""
    
    # Mock data for now - replace with actual database queries
    return DashboardMetrics(
        active_products=13,
        total_facilities=5,
        active_suppliers=5,
        pending_reorders=3,
        monthly_consumption=2847.5,
        avg_consumption_per_employee=15.8,
        sustainability_score=82.3,
        cost_savings_percentage=12.5
    )

@router.get("/consumption-trends", response_model=List[ConsumptionTrend])
async def get_consumption_trends(
    days: int = Query(default=30, ge=1, le=365),
    facility_id: Optional[str] = Depends(get_current_facility_id),
    db: Session = Depends(get_db)
):
    """Get consumption trends with predictions"""
    
    # Mock trend data - replace with actual SARIMAX predictions
    trends = []
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        base_consumption = 50 + (i % 7) * 5  # Weekly pattern
        
        trends.append(ConsumptionTrend(
            date=date.date().isoformat(),
            consumption=base_consumption + (i % 3) * 2,
            predicted=base_consumption,
            facility_count=5 if not facility_id else 1
        ))
    
    return list(reversed(trends))

@router.get("/alerts", response_model=List[AlertItem])
async def get_active_alerts(
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$"),
    facility_id: Optional[str] = Depends(get_current_facility_id),
    db: Session = Depends(get_db)
):
    """Get active alerts and notifications"""
    
    # Mock alerts - replace with database queries
    alerts = [
        AlertItem(
            id="alert_001",
            type="reorder",
            severity="high",
            title="Low Stock Alert",
            description="Toilet paper stock critically low at Distribution Center",
            facility_id="33333333-3333-4333-c333-333333333333",
            product_name="Premium Toilet Paper",
            created_at=(datetime.now() - timedelta(hours=2)).isoformat()
        ),
        AlertItem(
            id="alert_002",
            type="compliance",
            severity="medium",
            title="Certification Renewal Due",
            description="Organic certification expires in 30 days",
            facility_id="11111111-1111-4111-a111-111111111111",
            product_name="Organic Liquid Soap",
            created_at=(datetime.now() - timedelta(hours=6)).isoformat()
        )
    ]
    
    if severity:
        alerts = [a for a in alerts if a.severity == severity]
    
    if facility_id:
        alerts = [a for a in alerts if a.facility_id == facility_id]
    
    return alerts

@router.get("/ai-insights", response_model=List[AIInsight])
async def get_ai_insights(
    facility_id: Optional[str] = Depends(get_current_facility_id),
    db: Session = Depends(get_db)
):
    """Get AI-powered insights and recommendations"""
    
    insights = [
        AIInsight(
            type="optimization",
            title="Bulk Purchase Opportunity",
            description="Consolidating orders could reduce costs by 15%",
            impact="Cost reduction: $450/month",
            confidence=89.5,
            action_required=True
        ),
        AIInsight(
            type="prediction",
            title="Seasonal Demand Increase",
            description="SARIMAX predicts 28% increase in sanitizer demand",
            impact="Inventory adjustment needed",
            confidence=94.2,
            action_required=True
        ),
        AIInsight(
            type="sustainability",
            title="Carbon Footprint Reduction",
            description="Eco-friendly suppliers could reduce footprint by 22%",
            impact="Environmental improvement",
            confidence=78.3,
            action_required=False
        )
    ]
    
    return insights

@router.get("/sustainability-metrics", response_model=SustainabilityMetrics)
async def get_sustainability_metrics(
    facility_id: Optional[str] = Depends(get_current_facility_id),
    db: Session = Depends(get_db)
):
    """Get sustainability and environmental impact metrics"""
    
    return SustainabilityMetrics(
        carbon_footprint={
            "current_month_kg": 1245.6,
            "previous_month_kg": 1398.2,
            "reduction_percentage": 10.9
        },
        waste_reduction={
            "current_efficiency": 78.5,
            "target_efficiency": 85.0,
            "improvement_potential": 6.5
        },
        sustainable_products={
            "percentage": 45.2,
            "total_products": 13,
            "sustainable_count": 6
        },
        certifications={
            "organic": 3,
            "fair_trade": 2,
            "carbon_neutral": 1,
            "recycled_content": 4
        },
        cost_savings={
            "monthly_savings": 850.25,
            "annual_projection": 10203.00,
            "roi_percentage": 15.8
        }
    )