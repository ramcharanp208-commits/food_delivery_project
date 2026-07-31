from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db
from deps import get_current_user, get_current_admin_user

router = APIRouter(prefix="/orders", tags=["Orders"])


def build_order_response(order: models.Order) -> dict:
    """Build an order response dictionary with computed fields."""
    restaurant_name = None
    if order.restaurant:
        restaurant_name = order.restaurant.name

    items_data = []
    for item in order.items:
        item_data = {
            "id": item.id,
            "order_id": item.order_id,
            "menu_item_id": item.menu_item_id,
            "quantity": item.quantity,
            "price": item.price,
            "menu_item_name": item.menu_item.name if item.menu_item else None,
        }
        items_data.append(item_data)

    return {
        "id": order.id,
        "user_id": order.user_id,
        "restaurant_id": order.restaurant_id,
        "restaurant_name": restaurant_name,
        "total_amount": order.total_amount,
        "delivery_fee": order.delivery_fee,
        "status": order.status,
        "delivery_address": order.delivery_address,
        "payment_method": order.payment_method,
        "payment_status": order.payment_status,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "items": items_data,
    }


@router.post("/", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a new order from the user's cart."""
    # Get user's cart
    cart = db.query(models.Cart).filter(models.Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your cart is empty",
        )

    if not cart.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart has no restaurant associated",
        )

    # Get restaurant
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == cart.restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    # Calculate totals
    total_amount = 0.0
    for cart_item in cart.items:
        if cart_item.menu_item:
            total_amount += cart_item.menu_item.price * cart_item.quantity

    delivery_fee = restaurant.delivery_fee
    grand_total = total_amount + delivery_fee

    # Create order
    order = models.Order(
        user_id=current_user.id,
        restaurant_id=cart.restaurant_id,
        total_amount=grand_total,
        delivery_fee=delivery_fee,
        status="PENDING",
        delivery_address=order_data.delivery_address,
        payment_method=order_data.payment_method,
        payment_status="PENDING",
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Create order items from cart items
    for cart_item in cart.items:
        if cart_item.menu_item:
            order_item = models.OrderItem(
                order_id=order.id,
                menu_item_id=cart_item.menu_item_id,
                quantity=cart_item.quantity,
                price=cart_item.menu_item.price,
            )
            db.add(order_item)

    db.commit()

    # Clear the cart
    db.query(models.CartItem).filter(models.CartItem.cart_id == cart.id).delete()
    cart.restaurant_id = None
    db.commit()

    db.refresh(order)
    return build_order_response(order)


@router.get("/", response_model=List[schemas.OrderResponse])
def get_my_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get all orders for the current user."""
    orders = (
        db.query(models.Order)
        .filter(models.Order.user_id == current_user.id)
        .order_by(models.Order.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [build_order_response(order) for order in orders]


@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get a specific order by ID."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # Check if the order belongs to the current user (or admin)
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this order",
        )

    return build_order_response(order)


@router.put("/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(
    order_id: int,
    status_update: schemas.OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    """Update order status (admin only)."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    order.status = status_update.status

    # If order is delivered, mark payment as paid for COD
    if status_update.status == "DELIVERED" and order.payment_method == "COD":
        order.payment_status = "PAID"

    db.commit()
    db.refresh(order)
    return build_order_response(order)


@router.get("/admin/all", response_model=List[schemas.OrderResponse])
def get_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: str = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    """Get all orders (admin only)."""
    query = db.query(models.Order)
    if status_filter:
        query = query.filter(models.Order.status == status_filter)

    orders = (
        query.order_by(models.Order.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [build_order_response(order) for order in orders]