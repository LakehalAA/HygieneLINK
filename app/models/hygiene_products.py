from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Date, Time, Numeric, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB, ENUM
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

Base = declarative_base()

class ProductCategoryEnum(enum.Enum):
    TOILET_PAPER = "toilet_paper"
    HAND_SANITIZER = "hand_sanitizer"
    DISINFECTANT = "Disinfectant"
    SOAP = "soap"
    PAPER_TOWELS = "paper_towels"
    TISSUES = "tissues"
    CLEANING_SUPPLIES = "cleaning_supplies"
    DISPENSERS = "dispensers"

class UnitTypeEnum(enum.Enum):
    ROLLS = "rolls"
    BOTTLES = "bottles"
    DISPENSERS = "dispensers"
    BOXES = "boxes"
    PACKS = "packs"
    LITERS = "liters"
    PIECES = "pieces"

class AlertTypeEnum(enum.Enum):
    LOW_STOCK = "low_stock"
    CONSUMPTION_SPIKE = "consumption_spike"
    DELIVERY_DELAY = "delivery_delay"
    QUALITY_ISSUE = "quality_issue"
    BUDGET_EXCEEDED = "budget_exceeded"

class AlertSeverityEnum(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceStatusEnum(enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING = "pending"
    SUSPENDED = "suspended"

# Models
class Facility(Base):
    __tablename__ = "facilities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    address = Column(Text)
    facility_type = Column(String(100))
    employee_count = Column(Integer, default=0)
    operating_hours = Column(JSONB, default=lambda: {})
    contact_person = Column(String(255))
    contact_email = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="facility")
    inventory = relationship("Inventory", back_populates="facility")
    consumption_data = relationship("ConsumptionData", back_populates="facility")
    purchase_orders = relationship("PurchaseOrder", back_populates="facility")
    budgets = relationship("Budget", back_populates="facility")
    alerts = relationship("Alert", back_populates="facility")
    forecasts = relationship("Forecast", back_populates="facility")
    kpi_metrics = relationship("KPIMetric", back_populates="facility")
    sustainability_metrics = relationship("SustainabilityMetric", back_populates="facility")
    performance_benchmarks = relationship("PerformanceBenchmark", back_populates="facility")
    roi_metrics = relationship("ROIMetric", back_populates="facility")
    audit_schedules = relationship("AuditSchedule", back_populates="facility")
    audit_records = relationship("AuditRecord", back_populates="facility")
    reorder_rules = relationship("ReorderRule", back_populates="facility")
    prediction_models = relationship("PredictionModel", back_populates="facility")
    ai_insights = relationship("AIInsight", back_populates="facility")
    notifications = relationship("Notification", back_populates="facility")
    activity_logs = relationship("ActivityLog", back_populates="facility")

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    permissions = Column(JSONB, default=lambda: {})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(50))
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    role = relationship("Role", back_populates="users")
    facility = relationship("Facility", back_populates="users")
    notifications = relationship("Notification", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user")

class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    address = Column(Text)
    reliability_score = Column(Numeric(5, 2), default=85.0)
    sustainability_rating = Column(String(10))
    certifications = Column(JSONB, default=lambda: [])
    cardano_wallet_address = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = relationship("HygieneProduct", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    certifications_rel = relationship("Certification", back_populates="supplier")
    reorder_rules = relationship("ReorderRule", back_populates="supplier")

class HygieneProduct(Base):
    __tablename__ = "hygiene_products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    category = Column(ENUM(ProductCategoryEnum), nullable=False)
    brand = Column(String(100))
    unit_type = Column(ENUM(UnitTypeEnum), nullable=False)
    cost_per_unit = Column(Numeric(10, 2))
    sustainability_score = Column(Numeric(5, 2), default=0)
    certifications = Column(JSONB, default=lambda: [])
    product_specs = Column(JSONB, default=lambda: {})
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="products")
    consumption_records = relationship("ConsumptionData", back_populates="product")
    inventory = relationship("Inventory", back_populates="product")
    purchase_order_items = relationship("PurchaseOrderItem", back_populates="product")
    forecasts = relationship("Forecast", back_populates="product")
    certifications_rel = relationship("Certification", back_populates="product")
    sustainability_metrics = relationship("SustainabilityMetric", back_populates="product")
    reorder_rules = relationship("ReorderRule", back_populates="product")
    alerts = relationship("Alert", back_populates="product")
    ai_insights = relationship("AIInsight", back_populates="product")

class ConsumptionData(Base):
    __tablename__ = "consumption_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("hygiene_products.id"))
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"))
    department = Column(String(100))
    quantity_consumed = Column(Numeric(10, 2), nullable=False)
    consumption_date = Column(Date, nullable=False)
    consumption_time = Column(Time)
    weather_condition = Column(String(50))
    employee_count = Column(Integer)
    special_events = Column(Text)
    cost_impact = Column(Numeric(10, 2))
    sustainability_impact = Column(JSONB, default=lambda: {})
    recorded_at = Column(DateTime, default=datetime.utcnow)
    recorded_by = Column(String(255))
    
    # Relationships
    product = relationship("HygieneProduct", back_populates="consumption_records")
    facility = relationship("Facility", back_populates="consumption_data")

class PredictionModel(Base):
    __tablename__ = "prediction_models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(100), nullable=False)
    product_category = Column(ENUM(ProductCategoryEnum))
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"))
    model_type = Column(String(50), default="SARIMAX")
    model_parameters = Column(JSONB, default=lambda: {})
    training_data_points = Column(Integer)
    accuracy_score = Column(Numeric(5, 2))
    validation_metrics = Column(JSONB, default=lambda: {})
    last_trained = Column(DateTime)
    next_retrain_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    facility = relationship("Facility", back_populates="prediction_models")
    forecasts = relationship("Forecast", back_populates="model")

class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("hygiene_products.id"))
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"))
    current_stock = Column(Numeric(10, 2), nullable=False)
    minimum_threshold = Column(Numeric(10, 2), default=50.0)
    maximum_capacity = Column(Numeric(10, 2))
    reorder_point = Column(Numeric(10, 2))
    last_restocked = Column(DateTime)
    predicted_depletion_date = Column(Date)
    auto_reorder_enabled = Column(Boolean, default=True)
    storage_location = Column(String(255))
    batch_numbers = Column(JSONB, default=lambda: [])
    expiry_dates = Column(JSONB, default=lambda: [])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("HygieneProduct", back_populates="inventory")
    facility = relationship("Facility", back_populates="inventory")

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    po_number = Column(String(100), nullable=False, unique=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"))
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"))
    order_date = Column(Date, nullable=False)
    expected_delivery_date = Column(Date)
    actual_delivery_date = Column(Date)
    total_amount = Column(Numeric(12, 2))
    currency = Column(String(3), default="USD")
    status = Column(String(50), default="pending")
    payment_terms = Column(String(100))
    shipping_address = Column(Text)
    notes = Column(Text)
    created_by = Column(String(255))
    approved_by = Column(String(255))
    approved_at = Column(DateTime)
    blockchain_tx_hash = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_orders")
    facility = relationship("Facility", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order")

class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("hygiene_products.id"))
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    # total_price is computed column in PostgreSQL
    received_quantity = Column(Numeric(10, 2), default=0)
    quality_score = Column(Numeric(5, 2))
    batch_number = Column(String(255))
    expiry_date = Column(Date)
    notes = Column(Text)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("HygieneProduct", back_populates="purchase_order_items")

class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"))
    product_category = Column(ENUM(ProductCategoryEnum))
    budget_year = Column(Integer, nullable=False)
    budget_month = Column(Integer)
    allocated_amount = Column(Numeric(12, 2), nullable=False)
    spent_amount = Column(Numeric(12, 2), default=0)
    # remaining_amount and utilization_percentage are computed columns in PostgreSQL
    status = Column(String(50), default="active")
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    facility = relationship("Facility", back_populates="budgets")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_type = Column(ENUM(AlertTypeEnum), nullable=False)
    severity = Column(ENUM(AlertSeverityEnum), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("hygiene_products.id"))
    threshold_value = Column(Numeric(10, 2))
    current_value = Column(Numeric(10, 2))
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(255))
    acknowledged_at = Column(DateTime)
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(String(255))
    resolved_at = Column(DateTime)
    auto_generated = Column(Boolean, default=True)
    meta_data = Column(JSONB, default=lambda: {})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    facility = relationship("Facility", back_populates="alerts")
    product = relationship("HygieneProduct", back_populates="alerts")

