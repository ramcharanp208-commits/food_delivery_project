from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from datetime import datetime


# ==================== User Schemas ====================
class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None
    address: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None
    address: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Token Schemas ====================
class Token(BaseModel):
    access_token: str
    token_type: str
    user: "UserResponse"


class TokenData(BaseModel):
    email: Optional[str] = None


# ==================== Restaurant Schemas ====================
class RestaurantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    cuisine: str = Field(..., min_length=1, max_length=100)
    rating: Optional[float] = Field(default=4.0, ge=0, le=5)
    image_url: Optional[str] = None
    delivery_fee: Optional[float] = Field(default=30.0, ge=0)
    delivery_time_minutes: Optional[int] = Field(default=30, ge=1)


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    cuisine: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    image_url: Optional[str] = None
    delivery_fee: Optional[float] = Field(None, ge=0)
    delivery_time_minutes: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class MenuItemBrief(BaseModel):
    id: int
    name: str
    price: float
    image_url: Optional[str] = None
    category: Optional[str] = None
    is_available: bool

    class Config:
        from_attributes = True


class RestaurantResponse(RestaurantBase):
    id: int
    is_active: bool
    created_at: datetime
    items: List[MenuItemBrief] = []

    class Config:
        from_attributes = True


# ==================== Menu Item Schemas ====================
class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    image_url: Optional[str] = None
    category: Optional[str] = "Main Course"
    is_available: Optional[bool] = True


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    image_url: Optional[str] = None
    category: Optional[str] = None
    is_available: Optional[bool] = None


class MenuItemResponse(MenuItemBase):
    id: int
    restaurant_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Cart Schemas ====================
class CartItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = Field(default=1, ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)


class CartItemResponse(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    menu_item: MenuItemResponse

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: int
    user_id: int
    restaurant_id: Optional[int] = None
    restaurant_name: Optional[str] = None
    items: List[CartItemResponse] = []
    total_amount: float = 0.0
    delivery_fee: float = 0.0
    grand_total: float = 0.0

    class Config:
        from_attributes = True


# ==================== Order Schemas ====================
class OrderCreate(BaseModel):
    delivery_address: str = Field(..., min_length=5)
    payment_method: str = Field(default="COD", pattern="^(COD|CARD|UPI)$")


class OrderItemResponse(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    price: float
    menu_item_name: Optional[str] = None

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    restaurant_name: Optional[str] = None
    total_amount: float
    delivery_fee: float
    status: str
    delivery_address: Optional[str] = None
    payment_method: str
    payment_status: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(PENDING|CONFIRMED|PREPARING|OUT_FOR_DELIVERY|DELIVERED|CANCELLED)$")


# ==================== Generic Message Schema ====================
class MessageResponse(BaseModel):
    message: str
    success: bool = True


# Resolve forward references
Token.model_rebuild()