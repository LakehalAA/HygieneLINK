from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class HygieneProduct(Base):
    __tablename__ = "hygiene_products"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # toilet_paper, hand_sanitizer, soap, etc.
    brand = Column(String(100))
    unit_type = Column(String(50))  # rolls, bottles, dispensers
    cost_per_unit = Column(Float)
    sustainability_score = Column(Float)  # 0-100 rating
    certifications = Column(Text)  # JSON string of certifications
    supplier_id = Column(String, ForeignKey("suppliers.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="products")
    consumption_records = relationship("ConsumptionData", back_populates="product")

class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    address = Column(Text)
    reliability_score = Column(Float, default=85.0)  # Based on delivery performance
    sustainability_rating = Column(String(10))  # A, B, C, D grades
    certifications = Column(Text)  # JSON string
    cardano_wallet_address = Column(String(255))  # For blockchain payments
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    products = relationship("HygieneProduct", back_populates="supplier")

class ConsumptionData(Base):
    __tablename__ = "consumption_data"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, ForeignKey("hygiene_products.id"))
    facility_id = Column(String, nullable=False)  # Building/office identifier
    department = Column(String(100))  # IT, Marketing, Operations, etc.
    quantity_consumed = Column(Float, nullable=False)
    consumption_date = Column(DateTime, nullable=False)
    weather_condition = Column(String(50))  # External factor
    employee_count = Column(Integer)  # For normalization
    special_events = Column(Text)  # Conference, flu season, etc.
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("HygieneProduct", back_populates="consumption_records")

class PredictionModel(Base):
    __tablename__ = "prediction_models"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    model_name = Column(String(100), nullable=False)  # SARIMAX_toilet_paper
    product_category = Column(String(100))
    facility_id = Column(String)
    model_parameters = Column(Text)  # JSON string of SARIMAX params
    accuracy_score = Column(Float)  # Model performance metric
    last_trained = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, ForeignKey("hygiene_products.id"))
    facility_id = Column(String, nullable=False)
    current_stock = Column(Float, nullable=False)
    minimum_threshold = Column(Float, default=50.0)
    maximum_capacity = Column(Float)
    last_restocked = Column(DateTime)
    predicted_depletion_date = Column(DateTime)  # From SARIMAX
    auto_reorder_enabled = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("HygieneProduct")