class Forecast(Base):
    __tablename__ = "forecasts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey("prediction_models.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("hygiene_products.id"))
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"))
    forecast_date = Column(Date, nullable=False)
    predicted_consumption = Column(Numeric(10, 2), nullable=False)
    confidence_lower = Column(Numeric(10, 2))
    confidence_upper = Column(Numeric(10, 2))
    confidence_level = Column(Numeric(5, 2), default=95.0)
    forecast_horizon_days = Column(Integer)
    external_factors = Column(JSONB, default=lambda: {})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    model = relationship("PredictionModel", back_populates="forecasts")
    product = relationship("HygieneProduct", back_populates="forecasts")
    facility = relationship("Facility", back_populates="forecasts")

class KPIMetric(Base):
    __tablename__ = "kpi_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"))
    metric_name = Column(String(100), nullable=False)
    metric_category = Column(String(50))
    metric_value = Column(Numeric(15, 4), nullable=False)
    target_value = Column(Numeric(15, 4))
    unit_of_measure = Column(String(20))
    calculation_method = Column(Text)
    measurement_date = Column(Date, nullable=False)
    is_benchmark = Column(Boolean, default=False)
    meta_data = Column(JSONB, default=lambda: {})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    facility = relationship("Facility", back_populates="kpi_metrics")

