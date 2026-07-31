from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas
from database import get_db
from deps import get_current_user, get_current_admin_user

router = APIRouter(prefix="/restaurants/{restaurant_id}/items", tags=["Menu Items"])


@router.post("/", response_model=schemas.MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item(
    restaurant_id: int,
    item: schemas.MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    """Add a new menu item to a restaurant (admin only)."""
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    db_item = models.MenuItem(
        name=item.name,
        description=item.description,
        price=item.price,
        image_url=item.image_url,
        category=item.category,
        is_available=item.is_available,
        restaurant_id=restaurant_id,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/", response_model=List[schemas.MenuItemResponse])
def get_menu_items(
    restaurant_id: int,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get all menu items for a restaurant with optional filtering."""
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    query = db.query(models.MenuItem).filter(models.MenuItem.restaurant_id == restaurant_id)

    if category:
        query = query.filter(models.MenuItem.category.ilike(f"%{category}%"))

    if search:
        query = query.filter(
            (models.MenuItem.name.ilike(f"%{search}%"))
            | (models.MenuItem.description.ilike(f"%{search}%"))
        )

    items = query.all()
    return items


@router.get("/{item_id}", response_model=schemas.MenuItemResponse)
def get_menu_item(
    restaurant_id: int,
    item_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific menu item."""
    item = (
        db.query(models.MenuItem)
        .filter(models.MenuItem.id == item_id, models.MenuItem.restaurant_id == restaurant_id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )
    return item


@router.put("/{item_id}", response_model=schemas.MenuItemResponse)
def update_menu_item(
    restaurant_id: int,
    item_id: int,
    item_update: schemas.MenuItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    """Update a menu item (admin only)."""
    item = (
        db.query(models.MenuItem)
        .filter(models.MenuItem.id == item_id, models.MenuItem.restaurant_id == restaurant_id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", response_model=schemas.MessageResponse)
def delete_menu_item(
    restaurant_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    """Delete a menu item (admin only)."""
    item = (
        db.query(models.MenuItem)
        .filter(models.MenuItem.id == item_id, models.MenuItem.restaurant_id == restaurant_id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    db.delete(item)
    db.commit()
    return schemas.MessageResponse(message="Menu item deleted successfully")