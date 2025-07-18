from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.hygiene_products import HygieneProduct, Supplier
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json

router = APIRouter()

class ComplianceStatus(BaseModel):
    overall_score: float
    certifications_active: int
    certifications_expiring: int
    compliance_violations: int
    last_audit_date: str

class CertificationItem(BaseModel):
    id: str
    name: str
    type: str
    status: str
    expiry_date: Optional[str]
    issuing_body: str
    product_name: str
    supplier_name: str

@router.get("/status", response_model=ComplianceStatus)
async def get_compliance_status(
    facility_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get overall compliance status"""
    
    # Query products and suppliers with certifications
    products = db.query(HygieneProduct, Supplier).join(
        Supplier, HygieneProduct.supplier_id == Supplier.id
    ).all()
    
    total_certifications = 0
    active_certifications = 0
    expiring_certifications = 0
    
    thirty_days_from_now = datetime.now() + timedelta(days=30)
    
    for product, supplier in products:
        # Parse product certifications
        if product.certifications:
            try:
                product_certs = json.loads(product.certifications)
                for cert in product_certs:
                    total_certifications += 1
                    
                    if cert.get('status') == 'active':
                        active_certifications += 1
                        
                        # Check if expiring soon
                        expiry_str = cert.get('expiry_date')
                        if expiry_str:
                            expiry_date = datetime.fromisoformat(expiry_str)
                            if expiry_date <= thirty_days_from_now:
                                expiring_certifications += 1
            except:
                pass
        
        # Parse supplier certifications
        if supplier.certifications:
            try:
                supplier_certs = json.loads(supplier.certifications)
                for cert in supplier_certs:
                    total_certifications += 1
                    if cert.get('status') == 'active':
                        active_certifications += 1
            except:
                pass
    
    # Calculate compliance score
    compliance_score = (active_certifications / max(total_certifications, 1)) * 100
    
    return ComplianceStatus(
        overall_score=round(compliance_score, 1),
        certifications_active=active_certifications,
        certifications_expiring=expiring_certifications,
        compliance_violations=0,  # Mock - would implement violation tracking
        last_audit_date=(datetime.now() - timedelta(days=45)).isoformat()
    )

@router.get("/certifications", response_model=List[CertificationItem])
async def get_certifications(
    status: Optional[str] = None,  # active, expiring, expired
    db: Session = Depends(get_db)
):
    """Get detailed certification information"""
    
    certifications = []
    
    # Query products and suppliers
    products = db.query(HygieneProduct, Supplier).join(
        Supplier, HygieneProduct.supplier_id == Supplier.id
    ).all()
    
    for product, supplier in products:
        # Process product certifications
        if product.certifications:
            try:
                product_certs = json.loads(product.certifications)
                for cert in product_certs:
                    certifications.append(CertificationItem(
                        id=f"prod_{product.id}_{cert.get('name', 'unknown')}",
                        name=cert.get('name', 'Unknown Certification'),
                        type='product',
                        status=cert.get('status', 'unknown'),
                        expiry_date=cert.get('expiry_date'),
                        issuing_body=cert.get('issuing_body', 'Unknown'),
                        product_name=product.name,
                        supplier_name=supplier.name
                    ))
            except:
                pass
        
        # Process supplier certifications
        if supplier.certifications:
            try:
                supplier_certs = json.loads(supplier.certifications)
                for cert in supplier_certs:
                    certifications.append(CertificationItem(
                        id=f"supp_{supplier.id}_{cert.get('name', 'unknown')}",
                        name=cert.get('name', 'Unknown Certification'),
                        type='supplier',
                        status=cert.get('status', 'unknown'),
                        expiry_date=cert.get('expiry_date'),
                        issuing_body=cert.get('issuing_body', 'Unknown'),
                        product_name="N/A",
                        supplier_name=supplier.name
                    ))
            except:
                pass
    
    # Filter by status if provided
    if status:
        if status == "expiring":
            thirty_days_from_now = datetime.now() + timedelta(days=30)
            certifications = [
                cert for cert in certifications 
                if cert.expiry_date and datetime.fromisoformat(cert.expiry_date) <= thirty_days_from_now
            ]
        else:
            certifications = [cert for cert in certifications if cert.status == status]
    
    return certifications

@router.get("/audit-trail")
async def get_audit_trail(
    facility_id: Optional[str] = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get compliance audit trail and history"""
    
    # Mock audit trail data (would implement proper audit logging)
    audit_events = [
        {
            "id": "audit_001",
            "timestamp": (datetime.now() - timedelta(days=2)).isoformat(),
            "event_type": "certification_renewal",
            "description": "Organic certification renewed for Eco-Friendly Toilet Paper",
            "user": "system",
            "facility_id": "facility_001",
            "severity": "info"
        },
        {
            "id": "audit_002",
            "timestamp": (datetime.now() - timedelta(days=5)).isoformat(),
            "event_type": "compliance_check",
            "description": "Automated compliance check completed - 2 items require attention",
            "user": "system",
            "facility_id": "facility_002",
            "severity": "warning"
        },
        {
            "id": "audit_003",
            "timestamp": (datetime.now() - timedelta(days=10)).isoformat(),
            "event_type": "supplier_verification",
            "description": "Supplier Green Valley Organic verified for Fair Trade compliance",
            "user": "compliance_manager",
            "facility_id": "facility_001",
            "severity": "info"
        }
    ]
    
    if facility_id:
        audit_events = [event for event in audit_events if event["facility_id"] == facility_id]
    
    return {
        "total_events": len(audit_events),
        "events": audit_events,
        "summary": {
            "info_events": len([e for e in audit_events if e["severity"] == "info"]),
            "warning_events": len([e for e in audit_events if e["severity"] == "warning"]),
            "error_events": len([e for e in audit_events if e["severity"] == "error"])
        }
    }