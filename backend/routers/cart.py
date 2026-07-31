from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import models, schemas
from database import get_db
from deps import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


def get_or_create_cart(db: Session, user: models.User) -> models.Cart:
    """Get the user's cart or create one if it doesn't exist."""
    cart = db.query(models.Cart).filter(models.Cart.user_id == user.id).first()
    if not cart:
        cart = models.Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def calculate_cart_totals(cart: models.Cart) -> dict:
    """Calculate the total amount, delivery fee, and grand total for a cart."""
    total_amount = 0.0
    for cart_item in cart.items:
        if cart_item.menu_item:
            total_amount += cart_item.menu_item.price * cart_item.quantity

    delivery_fee = 0.0
    if cart.restaurant:
        delivery_fee = cart.restaurant.delivery_fee

    grand_total = total_amount + delivery_fee if total_amount > 0 else 0.0

    return {
        "total_amount": total_amount,
        "delivery_fee": delivery_fee,
        "grand_total": grand_total,
    }


def build_cart_response(cart: models.Cart, db: Session) -> dict:
    """Build a cart response dictionary with all computed fields."""
    # Force load of relationships
    _ = cart.items
    restaurant_name = None
    if cart.restaurant:
        restaurant_name = cart.restaurant.name

    totals = calculate_cart_totals(cart)

    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "restaurant_id": cart.restaurant_id,
        "restaurant_name": restaurant_name,
        "items": cart.items,
        "total_amount": totals["total_amount"],
        "delivery_fee": totals["delivery_fee"],
        "grand_total": totals["grand_total"],
    }


@router.post("/items", response_model=schemas.CartResponse)
def add_item_to_cart(
    item: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Add a menu item to the cart or update quantity if already exists."""
    # Find the menu item
    menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == item.menu_item_id).first()
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    if not menu_item.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This item is currently unavailable",
        )

    # Get or create cart
    cart = get_or_create_cart(db, current_user)

    # Check if adding item from a different restaurant
    if cart.restaurant_id is not None and cart.restaurant_id != menu_item.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your cart already has items from another restaurant. Please clear your cart first.",
        )

    # Set restaurant if cart is empty
    if cart.restaurant_id is None:
        cart.restaurant_id = menu_item.restaurant_id

    # Check if item already in cart
    existing_item = (
        db.query(models.CartItem)
        .filter(
            models.CartItem.cart_id == cart.id,
            models.CartItem.menu_item_id == item.menu_item_id,
        )
        .first()
    )

    if existing_item:
        existing_item.quantity += item.quantity
    else:
        cart_item = models.CartItem(
            cart_id=cart.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart)
    return build_cart_response(cart, db)


@router.get("/", response_model=schemas.CartResponse)
def get_cart(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get the current user's cart."""
    cart = get_or_create_cart(db, current_user)
    return build_cart_response(cart, db)


@router.put("/items/{menu_item_id}", response_model=schemas.CartResponse)
def update_cart_item_quantity(
    menu_item_id: int,
    item_update: schemas.CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Update the quantity of a cart item."""
    cart = get_or_create_cart(db, current_user)

    cart_item = (
        db.query(models.CartItem)
        .filter(
            models.CartItem.cart_id == cart.id,
            models.CartItem.menu_item_id == menu_item_id,
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in cart",
        )

    cart_item.quantity = item_update.quantity
    db.commit()
    db.refresh(cart)
    return build_cart_response(cart, db)


@router.delete("/items/{menu_item_id}", response_model=schemas.CartResponse)
def remove_item_from_cart(
    menu_item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Remove an item from the cart."""
    cart = get_or_create_cart(db, current_user)

    cart_item = (
        db.query(models.CartItem)
        .filter(
            models.CartItem.cart_id == cart.id,
            models.CartItem.menu_item_id == menu_item_id,
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in cart",
        )

    db.delete(cart_item)
    db.commit()
    db.refresh(cart)

    # If cart is empty, reset restaurant
    if not cart.items:
        cart.restaurant_id = None
        db.commit()
        db.refresh(cart)

    return build_cart_response(cart, db)


@router.delete("/", response_model=schemas.MessageResponse)
def clear_cart(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Clear all items from the cart."""
    cart = db.query(models.Cart).filter(models.Cart.user_id == current_user.id).first()
    if not cart:
        return schemas.MessageResponse(message="Cart is already empty")

    # Delete all cart items
    db.query(models.CartItem).filter(models.CartItem.cart_id == cart.id).delete()
    cart.restaurant_id = None
    db.commit()

    return schemas.MessageResponse(message="Cart cleared successfully")