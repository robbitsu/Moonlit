from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import Player, InventoryItem
from dependencies import get_db
from schemas import InventoryItemCreate, InventoryItemUpdate, InventoryItemRead, InventoryItemDelete

router = APIRouter(prefix="/inventory", tags=["inventory"])

# Inventory endpoints are slightly different from other endpoints:
# - They must be associated with a player
# - We need to grab the player, and then check if the item already exists and increment the quantity if it does, or create a new item if it doesn't.

@router.post("/{player_id}", response_model=InventoryItemRead, status_code=201)
async def create_inventory_item(player_id: int, new_inventory_item: InventoryItemCreate, db: Session = Depends(get_db)) -> InventoryItemRead:
    db_player = db.get(Player, player_id)
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")
    # Does the player already have this item?
    db_inventory_item = db.scalar(select(InventoryItem).where(InventoryItem.item_name == new_inventory_item.item_name, InventoryItem.player_id == player_id))
    if db_inventory_item:
        db_inventory_item.quantity += new_inventory_item.quantity
    else:
        db_inventory_item = InventoryItem(**new_inventory_item.model_dump(), player=db_player)
        db.add(db_inventory_item)
    db.flush()
    db.refresh(db_inventory_item)
    return InventoryItemRead.model_validate(db_inventory_item)

@router.get("/{player_id}", response_model=list[InventoryItemRead])
async def get_inventory_items(player_id: int, db: Session = Depends(get_db)) -> list[InventoryItemRead]:
    db_player = db.get(Player, player_id)
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")
    inventory_items = db.scalars(select(InventoryItem).where(InventoryItem.player_id == player_id)).all()
    return [InventoryItemRead.model_validate(inventory_item) for inventory_item in inventory_items]


@router.put("/{player_id}", response_model=InventoryItemRead)
async def update_inventory_item(player_id: int, inventory_item: InventoryItemUpdate, db: Session = Depends(get_db)) -> InventoryItemRead:
    db_player = db.get(Player, player_id)
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")
    db_inventory_item = db.scalar(select(InventoryItem).where(InventoryItem.item_name == inventory_item.item_name, InventoryItem.player_id == player_id))
    if not db_inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    if inventory_item.quantity is not None:
        if inventory_item.quantity == 0:
            db.delete(db_inventory_item)
            db.flush()
            return Response(status_code=204)
        db_inventory_item.quantity = inventory_item.quantity
    if inventory_item.item_name is not None:
        db_inventory_item.item_name = inventory_item.item_name
    db.flush()
    db.refresh(db_inventory_item)
    return InventoryItemRead.model_validate(db_inventory_item)

@router.delete("/{player_id}", status_code=204)
async def delete_inventory_item(player_id: int, inventory_item: InventoryItemDelete, db: Session = Depends(get_db)):
    db_player = db.get(Player, player_id)
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")
    db_inventory_item = db.scalar(select(InventoryItem).where(InventoryItem.item_name == inventory_item.item_name, InventoryItem.player_id == player_id))
    if not db_inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    db.delete(db_inventory_item)
    return Response(status_code=204)