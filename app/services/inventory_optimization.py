from typing import Dict, List
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

from app.models.hygiene_products import ConsumptionData
from app.services.sarimax_forecasting import SarimaxForecastingService

class InventoryOptimizationService:
    def __init__(self, forecasting_service: SarimaxForecastingService):
        self.forecasting_service = forecasting_service
    
    def calculate_optimal_reorder_point(self, product_id: str, facility_id: str,
                                       lead_time_days: int = 7) -> Dict:
        """Calculate optimal reorder point using SARIMAX forecasts"""
        
        # Get forecast for lead time period
        forecast = self.forecasting_service.generate_forecast(
            product_id, facility_id, days_ahead=lead_time_days * 2
        )
        
        # Calculate consumption during lead time
        lead_time_consumption = sum([
            pred['predicted_consumption'] 
            for pred in forecast['predictions'][:lead_time_days]
        ])
        
        # Safety stock (based on forecast uncertainty)
        forecast_variance = sum([
            (pred['upper_bound'] - pred['lower_bound']) / 3.92  # Convert 95% CI to std
            for pred in forecast['predictions'][:lead_time_days]
        ])
        
        safety_stock = 1.65 * forecast_variance  # 95% service level
        
        reorder_point = lead_time_consumption + safety_stock
        
        return {
            'product_id': product_id,
            'facility_id': facility_id,
            'reorder_point': round(reorder_point, 2),
            'lead_time_consumption': round(lead_time_consumption, 2),
            'safety_stock': round(safety_stock, 2),
            'service_level': 95,
            'calculated_at': datetime.now().isoformat()
        }
    
    def _extract_scalar(self, value) -> float:
        """Extract scalar value from pandas objects or return as-is"""
        if hasattr(value, 'item'):
            return float(value.item())
        elif hasattr(value, 'iloc'):
            return float(value.iloc[0])
        else:
            return float(value)

    def generate_sustainability_metrics(self, consumption_data: List[ConsumptionData]) -> Dict:
        """Calculate sustainability KPIs"""
        
        total_consumption = sum([record.quantity_consumed for record in consumption_data]) if consumption_data else 0
        total_employees = sum([record.employee_count for record in consumption_data]) / len(consumption_data) if consumption_data else 0
        
        # Consumption per employee (efficiency metric)
        consumption_per_employee = total_consumption / total_employees if bool(total_employees > 0) else 0
        
        # Waste reduction opportunity (mock calculation)
        predicted_optimal = total_consumption * 0.85  # 15% reduction potential
        waste_reduction_opportunity = total_consumption - predicted_optimal
        
        # Carbon footprint estimation (mock - would use real product data)
        carbon_per_unit = 0.1  # kg CO2 per unit (varies by product)
        total_carbon_footprint = total_consumption * carbon_per_unit
        
        return {
            'total_consumption': round(self._extract_scalar(total_consumption), 2),
            'consumption_per_employee': round(self._extract_scalar(consumption_per_employee), 2),
            'waste_reduction_opportunity': round(self._extract_scalar(waste_reduction_opportunity), 2),
            'potential_savings_percentage': 15.0,
            'carbon_footprint_kg': round(self._extract_scalar(total_carbon_footprint), 2),
            'sustainability_score': 78.5,
            'calculation_date': datetime.now().isoformat()
        }