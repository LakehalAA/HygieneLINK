from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.hygiene_products import HygieneProduct, Inventory, Supplier
from app.schemas.inventory import (
    InventoryCreate,
    InventoryOut,
    InventoryUpdate
)
from app.core.database import get_db
from typing import List

router = APIRouter()

@router.post("/", response_model=InventoryOut)
def create_inventory(inventory_in: InventoryCreate, db: Session = Depends(get_db)):
    inventory = Inventory(**inventory_in.dict())
    db.add(inventory)
    db.commit()
    db.refresh(inventory)
    return inventory

@router.get("/", response_model=List[InventoryOut])
def list_inventories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    inventories = db.query(
        Inventory,
        HygieneProduct.name.label('product_name'),
        HygieneProduct.category.label('category'),
        Supplier.name.label('supplier_name')
    ).join(
        HygieneProduct, Inventory.product_id == HygieneProduct.id
    ).join(
        Supplier, HygieneProduct.supplier_id == Supplier.id
    ).offset(skip).limit(limit).all()
    
    # Transform the result to match your InventoryOut schema
    result = []
    for inventory, product_name, category, supplier_name in inventories:
        inventory_dict = {
            **inventory.__dict__,
            'product_name': product_name,
            'category': category,
            'supplier_name': supplier_name
        }
        result.append(inventory_dict)
    
    return result

@router.get("/{inventory_id}", response_model=InventoryOut)
def get_inventory(inventory_id: str, db: Session = Depends(get_db)):
    inventory_data = db.query(
        Inventory,
        HygieneProduct.name.label('product_name'),
        HygieneProduct.category.label('category'),
        Supplier.name.label('supplier_name')
    ).join(
        HygieneProduct, Inventory.product_id == HygieneProduct.id
    ).join(
        Supplier, HygieneProduct.supplier_id == Supplier.id
    ).filter(Inventory.id == inventory_id).first()
    
    if not inventory_data:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    inventory, product_name, category, supplier_name = inventory_data
    
    # Create the response with joined data
    inventory_dict = {
        **inventory.__dict__,
        'product_name': product_name,
        'category': category,
        'supplier_name': supplier_name
    }

@router.put("/{inventory_id}", response_model=InventoryOut)
def update_inventory(inventory_id: str, inventory_in: InventoryUpdate, db: Session = Depends(get_db)):
    inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    for key, value in inventory_in.dict(exclude_unset=True).items():
        setattr(inventory, key, value)
    db.commit()
    db.refresh(inventory)
    return inventory

@router.delete("/{inventory_id}")
def delete_inventory(inventory_id: str, db: Session = Depends(get_db)):
    inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    db.delete(inventory)
    db.commit()
    return {"message": "Inventory item deleted successfully"}