class SustainabilityMetric(Base):
    __tablename__ = "sustainability_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("hygiene_products.id"))
    metric_date = Column(Date, nullable=False)
    carbon_footprint_kg = Column(Numeric(10, 3))
    water_usage_liters = Column(Numeric(10, 2))
    waste_generated_kg = Column(Numeric(10, 2))
    recycled_content_percentage = Column(Numeric(5, 2))
    renewable_energy_percentage = Column(Numeric(5, 2))
    packaging_waste_kg = Column(Numeric(10, 2))
    transportation_emissions_kg = Column(Numeric(10, 2))
    cost_savings_usd = Column(Numeric(10, 2))
    efficiency_score = Column(Numeric(5, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    facility = relationship("Facility", back_populates="sustainability_metrics")
    product = relationship("HygieneProduct", back_populates="sustainability_metrics")

class PerformanceBenchmark(Base):
    __tablename__ = "performance_benchmarks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"))
    product_category = Column(ENUM(ProductCategoryEnum))
    benchmark_type = Column(String(100), nullable=False)
    benchmark_name = Column(String(255), nullable=False)
    target_value = Column(Numeric(15, 4), nullable=False)
    current_value = Column(Numeric(15, 4))
    achievement_percentage = Column(Numeric(5, 2))
    measurement_period = Column(String(50))
    unit_of_measure = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    facility = relationship("Facility", back_populates="performance_benchmarks")

class ROIMetric(Base):
    __tablename__ = "roi_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"))
    initiative_name = Column(String(255), nullable=False)
    initiative_type = Column(String(100))
    investment_amount = Column(Numeric(12, 2), nullable=False)
    savings_amount = Column(Numeric(12, 2), default=0)
    # roi_percentage is computed column in PostgreSQL
    payback_period_months = Column(Integer)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    status = Column(String(50), default="active")
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    facility = relationship("Facility", back_populates="roi_metrics")

