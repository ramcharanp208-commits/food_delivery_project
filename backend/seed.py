"""Seed script to populate the database with test data."""
import models
from database import engine, SessionLocal
from auth import get_password_hash

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()


def seed_data():
    # Check if data already exists
    if db.query(models.User).filter(models.User.email == "admin@swiggy.com").first():
        print("Seed data already exists. Skipping...")
        return

    # Create admin user
    admin = models.User(
        email="admin@swiggy.com",
        full_name="Admin User",
        phone="1234567890",
        address="Admin Office",
        hashed_password=get_password_hash("admin123"),
        is_admin=True,
    )
    db.add(admin)

    # Create regular test user
    test_user = models.User(
        email="user@swiggy.com",
        full_name="Test User",
        phone="9876543210",
        address="123 Main Street, Apartment 4B, City",
        hashed_password=get_password_hash("user123"),
    )
    db.add(test_user)
    db.commit()

    # Create restaurants
    restaurants_data = [
        {
            "name": "Biryani House",
            "description": "Authentic Hyderabadi biryani and Mughlai cuisine",
            "cuisine": "Mughlai",
            "rating": 4.5,
            "image_url": "https://images.unsplash.com/photo-1633945274405-b6c8063a8a1e?w=400",
            "delivery_fee": 30.0,
            "delivery_time_minutes": 35,
        },
        {
            "name": "Pizza Paradise",
            "description": "Wood-fired pizzas, pasta, and Italian favorites",
            "cuisine": "Italian",
            "rating": 4.3,
            "image_url": "https://images.unsplash.com/photo-1565299624946-b28f40a85ae2?w=400",
            "delivery_fee": 25.0,
            "delivery_time_minutes": 30,
        },
        {
            "name": "Burger Barn",
            "description": "Gourmet burgers, fries, and shakes",
            "cuisine": "American",
            "rating": 4.2,
            "image_url": "https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=400",
            "delivery_fee": 20.0,
            "delivery_time_minutes": 25,
        },
        {
            "name": "Spice Garden",
            "description": "Traditional South Indian thalis and snacks",
            "cuisine": "South Indian",
            "rating": 4.6,
            "image_url": "https://images.unsplash.com/photo-1631452180519-c5140c312d81?w=400",
            "delivery_fee": 35.0,
            "delivery_time_minutes": 40,
        },
        {
            "name": "Dragon Wok",
            "description": "Chinese and Thai cuisine, noodles, and dumplings",
            "cuisine": "Chinese",
            "rating": 4.4,
            "image_url": "https://images.unsplash.com/photo-1525755662774-0ce203733545?w=400",
            "delivery_fee": 30.0,
            "delivery_time_minutes": 35,
        },
    ]

    for r_data in restaurants_data:
        restaurant = models.Restaurant(**r_data)
        db.add(restaurant)
        db.commit()
        db.refresh(restaurant)

        # Add menu items for each restaurant
        if restaurant.name == "Biryani House":
            items = [
                ("Chicken Biryani", "Aromatic basmati rice with tender chicken", 249.0, "Main Course"),
                ("Mutton Biryani", "Slow-cooked mutton with fragrant rice", 329.0, "Main Course"),
                ("Veg Biryani", "Mixed vegetable biryani with saffron", 199.0, "Main Course"),
                ("Chicken 65", "Spicy deep-fried chicken appetizer", 179.0, "Starters"),
                ("Paneer Tikka", "Grilled cottage cheese with spices", 159.0, "Starters"),
                ("Gulab Jamun", "Sweet dumplings in sugar syrup", 89.0, "Desserts"),
            ]
        elif restaurant.name == "Pizza Paradise":
            items = [
                ("Margherita Pizza", "Classic pizza with tomato and mozzarella", 199.0, "Pizzas"),
                ("Pepperoni Pizza", "Loaded with pepperoni and cheese", 299.0, "Pizzas"),
                ("Veggie Supreme Pizza", "Garden vegetables with extra cheese", 279.0, "Pizzas"),
                ("Pasta Alfredo", "Creamy white sauce pasta", 179.0, "Pasta"),
                ("Garlic Bread", "Toasted bread with garlic butter", 99.0, "Sides"),
                ("Tiramisu", "Classic Italian dessert", 129.0, "Desserts"),
            ]
        elif restaurant.name == "Burger Barn":
            items = [
                ("Classic Cheeseburger", "Beef patty with cheese and veggies", 149.0, "Burgers"),
                ("Crispy Chicken Burger", "Fried chicken with special sauce", 179.0, "Burgers"),
                ("Veg Burger", "Plant-based patty with fresh veggies", 129.0, "Burgers"),
                ("French Fries", "Golden crispy fries", 89.0, "Sides"),
                ("Chocolate Shake", "Thick and creamy chocolate shake", 119.0, "Beverages"),
                ("Onion Rings", "Crispy battered onion rings", 99.0, "Sides"),
            ]
        elif restaurant.name == "Spice Garden":
            items = [
                ("Masala Dosa", "Crispy rice crepe with potato filling", 99.0, "Main Course"),
                ("Idli Sambar", "Steamed rice cakes with lentil soup", 79.0, "Main Course"),
                ("Vada", "Crispy fried lentil donuts", 69.0, "Starters"),
                ("Mini Meals", "Complete South Indian thali", 149.0, "Thalis"),
                ("Filter Coffee", "Traditional South Indian coffee", 39.0, "Beverages"),
                ("Payasam", "Rice pudding with jaggery and nuts", 59.0, "Desserts"),
            ]
        elif restaurant.name == "Dragon Wok":
            items = [
                ("Hakka Noodles", "Stir-fried noodles with vegetables", 139.0, "Noodles"),
                ("Chilli Chicken", "Spicy battered chicken in chili sauce", 179.0, "Starters"),
                ("Veg Manchurian", "Fried vegetable balls in spicy sauce", 149.0, "Main Course"),
                ("Schezwan Fried Rice", "Spicy fried rice with schezwan sauce", 129.0, "Rice"),
                ("Veg Spring Rolls", "Crispy rolls with vegetable filling", 99.0, "Starters"),
                ("Honey Noodles", "Sweet crispy noodles with honey", 89.0, "Desserts"),
            ]
        else:
            items = []

        for name, desc, price, category in items:
            menu_item = models.MenuItem(
                name=name,
                description=desc,
                price=price,
                category=category,
                restaurant_id=restaurant.id,
                image_url=f"https://images.unsplash.com/photo-1546069901-ba9599f7bde4?w=400",
            )
            db.add(menu_item)

        db.commit()

    print("Seed data created successfully!")
    print("\n--- Admin Login ---")
    print("Email: admin@swiggy.com")
    print("Password: admin123")
    print("\n--- Test User Login ---")
    print("Email: user@swiggy.com")
    print("Password: user123")
    print("\n5 restaurants with 30 menu items created.")


if __name__ == "__main__":
    seed_data()
    db.close()