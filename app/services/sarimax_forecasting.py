import pandas as pd
import numpy as np
from decimal import Decimal
from app.models.hygiene_products import ConsumptionData
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.statespace.mlemodel import MLEResults
from sklearn.metrics import mean_absolute_percentage_error
import redis
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union, Any

class SarimaxForecastingService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.cache_ttl = 3600  # 1 hour cache
    
    def _convert_decimal_to_float(self, value) -> float:
        """Convert Decimal or other numeric types to float"""
        if isinstance(value, Decimal):
            return float(value)
        elif value is None:
            return 0.0
        else:
            return float(value)
    
    def prepare_time_series_data(self, consumption_records: List[ConsumptionData]) -> pd.DataFrame:
        """Convert consumption records to time series DataFrame with proper type handling"""
        data = []
        for record in consumption_records:
            data.append({
                'date': record.consumption_date,
                'quantity': self._convert_decimal_to_float(record.quantity_consumed),
                'employee_count': self._convert_decimal_to_float(record.employee_count),
                'weather': record.weather_condition,
                'special_events': 1 if bool(record.special_events) else 0
            })
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date').sort_index()
        
        # Resample to daily frequency, fill missing days
        df = df.resample('D').agg({
            'quantity': 'sum',
            'employee_count': 'mean',
            'weather': 'first',
            'special_events': 'max'
        }).fillna(0)

        if not isinstance(df, pd.DataFrame):
            raise ValueError("Resulting object is not a DataFrame")

        return df
    
    def create_exogenous_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create exogenous variables for SARIMAX"""
        exog = pd.DataFrame(index=df.index)
        
        # Employee count (normalized)
        employee_mean = float(df['employee_count'].mean())
        employee_std = float(df['employee_count'].std())
        if employee_std > 0:
            exog['employee_count_norm'] = (df['employee_count'] - employee_mean) / employee_std
        else:
            exog['employee_count_norm'] = 0.0
        
        # Special events indicator
        exog['special_events'] = df['special_events'].astype(float)
        
        # Day of week effects
        weekday_series = df.index.to_series().dt.dayofweek
        exog['monday'] = (weekday_series == 0).astype(float)
        exog['friday'] = (weekday_series == 4).astype(float)
        
        # Seasonal indicators
        month_series = df.index.to_series().dt.month
        exog['flu_season'] = ((month_series >= 11) | (month_series <= 3)).astype(float)
        
        return exog
    
    def _get_cache_value(self, key: str) -> Optional[str]:
        """Helper method to handle Redis cache retrieval with proper type handling"""
        try:
            cached_value = self.redis.get(key)
            if cached_value is None:
                return None

            # Handle bytes from Redis
            if isinstance(cached_value, bytes):
                return cached_value.decode('utf-8')
            elif isinstance(cached_value, str):
                return cached_value
            else:
                return str(cached_value)
        except Exception:
            return None
    
    def train_sarimax_model(self, product_id: str, facility_id: str, 
                           consumption_data: List[ConsumptionData]) -> Dict[str, Any]:
        """Train SARIMAX model for specific product/facility combination"""
        
        # Check cache first
        cache_key = f"sarimax_model:{product_id}:{facility_id}"
        cached_model_str = self._get_cache_value(cache_key)
        if cached_model_str:
            try:
                return json.loads(cached_model_str)
            except json.JSONDecodeError:
                pass  # Continue with training if cache is corrupted
        
        # Prepare data
        df = self.prepare_time_series_data(consumption_data)
        if len(df) < 30:  # Need minimum data points
            raise ValueError("Insufficient data for training (minimum 30 days required)")
        
        exog = self.create_exogenous_variables(df)
        
        # Split data for validation
        train_size = int(len(df) * 0.8)
        train_data = df['quantity'][:train_size]
        train_exog = exog[:train_size]
        test_data = df['quantity'][train_size:]
        test_exog = exog[train_size:]
        
        # Grid search for best parameters (simplified)
        best_aic = float('inf')
        best_params: Optional[tuple] = None
        best_model: Optional[MLEResults] = None
        
        # SARIMAX parameter combinations
        param_combinations = [
            ((1,1,1), (1,1,1,7)),   # Weekly seasonality
            ((1,1,2), (1,1,1,7)),
            ((2,1,1), (1,1,1,7)),
            ((1,1,1), (0,1,1,7)),
        ]
        
        for (p,d,q), (P,D,Q,s) in param_combinations:
            try:
                model = SARIMAX(
                    train_data,
                    exog=train_exog,
                    order=(p,d,q),
                    seasonal_order=(P,D,Q,s),
                    enforce_stationarity=False,
                    enforce_invertibility=False
                )
                fitted_model: Any = model.fit(disp=False, maxiter=100)
                
                # Check if model has required attributes
                if hasattr(fitted_model, 'aic') and fitted_model.aic < best_aic:
                    best_aic = fitted_model.aic
                    best_params = ((p,d,q), (P,D,Q,s))
                    best_model = fitted_model
                    
            except Exception as e:
                continue
        
        if best_model is None or best_params is None:
            raise ValueError("Could not fit SARIMAX model with any parameter combination")
        
        # Generate test predictions
        try:
            test_predictions = best_model.forecast(
                steps=len(test_data),
                exog=test_exog
            )
            
            # Ensure test_predictions is a numpy array
            if hasattr(test_predictions, 'values'):
                test_predictions = test_predictions.values
            
            accuracy = 100 - mean_absolute_percentage_error(test_data, test_predictions)
            
        except Exception as e:
            # If forecasting fails, set a default accuracy
            accuracy = 0.0
        
        # Prepare model metadata
        model_summary = ""
        if hasattr(best_model, 'summary'):
            try:
                model_summary = str(best_model.summary())
            except Exception:
                model_summary = "Summary not available"
        
        model_info: Dict[str, Any] = {
            'product_id': product_id,
            'facility_id': facility_id,
            'best_params': best_params,
            'aic': float(best_aic),
            'accuracy_score': float(accuracy),
            'trained_at': datetime.now().isoformat(),
            'training_data_points': len(df),
            'model_summary': model_summary
        }
        
        # Cache the model info
        try:
            self.redis.setex(cache_key, self.cache_ttl, json.dumps(model_info, default=str))
        except Exception:
            pass  # Continue even if caching fails
        
        return model_info
    
    def generate_forecast(self, product_id: str, facility_id: str, 
                     days_ahead: int = 30) -> Dict[str, Any]:
        """Generate consumption forecast for next N days using trained SARIMAX model"""
        
        cache_key = f"forecast:{product_id}:{facility_id}:{days_ahead}"
        cached_forecast_str = self._get_cache_value(cache_key)
        if cached_forecast_str:
            try:
                return json.loads(cached_forecast_str)
            except json.JSONDecodeError:
                pass  # Continue with forecast generation if cache is corrupted
        
        # Get trained model info from cache
        model_cache_key = f"sarimax_model:{product_id}:{facility_id}"
        cached_model_str = self._get_cache_value(model_cache_key)
        if not cached_model_str:
            raise ValueError(f"No trained model found for product {product_id} at facility {facility_id}")
        
        try:
            model_info = json.loads(cached_model_str)
            best_params = model_info['best_params']
            order, seasonal_order = best_params
        except (json.JSONDecodeError, KeyError):
            raise ValueError("Invalid model info in cache")
        
        # We need to get the original training data to refit the model
        # This is a limitation - in production, you'd want to save the fitted model object
        # For now, we'll need to re-query the consumption data
        from app.core.database import get_db
        from sqlalchemy.orm import Session
        
        # Get a database session (you might need to adjust this based on your setup)
        db = next(get_db())
        try:
            consumption_data = db.query(ConsumptionData).filter(
                ConsumptionData.product_id == product_id,
                ConsumptionData.facility_id == facility_id
            ).order_by(ConsumptionData.consumption_date).all()
            
            if len(consumption_data) < 30:
                raise ValueError("Insufficient historical data for forecasting")
            
            # Prepare historical data
            df = self.prepare_time_series_data(consumption_data)
            exog = self.create_exogenous_variables(df)
            
            # Refit the model with best parameters
            try:
                model = SARIMAX(
                    df['quantity'],
                    exog=exog,
                    order=order,
                    seasonal_order=seasonal_order,
                    enforce_stationarity=False,
                    enforce_invertibility=False
                )
                fitted_model = model.fit(disp=False, maxiter=100)
                
                # Verify model fitted successfully
                if not hasattr(fitted_model, 'params'):
                    raise ValueError("Model fitting failed - no parameters available")
                    
            except Exception as e:
                raise ValueError(f"Error fitting SARIMAX model: {str(e)}")
            
            # Generate forecast dates
            forecast_dates = pd.date_range(
                start=datetime.now().date(),
                periods=days_ahead,
                freq='D'
            )
            
            # Create future exogenous variables
            future_exog = self._create_future_exogenous_variables(
                forecast_dates, 
                df, 
                exog
            )

            print(f"Model params: {fitted_model}")
            print(f"Data shape: {df.shape}, Exog shape: {future_exog.shape}")
            
            # Generate forecast - using get_prediction for out-of-sample forecasting
            try:
                # For out-of-sample forecasting, we need to use get_prediction
                start_idx = len(df)
                end_idx = start_idx + days_ahead - 1
                
                # Create extended index for prediction
                extended_index = pd.date_range(
                    start=df.index[-1] + pd.Timedelta(days=1),
                    periods=days_ahead,
                    freq='D'
                )
                
                # Get prediction results
                prediction_results = fitted_model.get_prediction(
                    start=start_idx,
                    end=end_idx,
                    exog=future_exog,
                    dynamic=False
                )
                
                forecast_result = prediction_results.predicted_mean
                forecast_ci = prediction_results.conf_int()
                
            except Exception as e:
                # Fallback method using simple prediction
                try:
                    forecast_result = fitted_model.predict(
                        start=len(df),
                        end=len(df) + days_ahead - 1,
                        exog=future_exog
                    )
                    
                    # Create simple confidence intervals
                    residuals = fitted_model.resid
                    forecast_std = float(np.std(residuals)) if len(residuals) > 0 else float(np.std(df['quantity'])) * 0.15
                    
                    lower_bound = forecast_result - 1.96 * forecast_std
                    upper_bound = forecast_result + 1.96 * forecast_std
                    
                    # Create DataFrame to match expected format
                    forecast_ci = pd.DataFrame({
                        'lower quantity': lower_bound,
                        'upper quantity': upper_bound
                    })
                    
                except Exception as e2:
                    raise ValueError(f"All forecast methods failed. Original error: {str(e)}. Fallback error: {str(e2)}")
            
            # Convert to numpy arrays and ensure float types
            if hasattr(forecast_result, 'values'):
                predicted_consumption = forecast_result.values.astype(float)
            else:
                predicted_consumption = np.array(forecast_result, dtype=float)
            
            if hasattr(forecast_ci, 'values'):
                ci_values = forecast_ci.values.astype(float)
            else:
                ci_values = np.array(forecast_ci, dtype=float)
            
            # Ensure no negative consumption
            predicted_consumption = np.maximum(predicted_consumption, 0.0)
            lower_bound = np.maximum(ci_values[:, 0], 0.0)
            upper_bound = np.maximum(ci_values[:, 1], 0.0)
            
            # Calculate depletion date
            depletion_date = self._calculate_depletion_date(
                predicted_consumption, 
                forecast_dates
            )
            
            forecast_data: Dict[str, Any] = {
                'product_id': product_id,
                'facility_id': facility_id,
                'forecast_horizon': days_ahead,
                'generated_at': datetime.now().isoformat(),
                'model_params': best_params,
                'predictions': [
                    {
                        'date': date.strftime('%Y-%m-%d'),
                        'predicted_consumption': float(pred),
                        'lower_bound': float(low),
                        'upper_bound': float(high),
                        'confidence_level': 95
                    }
                    for date, pred, low, high in zip(
                        forecast_dates, predicted_consumption, lower_bound, upper_bound
                    )
                ],
                'total_predicted_consumption': float(predicted_consumption.sum()),
                'average_daily_consumption': float(predicted_consumption.mean()),
                'depletion_date': depletion_date
            }
            
            # Cache forecast
            try:
                self.redis.setex(cache_key, 1800, json.dumps(forecast_data, default=str))  # 30 min cache
            except Exception:
                pass  # Continue even if caching fails
            
            return forecast_data
            
        except Exception as e:
            raise ValueError(f"Error generating forecast: {str(e)}")
        finally:
            db.close()

    def _create_future_exogenous_variables(self, forecast_dates: pd.DatetimeIndex, 
                                     historical_df: pd.DataFrame, 
                                     historical_exog: pd.DataFrame) -> pd.DataFrame:
        """Create exogenous variables for future forecast periods"""
        future_exog = pd.DataFrame(index=forecast_dates)
        
        # Use recent average employee count for future predictions
        recent_employee_count = float(historical_df['employee_count'].tail(30).mean())
        
        # Normalize using same parameters as training data
        employee_mean = float(historical_df['employee_count'].mean())
        employee_std = float(historical_df['employee_count'].std())
        
        if employee_std > 0:
            future_exog['employee_count_norm'] = (recent_employee_count - employee_mean) / employee_std
        else:
            future_exog['employee_count_norm'] = 0.0
        
        # Assume no special events in future (conservative approach)
        future_exog['special_events'] = 0.0
        
        # Day of week effects
        weekday_series = forecast_dates.to_series().dt.dayofweek
        future_exog['monday'] = (weekday_series == 0).astype(float)
        future_exog['friday'] = (weekday_series == 4).astype(float)
        
        # Seasonal indicators
        month_series = forecast_dates.to_series().dt.month
        future_exog['flu_season'] = ((month_series >= 11) | (month_series <= 3)).astype(float)
        
        return future_exog
    
    def _calculate_depletion_date(self, predicted_consumption: np.ndarray, 
                                 forecast_dates: pd.DatetimeIndex, 
                                 current_stock: float = 100.0) -> Optional[str]:
        """Calculate when stock will be depleted based on predictions"""
        cumulative_consumption = np.cumsum(predicted_consumption)
        depletion_indices = np.where(cumulative_consumption >= current_stock)[0]
        
        if len(depletion_indices) > 0:
            depletion_date = forecast_dates[depletion_indices[0]]
            return str(depletion_date.strftime('%Y-%m-%d'))
        return None