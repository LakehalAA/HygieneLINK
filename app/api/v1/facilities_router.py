from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.hygiene_products import Facility
from app.schemas.schemas import (
    FacilityCreate, 
    FacilityResponse, 
    FacilityUpdate
)
from app.core.database import get_db

router = APIRouter()

@router.post("/", response_model=FacilityResponse)
def create_facility(facility_in: FacilityCreate, db: Session = Depends(get_db)):
    facility = Facility(**facility_in.dict())
    db.add(facility)
    db.commit()
    db.refresh(facility)
    return facility

@router.get("/", response_model=List[FacilityResponse])
def list_facilities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Facility).offset(skip).limit(limit).all()

@router.get("/{facility_id}", response_model=FacilityResponse)
def get_facility(facility_id: str, db: Session = Depends(get_db)):
    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    return facility

@router.put("/{facility_id}", response_model=FacilityResponse)
def update_facility(facility_id: str, facility_in: FacilityUpdate, db: Session = Depends(get_db)):
    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    for key, value in facility_in.dict(exclude_unset=True).items():
        setattr(facility, key, value)
    db.commit()
    db.refresh(facility)
    return facility

@router.delete("/{facility_id}")
def delete_facility(facility_id: str, db: Session = Depends(get_db)):
    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    db.delete(facility)
    db.commit()
    return {"message": "Facility deleted successfully"}
