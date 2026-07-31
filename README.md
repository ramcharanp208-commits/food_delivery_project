# 🍔 FoodExpress - Food Delivery App

A full-stack food delivery web application built with **FastAPI** (backend) and **Vanilla HTML/CSS/JS** (frontend). Inspired by Swiggy, this app allows users to browse restaurants, view menus, add items to cart, place orders, and track order history.

![FastAPI](https://img.shields.io/badge/FastAPI-0.140.13-009688?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-71B333?logo=sqlalchemy)
![Render](https://img.shields.io/badge/Deploy-Render-46E3B7?logo=render)

---

## ✨ Features

### 🔐 Authentication
- User registration with email, name, phone, address
- Login with JWT token authentication
- Persistent login (token stored in localStorage)
- User profile view & update
- Admin & regular user roles

### 🍽️ Restaurants & Menu
- Browse all restaurants with images, ratings, delivery info
- Search restaurants by name, cuisine, or description
- View restaurant details with full menu
- Menu items grouped by category
- Veg/non-veg indicators

### 🛒 Cart
- Add items to cart
- Update item quantities (+/-)
- Remove individual items
- Clear entire cart
- Cart bill summary (item total + delivery fee + grand total)
- Cart count badge in navbar
- Single-restaurant cart (can't mix items from different restaurants)

### 📦 Orders
- Place orders with delivery address & payment method
- Payment options: COD, Card, UPI
- View order history with status tracking
- Order statuses: PENDING → CONFIRMED → PREPARING → OUT_FOR_DELIVERY → DELIVERED
- Admin can view all orders & update status

### 🎨 UI/UX
- Swiggy-inspired orange theme
- Fully responsive (mobile + desktop)
- SPA-style navigation (no page reloads)
- Toast notifications for feedback
- Loading spinners
- Empty states with helpful messages
- Modal dialogs for auth & checkout

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI 0.140.13 |
| **Database** | SQLite (via SQLAlchemy 2.0) |
| **Authentication** | JWT (python-jose) + bcrypt (passlib) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript (ES6+) |
| **Server** | Uvicorn (ASGI) |
| **Deployment** | Render.com |

---

## 📁 Project Structure

```
swigg_example/
├── backend/
│   ├── main.py              # FastAPI app entry point + static file serving
│   ├── config.py            # App configuration (env vars)
│   ├── database.py           # SQLAlchemy database setup
│   ├── models.py            # Database models (User, Restaurant, MenuItem, Cart, Order)
│   ├── schemas.py           # Pydantic validation schemas
│   ├── auth.py              # Password hashing & JWT token utilities
│   ├── deps.py              # Dependency injection (get_current_user, admin)
│   ├── seed.py              # Database seeding script (test data)
│   ├── test_api.py          # API test cases
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # /auth - register, login, profile
│       ├── restaurants.py   # /restaurants - CRUD operations
│       ├── menu.py          # /restaurants/{id}/items - menu CRUD
│       ├── cart.py          # /cart - cart management
│       └── orders.py        # /orders - order creation & tracking
├── frontend/
│   ├── index.html           # Main HTML with navbar, modals, views
│   ├── style.css           # Complete CSS with Swiggy theme
│   └── script.js            # JavaScript SPA logic + API integration
├── requirements.txt         # Python dependencies
├── render.yaml             # Render deployment config
├── Procfile                 # Alternative deployment config
├── .env                     # Environment variables
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- pip (Python package manager)
- A web browser

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd swigg_example
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Seed the database** (creates test data: 2 users, 5 restaurants, 30 menu items):
   ```bash
   cd backend
   python seed.py
   ```

4. **Start the server:**
   ```bash
   cd backend
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

5. **Open the app:**
   - Go to **http://127.0.0.1:8000/** in your browser
   - The backend serves both the API and frontend!

---

## 🖥️ Run Commands

| Action | Command |
|--------|---------|
| **Start server** | `cd backend; uvicorn main:app --reload --host 127.0.0.1 --port 8000` |
| **Seed database** | `cd backend; python seed.py` |
| **Run tests** | `cd backend; python test_api.py` |
| **Open frontend** | Open `http://127.0.0.1:8000/` in browser |
| **API docs** | Open `http://127.0.0.1:8000/docs` in browser (Swagger UI) |
| **Alternative API docs** | Open `http://127.0.0.1:8000/redoc` in browser (ReDoc) |

---

## 📡 API Endpoints

### Authentication (`/auth`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Register a new user | ❌ |
| POST | `/auth/login` | Login (OAuth2 form: username=email) | ❌ |
| GET | `/auth/me` | Get current user profile | ✅ |
| PUT | `/auth/me` | Update current user profile | ✅ |

### Restaurants (`/restaurants`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/restaurants/` | List restaurants (supports `?search=` & `?cuisine=`) | ❌ |
| GET | `/restaurants/{id}` | Get restaurant details | ❌ |
| POST | `/restaurants/` | Create restaurant | 👑 Admin |
| PUT | `/restaurants/{id}` | Update restaurant | 👑 Admin |
| DELETE | `/restaurants/{id}` | Delete restaurant | 👑 Admin |

### Menu Items (`/restaurants/{restaurant_id}/items`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/restaurants/{id}/items/` | List menu items (supports `?category=` & `?search=`) | ❌ |
| GET | `/restaurants/{id}/items/{item_id}` | Get specific menu item | ❌ |
| POST | `/restaurants/{id}/items/` | Add menu item | 👑 Admin |
| PUT | `/restaurants/{id}/items/{item_id}` | Update menu item | 👑 Admin |
| DELETE | `/restaurants/{id}/items/{item_id}` | Delete menu item | 👑 Admin |

### Cart (`/cart`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/cart/` | Get user's cart | ✅ |
| POST | `/cart/items` | Add item to cart (body: `{menu_item_id, quantity}`) | ✅ |
| PUT | `/cart/items/{menu_item_id}` | Update quantity (body: `{quantity}`) | ✅ |
| DELETE | `/cart/items/{menu_item_id}` | Remove item from cart | ✅ |
| DELETE | `/cart/` | Clear entire cart | ✅ |

### Orders (`/orders`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/orders/` | Create order from cart (body: `{delivery_address, payment_method}`) | ✅ |
| GET | `/orders/` | Get user's orders | ✅ |
| GET | `/orders/{id}` | Get specific order | ✅ |
| PUT | `/orders/{id}/status` | Update order status | 👑 Admin |
| GET | `/orders/admin/all` | Get all orders (supports `?status=`) | 👑 Admin |

### Other
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api` | API information |
| GET | `/health` | Health check (for Render) |
| GET | `/docs` | Swagger UI documentation |
| GET | `/redoc` | ReDoc documentation |

---

## 🔑 Test Credentials

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@swiggy.com | admin123 |
| **User** | user@swiggy.com | user123 |

---

## 🌐 Deployment on Render

### Method 1: Blueprint (Recommended)

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **"New+"** → **"Blueprint"**
4. Select your GitHub repository
5. Render auto-detects `render.yaml` and creates the service
6. Click **"Apply"** and wait for deployment
7. Your app will be live at: `https://foodexpress-api.onrender.com`

### Method 2: Manual Setup

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New+"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `foodexpress-api`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
5. Add Environment Variables:
   - `PYTHON_VERSION` = `3.11.9`
   - `SECRET_KEY` = (generate random)
   - `ALGORITHM` = `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES` = `10080`
   - `DATABASE_URL` = `sqlite:///./swiggy.db`
   - `DEBUG` = `False`
6. Click **"Create Web Service"**

### ⚠️ Note on SQLite
Render's free tier uses ephemeral storage, so the SQLite database resets on each deploy. For production, use Render's managed PostgreSQL. For demo purposes, SQLite works fine.

---

## 🗄️ Database Models

- **User**: id, email, full_name, phone, address, hashed_password, is_active, is_admin, created_at
- **Restaurant**: id, name, description, cuisine, rating, image_url, delivery_fee, delivery_time_minutes, is_active
- **MenuItem**: id, name, description, price, image_url, category, is_available, restaurant_id
- **Cart**: id, user_id, restaurant_id, items[], total_amount, delivery_fee, grand_total
- **Order**: id, user_id, restaurant_id, total_amount, delivery_fee, status, delivery_address, payment_method, payment_status, created_at, items[]

---

## 📝 License

This project is for educational purposes.

---

## 👨‍💻 Built With

- **Backend**: FastAPI + SQLAlchemy + JWT Auth
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **Database**: SQLite
- **Deployment**: Render.com