class AuditSchedule(Base):
    __tablename__ = "audit_schedules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"))
    audit_type = Column(String(100), nullable=False)
    audit_name = Column(String(255), nullable=False)
    frequency_type = Column(String(50))
    frequency_value = Column(Integer)
    next_audit_date = Column(Date)
    assigned_auditor = Column(String(255))
    checklist_template = Column(JSONB, default=lambda: {})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    facility = relationship("Facility", back_populates="audit_schedules")
    audit_records = relationship("AuditRecord", back_populates="audit_schedule")

class AuditRecord(Base):
    __tablename__ = "audit_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_schedule_id = Column(UUID(as_uuid=True), ForeignKey("audit_schedules.id"))
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"))
    audit_date = Column(Date, nullable=False)
    auditor_name = Column(String(255))
    audit_type = Column(String(100))
    overall_score = Column(Numeric(5, 2))
    compliance_percentage = Column(Numeric(5, 2))
    findings = Column(JSONB, default=lambda: [])
    recommendations = Column(JSONB, default=lambda: [])
    corrective_actions = Column(JSONB, default=lambda: [])
    status = Column(String(50), default="completed")
    report_document_url = Column(Text)
    follow_up_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    audit_schedule = relationship("AuditSchedule", back_populates="audit_records")
    facility = relationship("Facility", back_populates="audit_records")

class Certification(Base):
    __tablename__ = "certifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    certification_type = Column(String(100))
    issuing_body = Column(String(255))
    product_id = Column(UUID(as_uuid=True), ForeignKey("hygiene_products.id"))
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"))
    certificate_number = Column(String(255))
    issue_date = Column(Date)
    expiry_date = Column(Date)
    status = Column(ENUM(ComplianceStatusEnum), default="active")
    renewal_reminder_days = Column(Integer, default=30)
    compliance_score = Column(Numeric(5, 2))
    certificate_document_url = Column(Text)
    audit_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("HygieneProduct", back_populates="certifications_rel")
    supplier = relationship("Supplier", back_populates="certifications_rel")

class ReorderRule(Base):
    __tablename__ = "reorder_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("hygiene_products.id"))
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"))
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"))
    rule_name = Column(String(255), nullable=False)
    trigger_type = Column(String(50), nullable=False)
    trigger_value = Column(Numeric(10, 2))
    reorder_quantity = Column(Numeric(10, 2), nullable=False)
    lead_time_days = Column(Integer, default=7)
    safety_stock_days = Column(Integer, default=3)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)
    seasonal_adjustment = Column(JSONB, default=lambda: {})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("HygieneProduct", back_populates="reorder_rules")
    facility = relationship("Facility", back_populates="reorder_rules")
    supplier = relationship("Supplier", back_populates="reorder_rules")

class AIInsight(Base):
    __tablename__ = "ai_insights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    insight_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    impact_description = Column(Text)
    confidence_score = Column(Numeric(5, 2))
    priority_score = Column(Integer)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("hygiene_products.id"))
    action_required = Column(Boolean, default=False)
    is_implemented = Column(Boolean, default=False)
    implemented_by = Column(String(255))
    implemented_at = Column(DateTime)
    estimated_savings = Column(Numeric(10, 2))
    estimated_impact_percentage = Column(Numeric(5, 2))
    valid_until = Column(Date)
    meta_data = Column(JSONB, default=lambda: {})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    facility = relationship("Facility", back_populates="ai_insights")
    product = relationship("HygieneProduct", back_populates="ai_insights")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"))
    title = Column(String(255), nullable=False)
    message = Column(Text)
    notification_type = Column(String(50))
    is_read = Column(Boolean, default=False)
    meta_data = Column(JSONB, default=lambda: {})
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")
    facility = relationship("Facility", back_populates="notifications")

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"))
    action = Column(String(255), nullable=False)
    description = Column(Text)
    action_type = Column(String(50))
    meta_data = Column(JSONB, default=lambda: {})
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="activity_logs")
    facility = relationship("Facility", back_populates="activity_logs")