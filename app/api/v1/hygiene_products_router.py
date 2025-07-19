from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.hygiene_products import HygieneProduct
from app.schemas.schemas import (
    HygieneProductCreate,
    HygieneProductResponse,
    HygieneProductUpdate
)
from app.core.database import get_db
from typing import List

router = APIRouter()

@router.post("/", response_model=HygieneProductResponse)
def create_product(product_in: HygieneProductCreate, db: Session = Depends(get_db)):
    product = HygieneProduct(**product_in.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/", response_model=List[HygieneProductResponse])
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(HygieneProduct).offset(skip).limit(limit).all()

@router.get("/{product_id}", response_model=HygieneProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(HygieneProduct).filter(HygieneProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=HygieneProductResponse)
def update_product(product_id: str, product_in: HygieneProductUpdate, db: Session = Depends(get_db)):
    product = db.query(HygieneProduct).filter(HygieneProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product_in.dict(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
def delete_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(HygieneProduct).filter(HygieneProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}