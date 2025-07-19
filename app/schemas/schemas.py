from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    role_id: Optional[str]
    facility_id: Optional[str]
    is_active: Optional[bool]
    
class FacilityBase(BaseModel):
    name: str
    location: Optional[str]
    address: Optional[str]
    facility_type: Optional[str]
    employee_count: Optional[int] = 0
    operating_hours: Optional[dict] = {}
    contact_person: Optional[str]
    contact_email: Optional[str]
    is_active: Optional[bool] = True

class FacilityCreate(FacilityBase):
    pass

class FacilityResponse(FacilityBase):
    id: str
    created_at: datetime
    updated_at: datetime

class UserBase(BaseModel):
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    role_id: Optional[str]
    facility_id: Optional[str]
    is_active: Optional[bool] = True
    is_admin: Optional[bool] = False

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

class RoleBase(BaseModel):
    name: str
    description: Optional[str]
    permissions: Optional[dict] = {}
    is_active: Optional[bool] = True

    class Config:
        orm_mode = True

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: str
    created_at: datetime
    updated_at: datetime

class SupplierBase(BaseModel):
    name: str
    contact_email: Optional[EmailStr]
    contact_phone: Optional[str]
    address: Optional[str]
    reliability_score: Optional[float] = 85.0
    sustainability_rating: Optional[str]
    certifications: Optional[list] = []
    cardano_wallet_address: Optional[str]
    is_active: bool = True

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    contact_email: Optional[EmailStr]
    contact_phone: Optional[str]
    address: Optional[str]
    reliability_score: Optional[float]
    sustainability_rating: Optional[str]
    certifications: Optional[list]
    cardano_wallet_address: Optional[str]
    is_active: Optional[bool]

