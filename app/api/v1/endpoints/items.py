from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemOut

router = APIRouter()


@router.post("/", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(data: ItemCreate, db: Session = Depends(get_db)):
    exists = db.query(Item).filter(Item.name == data.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Item ya existe")
    item = Item(name=data.name)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=List[ItemOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(Item).order_by(Item.id).all()
