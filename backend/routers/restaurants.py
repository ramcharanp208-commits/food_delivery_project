from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas
from database import get_db
from deps import get_current_user, get_current_admin_user

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.post("/", response_model=schemas.RestaurantResponse, status_code=status.HTTP_201_CREATED)
def create_restaurant(
    restaurant: schemas.RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    """Create a new restaurant (admin only)."""
    db_restaurant = models.Restaurant(
        name=restaurant.name,
        description=restaurant.description,
        cuisine=restaurant.cuisine,
        rating=restaurant.rating,
        image_url=restaurant.image_url,
        delivery_fee=restaurant.delivery_fee,
        delivery_time_minutes=restaurant.delivery_time_minutes,
    )
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant


@router.get("/", response_model=List[schemas.RestaurantResponse])
def get_restaurants(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    cuisine: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get all restaurants with optional filtering and search."""
    query = db.query(models.Restaurant).filter(models.Restaurant.is_active == True)

    if cuisine:
        query = query.filter(models.Restaurant.cuisine.ilike(f"%{cuisine}%"))

    if search:
        query = query.filter(
            (models.Restaurant.name.ilike(f"%{search}%"))
            | (models.Restaurant.cuisine.ilike(f"%{search}%"))
            | (models.Restaurant.description.ilike(f"%{search}%"))
        )

    restaurants = query.offset(skip).limit(limit).all()
    return restaurants


@router.get("/{restaurant_id}", response_model=schemas.RestaurantResponse)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    """Get a specific restaurant by ID."""
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )
    return restaurant


@router.put("/{restaurant_id}", response_model=schemas.RestaurantResponse)
def update_restaurant(
    restaurant_id: int,
    restaurant_update: schemas.RestaurantUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    """Update a restaurant (admin only)."""
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    update_data = restaurant_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(restaurant, field, value)

    db.commit()
    db.refresh(restaurant)
    return restaurant


@router.delete("/{restaurant_id}", response_model=schemas.MessageResponse)
def delete_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    """Delete a restaurant (admin only)."""
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    db.delete(restaurant)
    db.commit()
    return schemas.MessageResponse(message="Restaurant deleted successfully")