class SupplierResponse(SupplierBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class HygieneProductUpdate(BaseModel):
    brand: Optional[str]
    cost_per_unit: Optional[float]
    sustainability_score: Optional[float]
    certifications: Optional[list]
    product_specs: Optional[dict]
    supplier_id: Optional[str]
    is_active: Optional[bool]

class HygieneProductBase(BaseModel):
    name: str
    category: str
    brand: Optional[str]
    unit_type: str
    cost_per_unit: Optional[float]
    sustainability_score: Optional[float] = 0
    certifications: Optional[list] = []
    product_specs: Optional[dict] = {}
    supplier_id: Optional[str]
    is_active: Optional[bool] = True

class HygieneProductCreate(HygieneProductBase):
    pass

class HygieneProductResponse(HygieneProductBase):
    id: str
    created_at: datetime
    updated_at: datetime

class PurchaseOrderItemUpdate(BaseModel):
    received_quantity: Optional[float]
    quality_score: Optional[float]
    batch_number: Optional[str]
    expiry_date: Optional[date]
    notes: Optional[str]

class PurchaseOrderUpdate(BaseModel):
    expected_delivery_date: Optional[date]
    actual_delivery_date: Optional[date]
    status: Optional[str]
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    blockchain_tx_hash: Optional[str]
    notes: Optional[str]

class ConsumptionDataBase(BaseModel):
    product_id: str
    facility_id: str
    department: Optional[str]
    quantity_consumed: float
    consumption_date: date
    consumption_time: Optional[str]
    weather_condition: Optional[str]
    employee_count: Optional[int]
    special_events: Optional[str]
    cost_impact: Optional[float]
    sustainability_impact: Optional[dict] = {}
    recorded_by: Optional[str]

class ConsumptionDataCreate(ConsumptionDataBase):
    pass

class ConsumptionDataResponse(ConsumptionDataBase):
    id: str
    recorded_at: datetime

class PredictionModelBase(BaseModel):
    model_name: str
    product_category: Optional[str]
    facility_id: Optional[str]
    model_type: Optional[str] = "SARIMAX"
    model_parameters: Optional[dict] = {}
    training_data_points: Optional[int]
    accuracy_score: Optional[float]
    validation_metrics: Optional[dict] = {}
    last_trained: Optional[datetime]
    next_retrain_date: Optional[date]
    is_active: Optional[bool] = True

class PredictionModelCreate(PredictionModelBase):
    pass

class PredictionModelResponse(PredictionModelBase):
    id: str
    created_at: datetime

class PurchaseOrderItemBase(BaseModel):
    product_id: str
    quantity: float
    unit_price: float
    received_quantity: Optional[float] = 0
    quality_score: Optional[float]
    batch_number: Optional[str]
    expiry_date: Optional[date]
    notes: Optional[str]

class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    pass

class PurchaseOrderItemResponse(PurchaseOrderItemBase):
    id: str

class PurchaseOrderBase(BaseModel):
    po_number: str
    supplier_id: str
    facility_id: str
    order_date: date
    expected_delivery_date: Optional[date]
    actual_delivery_date: Optional[date]
    total_amount: Optional[float]
    currency: Optional[str] = "USD"
    status: Optional[str] = "pending"
    payment_terms: Optional[str]
    shipping_address: Optional[str]
    notes: Optional[str]
    created_by: Optional[str]
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    blockchain_tx_hash: Optional[str]

class PurchaseOrderCreate(PurchaseOrderBase):
    items: List[PurchaseOrderItemCreate]

class PurchaseOrderResponse(PurchaseOrderBase):
    id: str
    created_at: datetime
    updated_at: datetime
    items: List[PurchaseOrderItemResponse]

class BudgetBase(BaseModel):
    facility_id: str
    product_category: Optional[str]
    budget_year: int
    budget_month: Optional[int]
    allocated_amount: float
    spent_amount: Optional[float] = 0
    status: Optional[str] = "active"
    notes: Optional[str]

class BudgetCreate(BudgetBase):
    pass

class BudgetResponse(BudgetBase):
    id: str
    created_at: datetime
    updated_at: datetime

class KPIMetricBase(BaseModel):
    facility_id: str
    metric_name: str
    metric_category: Optional[str]
    metric_value: float
    target_value: Optional[float]
    unit_of_measure: Optional[str]
    calculation_method: Optional[str]
    measurement_date: date
    is_benchmark: Optional[bool] = False
    metadata: Optional[dict] = {}

class KPIMetricCreate(KPIMetricBase):
    pass

class KPIMetricResponse(KPIMetricBase):
    id: str
    created_at: datetime

class SustainabilityMetricBase(BaseModel):
    facility_id: str
    product_id: Optional[str]
    metric_date: date
    carbon_footprint_kg: Optional[float]
    water_usage_liters: Optional[float]
    waste_generated_kg: Optional[float]
    recycled_content_percentage: Optional[float]
    renewable_energy_percentage: Optional[float]
    packaging_waste_kg: Optional[float]
    transportation_emissions_kg: Optional[float]
    cost_savings_usd: Optional[float]
    efficiency_score: Optional[float]

class SustainabilityMetricCreate(SustainabilityMetricBase):
    pass

class SustainabilityMetricResponse(SustainabilityMetricBase):
    id: str
    created_at: datetime

class PerformanceBenchmarkBase(BaseModel):
    facility_id: str
    product_category: Optional[str]
    benchmark_type: str
    benchmark_name: str
    target_value: float
    current_value: Optional[float]
    achievement_percentage: Optional[float]
    measurement_period: Optional[str]
    unit_of_measure: Optional[str]
    is_active: Optional[bool] = True

class PerformanceBenchmarkCreate(PerformanceBenchmarkBase):
    pass

class PerformanceBenchmarkResponse(PerformanceBenchmarkBase):
    id: str
    created_at: datetime
    updated_at: datetime

class ROIMetricBase(BaseModel):
    facility_id: str
    initiative_name: str
    initiative_type: Optional[str]
    investment_amount: float
    savings_amount: Optional[float] = 0
    payback_period_months: Optional[int]
    start_date: date
    end_date: Optional[date]
    status: Optional[str] = "active"
    description: Optional[str]

class ROIMetricCreate(ROIMetricBase):
    pass

class ROIMetricResponse(ROIMetricBase):
    id: str
    created_at: datetime
    updated_at: datetime

class AuditScheduleBase(BaseModel):
    facility_id: str
    audit_type: str
    audit_name: str
    frequency_type: Optional[str]
    frequency_value: Optional[int]
    next_audit_date: Optional[date]
    assigned_auditor: Optional[str]
    checklist_template: Optional[dict] = {}
    is_active: Optional[bool] = True

class AuditScheduleCreate(AuditScheduleBase):
    pass

class AuditScheduleResponse(AuditScheduleBase):
    id: str
    created_at: datetime
    updated_at: datetime

class AuditRecordBase(BaseModel):
    audit_schedule_id: str
    facility_id: str
    audit_date: date
    auditor_name: Optional[str]
    audit_type: Optional[str]
    overall_score: Optional[float]
    compliance_percentage: Optional[float]
    findings: Optional[list] = []
    recommendations: Optional[list] = []
    corrective_actions: Optional[list] = []
    status: Optional[str] = "completed"
    report_document_url: Optional[str]
    follow_up_date: Optional[date]

class AuditRecordCreate(AuditRecordBase):
    pass

class AuditRecordResponse(AuditRecordBase):
    id: str
    created_at: datetime
    updated_at: datetime

class CertificationBase(BaseModel):
    name: str
    certification_type: Optional[str]
    issuing_body: Optional[str]
    product_id: Optional[str]
    supplier_id: Optional[str]
    certificate_number: Optional[str]
    issue_date: Optional[date]
    expiry_date: Optional[date]
    status: Optional[str] = "active"
    renewal_reminder_days: Optional[int] = 30
    compliance_score: Optional[float]
    certificate_document_url: Optional[str]
    audit_notes: Optional[str]

class CertificationCreate(CertificationBase):
    pass

class CertificationResponse(CertificationBase):
    id: str
    created_at: datetime
    updated_at: datetime

class NotificationBase(BaseModel):
    user_id: str
    facility_id: str
    notification_type: str
    title: str
    message: str
    is_read: Optional[bool] = False
    metadata: Optional[dict] = {}

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: str
    created_at: datetime

class ActivityLogBase(BaseModel):
    user_id: str
    facility_id: str
    activity_type: str
    description: Optional[str]
    metadata: Optional[dict] = {}

class ActivityLogCreate(ActivityLogBase):
    pass

class ActivityLogResponse(ActivityLogBase):
    id: str
    created_at: datetime

class FacilityUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Facility name")
    location: Optional[str] = Field(None, description="Physical location of the facility")
    contact_person: Optional[str] = Field(None, description="Primary contact person")
    contact_email: Optional[str] = Field(None, description="Contact email address")
    contact_phone: Optional[str] = Field(None, description="Contact phone number")
    capacity: Optional[int] = Field(None, description="Facility capacity")
    is_active: Optional[bool] = Field(None, description="Active status of the facility")