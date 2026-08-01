// ==================== CONFIG ====================
// Dynamic API URL: uses localhost when opening file directly,
// uses same origin (empty string) when served from backend (Render)
const API_URL = "https://onrender.com";

// ==================== STATE ====================
let authToken = localStorage.getItem("token") || null;
let currentUser = JSON.parse(localStorage.getItem("user") || "null");
let currentView = "home";
let currentRestaurantId = null;
let cartData = null;
let searchTimeout = null;

// ==================== API HELPER ====================
async function apiCall(endpoint, method = "GET", body = null, isFormData = false) {
    const headers = {};
    if (authToken) {
        headers["Authorization"] = `Bearer ${authToken}`;
    }
    let payload = undefined;
    if (body) {
        if (isFormData) {
            payload = body; // FormData object
        } else {
            headers["Content-Type"] = "application/json";
            payload = JSON.stringify(body);
        }
    }
    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method,
            headers,
            body: payload,
        });
        const data = await response.json();
        if (!response.ok) {
            const msg = data.detail || "Something went wrong";
            throw new Error(typeof msg === "object" ? JSON.stringify(msg) : msg);
        }
        return data;
    } catch (error) {
        if (error.message === "Failed to fetch") {
            throw new Error("Cannot connect to server. Is the backend running on " + API_URL + "?");
        }
        throw error;
    }
}

// ==================== TOAST ====================
function showToast(message, type = "") {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.className = "toast show " + type;
    setTimeout(() => {
        toast.className = "toast";
    }, 3000);
}

// ==================== AUTH ====================
function openAuthModal() {
    document.getElementById("auth-modal").classList.add("show");
}

function closeAuthModal() {
    document.getElementById("auth-modal").classList.remove("show");
}

function switchAuthTab(tab) {
    const loginForm = document.getElementById("login-form");
    const regForm = document.getElementById("register-form");
    const tabLogin = document.getElementById("tab-login");
    const tabReg = document.getElementById("tab-register");
    if (tab === "login") {
        loginForm.classList.remove("hidden");
        regForm.classList.add("hidden");
        tabLogin.classList.add("active");
        tabReg.classList.remove("active");
    } else {
        loginForm.classList.add("hidden");
        regForm.classList.remove("hidden");
        tabLogin.classList.remove("active");
        tabReg.classList.add("active");
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;
    try {
        const formData = new FormData();
        formData.append("username", email);
        formData.append("password", password);
        const data = await apiCall("/auth/login", "POST", formData, true);
        authToken = data.access_token;
        currentUser = data.user;
        localStorage.setItem("token", authToken);
        localStorage.setItem("user", JSON.stringify(currentUser));
        closeAuthModal();
        updateNavForUser();
        showToast("Login successful! Welcome, " + currentUser.full_name, "success");
        navigateTo("home");
    } catch (error) {
        showToast("Login failed: " + error.message, "error");
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const body = {
        email: document.getElementById("reg-email").value,
        full_name: document.getElementById("reg-name").value,
        phone: document.getElementById("reg-phone").value || null,
        address: document.getElementById("reg-address").value || null,
        password: document.getElementById("reg-password").value,
    };
    try {
        await apiCall("/auth/register", "POST", body);
        showToast("Registration successful! Please login.", "success");
        switchAuthTab("login");
        document.getElementById("login-email").value = body.email;
    } catch (error) {
        showToast("Registration failed: " + error.message, "error");
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    cartData = null;
    updateNavForUser();
    showToast("Logged out successfully", "success");
    navigateTo("home");
}

function toggleUserDropdown() {
    if (!authToken) {
        openAuthModal();
        return;
    }
    document.getElementById("user-dropdown").classList.toggle("show");
}

// Close dropdown when clicking outside
document.addEventListener("click", (e) => {
    const userMenu = document.getElementById("user-menu");
    const dropdown = document.getElementById("user-dropdown");
    if (userMenu && !userMenu.contains(e.target)) {
        dropdown.classList.remove("show");
    }
});

function updateNavForUser() {
    const userInfo = document.getElementById("user-info");
    const navUser = document.getElementById("nav-user");
    if (authToken && currentUser) {
        navUser.innerHTML = `👤 ${currentUser.full_name.split(" ")[0]}`;
        userInfo.innerHTML = `<strong>${currentUser.full_name}</strong>${currentUser.email}`;
    } else {
        navUser.innerHTML = "👤 Login";
        userInfo.innerHTML = "";
    }
    updateCartCount();
}

// ==================== NAVIGATION ====================
function navigateTo(view, restaurantId = null) {
    currentView = view;
    currentRestaurantId = restaurantId;
    document.getElementById("user-dropdown").classList.remove("show");
    const main = document.getElementById("main-content");
    main.innerHTML = `<div class="loading"><div class="spinner"></div>Loading...</div>`;
    switch (view) {
        case "home":
            renderHome();
            break;
        case "restaurant":
            renderRestaurantDetail(restaurantId);
            break;
        case "cart":
            renderCart();
            break;
        case "orders":
            renderOrders();
            break;
        case "profile":
            renderProfile();
            break;
        default:
            renderHome();
    }
}

// ==================== HOME / RESTAURANTS ====================
async function renderHome() {
    const main = document.getElementById("main-content");
    main.innerHTML = `
        <h2>Restaurants Near You</h2>
        <div class="grid-container" id="restaurant-list">
            <div class="loading"><div class="spinner"></div>Loading restaurants...</div>
        </div>
    `;
    try {
        const restaurants = await apiCall("/restaurants/");
        renderRestaurantList(restaurants);
    } catch (error) {
        document.getElementById("restaurant-list").innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <h3>Could not load restaurants</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}

function renderRestaurantList(restaurants) {
    const container = document.getElementById("restaurant-list");
    if (!restaurants || restaurants.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🍽️</div>
                <h3>No restaurants found</h3>
                <p>Try a different search or check back later.</p>
            </div>
        `;
        return;
    }
    container.innerHTML = "";
    restaurants.forEach((r) => {
        const card = document.createElement("div");
        card.className = "card";
        card.onclick = () => navigateTo("restaurant", r.id);
        const img = r.image_url
            ? `<img class="card-image" src="${r.image_url}" alt="${r.name}" onerror="this.style.display='none'"/>`
            : `<div class="card-image" style="display:flex;align-items:center;justify-content:center;font-size:3rem;">🍽️</div>`;
        card.innerHTML = `
            ${img}
            <div class="card-body">
                <h3>${r.name}</h3>
                <p class="cuisine">${r.cuisine}</p>
                <div class="card-meta">
                    <span class="rating">★ ${r.rating || "N/A"}</span>
                    <span class="delivery-info">⏱ ${r.delivery_time_minutes || 30} min</span>
                    <span class="delivery-info">₹${r.delivery_fee || 0} delivery</span>
                </div>
                <p class="cuisine">${r.description || ""}</p>
            </div>
        `;
        container.appendChild(card);
    });
}

// ==================== SEARCH ====================
function handleSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(async () => {
        const query = document.getElementById("search-input").value.trim();
        if (currentView !== "home") {
            navigateTo("home");
        }
        try {
            const endpoint = query
                ? `/restaurants/?search=${encodeURIComponent(query)}`
                : `/restaurants/`;
            const restaurants = await apiCall(endpoint);
            renderRestaurantList(restaurants);
        } catch (error) {
            showToast("Search failed: " + error.message, "error");
        }
    }, 400);
}

// ==================== RESTAURANT DETAIL ====================
async function renderRestaurantDetail(restaurantId) {
    const main = document.getElementById("main-content");
    try {
        const restaurant = await apiCall(`/restaurants/${restaurantId}`);
        const items = await apiCall(`/restaurants/${restaurantId}/items/`);
        // Group items by category
        const categories = {};
        items.forEach((item) => {
            const cat = item.category || "Other";
            if (!categories[cat]) categories[cat] = [];
            categories[cat].push(item);
        });
        let itemsHTML = "";
        for (const [category, catItems] of Object.entries(categories)) {
            let catItemsHTML = "";
            catItems.forEach((item) => {
                const cartQty = getCartItemQty(item.id);
                const actionHTML = cartQty > 0
                    ? `<div class="qty-control">
                         <button class="qty-btn" onclick="updateCartFromMenu(${item.id}, ${cartQty - 1})">−</button>
                         <span class="qty-display">${cartQty}</span>
                         <button class="qty-btn" onclick="updateCartFromMenu(${item.id}, ${cartQty + 1})">+</button>
                       </div>`
                    : `<button class="add-btn" onclick="addToCart(${item.id})" ${!item.is_available ? "disabled" : ""}>
                         ${item.is_available ? "ADD" : "Unavailable"}
                       </button>`;
                const img = item.image_url
                    ? `<img class="menu-item-img" src="${item.image_url}" alt="${item.name}" onerror="this.style.display='none'"/>`
                    : "";
                catItemsHTML += `
                    <div class="menu-item-card">
                        <div class="menu-item-info">
                            <div class="menu-item-name"><span class="menu-item-veg"></span>${item.name}</div>
                            <div class="menu-item-price">₹${item.price}</div>
                            <div class="menu-item-desc">${item.description || ""}</div>
                        </div>
                        <div class="menu-item-actions">
                            ${img}
                            ${actionHTML}
                        </div>
                    </div>
                `;
            });
            itemsHTML += `
                <div class="category-section">
                    <h3 class="category-title">${category} (${catItems.length})</h3>
                    ${catItemsHTML}
                </div>
            `;
        }
        const img = restaurant.image_url
            ? `<img class="card-image" src="${restaurant.image_url}" style="height:200px;border-radius:12px;width:100%;object-fit:cover;" alt="${restaurant.name}" onerror="this.style.display='none'"/>`
            : "";
        main.innerHTML = `
            <button class="back-btn" onclick="navigateTo('home')">← Back to Restaurants</button>
            <div class="restaurant-header">
                ${img}
                <h2>${restaurant.name}</h2>
                <p class="cuisine">${restaurant.cuisine}</p>
                <div class="card-meta">
                    <span class="rating">★ ${restaurant.rating || "N/A"}</span>
                    <span class="delivery-info">⏱ ${restaurant.delivery_time_minutes || 30} min</span>
                    <span class="delivery-info">₹${restaurant.delivery_fee || 0} delivery fee</span>
                </div>
                <p class="cuisine">${restaurant.description || ""}</p>
            </div>
            ${itemsHTML || "<p>No menu items available.</p>"}
        `;
    } catch (error) {
        main.innerHTML = `
            <button class="back-btn" onclick="navigateTo('home')">← Back to Restaurants</button>
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <h3>Could not load restaurant</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}

// ==================== CART ====================
function getCartItemQty(menuItemId) {
    if (!cartData || !cartData.items) return 0;
    const item = cartData.items.find((i) => i.menu_item_id === menuItemId);
    return item ? item.quantity : 0;
}

async function addToCart(menuItemId) {
    if (!authToken) {
        showToast("Please login to add items to cart", "error");
        openAuthModal();
        return;
    }
    try {
        cartData = await apiCall("/cart/items", "POST", {
            menu_item_id: menuItemId,
            quantity: 1,
        });
        updateCartCount();
        showToast("Added to cart!", "success");
        // Re-render the current view to update quantity controls
        if (currentView === "restaurant") {
            renderRestaurantDetail(currentRestaurantId);
        }
    } catch (error) {
        showToast("Failed to add to cart: " + error.message, "error");
    }
}

async function updateCartFromMenu(menuItemId, newQty) {
    if (newQty <= 0) {
        await removeFromCart(menuItemId);
        return;
    }
    try {
        cartData = await apiCall(`/cart/items/${menuItemId}`, "PUT", {
            quantity: newQty,
        });
        updateCartCount();
        if (currentView === "restaurant") {
            renderRestaurantDetail(currentRestaurantId);
        }
    } catch (error) {
        showToast("Failed to update cart: " + error.message, "error");
    }
}

async function removeFromCart(menuItemId) {
    try {
        cartData = await apiCall(`/cart/items/${menuItemId}`, "DELETE");
        updateCartCount();
        if (currentView === "cart") {
            renderCart();
        } else if (currentView === "restaurant") {
            renderRestaurantDetail(currentRestaurantId);
        }
        showToast("Item removed from cart", "success");
    } catch (error) {
        showToast("Failed to remove item: " + error.message, "error");
    }
}

async function clearCart() {
    if (!confirm("Clear all items from cart?")) return;
    try {
        await apiCall("/cart/", "DELETE");
        cartData = null;
        updateCartCount();
        renderCart();
        showToast("Cart cleared", "success");
    } catch (error) {
        showToast("Failed to clear cart: " + error.message, "error");
    }
}

function updateCartCount() {
    const countEl = document.getElementById("cart-count");
    const count = cartData && cartData.items ? cartData.items.length : 0;
    countEl.textContent = count;
}

async function fetchCart() {
    if (!authToken) {
        cartData = null;
        updateCartCount();
        return;
    }
    try {
        cartData = await apiCall("/cart/");
        updateCartCount();
    } catch (error) {
        cartData = null;
    }
}

async function renderCart() {
    const main = document.getElementById("main-content");
    if (!authToken) {
        main.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🛒</div>
                <h3>Please login to view your cart</h3>
                <button class="btn-primary" style="max-width:200px;margin:1rem auto 0;" onclick="openAuthModal()">Login Now</button>
            </div>
        `;
        return;
    }
    main.innerHTML = `<div class="loading"><div class="spinner"></div>Loading cart...</div>`;
    try {
        if (!cartData) {
            await fetchCart();
        }
        const cart = cartData;
        if (!cart || !cart.items || cart.items.length === 0) {
            main.innerHTML = `
                <div class="cart-view">
                    <h2>Your Cart</h2>
                    <div class="empty-state">
                        <div class="empty-state-icon">🛒</div>
                        <h3>Your cart is empty</h3>
                        <p>Add some delicious food to get started!</p>
                        <button class="btn-primary" style="max-width:200px;margin:1rem auto 0;" onclick="navigateTo('home')">Browse Restaurants</button>
                    </div>
                </div>
            `;
            return;
        }
        let itemsHTML = "";
        cart.items.forEach((item) => {
            itemsHTML += `
                <div class="cart-item">
                    <div class="cart-item-info">
                        <div class="cart-item-name"><span class="menu-item-veg"></span>${item.menu_item.name}</div>
                        <div class="cart-item-price">₹${item.menu_item.price} each</div>
                    </div>
                    <div class="cart-item-controls">
                        <div class="qty-control">
                            <button class="qty-btn" onclick="updateCartFromMenu(${item.menu_item_id}, ${item.quantity - 1})">−</button>
                            <span class="qty-display">${item.quantity}</span>
                            <button class="qty-btn" onclick="updateCartFromMenu(${item.menu_item_id}, ${item.quantity + 1})">+</button>
                        </div>
                        <div class="cart-item-price" style="font-weight:700;color:#282c3f;">₹${(item.menu_item.price * item.quantity).toFixed(2)}</div>
                        <button class="btn-danger" onclick="removeFromCart(${item.menu_item_id})">Remove</button>
                    </div>
                </div>
            `;
        });
        main.innerHTML = `
            <div class="cart-view">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem;">
                    <h2 style="margin-bottom:0;">Your Cart</h2>
                    <button class="btn-danger" onclick="clearCart()">Clear Cart</button>
                </div>
                <p class="cuisine" style="margin-bottom:1rem;">From: <strong>${cart.restaurant_name || "Restaurant"}</strong></p>
                ${itemsHTML}
                <div class="cart-summary">
                    <h3 style="margin-bottom:1rem;">Bill Details</h3>
                    <div class="summary-row">
                        <span>Item Total</span>
                        <span>₹${cart.total_amount.toFixed(2)}</span>
                    </div>
                    <div class="summary-row">
                        <span>Delivery Fee</span>
                        <span>₹${cart.delivery_fee.toFixed(2)}</span>
                    </div>
                    <div class="summary-row total">
                        <span>To Pay</span>
                        <span>₹${cart.grand_total.toFixed(2)}</span>
                    </div>
                    <button class="btn-primary" style="margin-top:1.5rem;" onclick="openCheckoutModal()">Proceed to Checkout</button>
                </div>
            </div>
        `;
    } catch (error) {
        main.innerHTML = `<div class="empty-state"><p>Error loading cart: ${error.message}</p></div>`;
    }
}

// ==================== CHECKOUT ====================
function openCheckoutModal() {
    if (!cartData || !cartData.items || cartData.items.length === 0) {
        showToast("Your cart is empty", "error");
        return;
    }
    // Pre-fill address from user profile
    if (currentUser && currentUser.address) {
        document.getElementById("checkout-address").value = currentUser.address;
    }
    const summary = document.getElementById("checkout-summary");
    summary.innerHTML = `
        <div class="summary-row"><span>Items (${cartData.items.length})</span><span>₹${cartData.total_amount.toFixed(2)}</span></div>
        <div class="summary-row"><span>Delivery Fee</span><span>₹${cartData.delivery_fee.toFixed(2)}</span></div>
        <div class="summary-row total"><span>Total</span><span>₹${cartData.grand_total.toFixed(2)}</span></div>
    `;
    document.getElementById("checkout-modal").classList.add("show");
}

function closeCheckoutModal() {
    document.getElementById("checkout-modal").classList.remove("show");
}

async function handleCheckout(event) {
    event.preventDefault();
    const address = document.getElementById("checkout-address").value;
    const payment = document.getElementById("checkout-payment").value;
    try {
        const order = await apiCall("/orders/", "POST", {
            delivery_address: address,
            payment_method: payment,
        });
        closeCheckoutModal();
        cartData = null;
        updateCartCount();
        showToast(`Order placed successfully! Order #${order.id}`, "success");
        navigateTo("orders");
    } catch (error) {
        showToast("Checkout failed: " + error.message, "error");
    }
}

// ==================== ORDERS ====================
async function renderOrders() {
    const main = document.getElementById("main-content");
    if (!authToken) {
        main.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📦</div>
                <h3>Please login to view your orders</h3>
                <button class="btn-primary" style="max-width:200px;margin:1rem auto 0;" onclick="openAuthModal()">Login Now</button>
            </div>
        `;
        return;
    }
    main.innerHTML = `<div class="loading"><div class="spinner"></div>Loading orders...</div>`;
    try {
        const orders = await apiCall("/orders/");
        if (!orders || orders.length === 0) {
            main.innerHTML = `
                <h2>Your Orders</h2>
                <div class="empty-state">
                    <div class="empty-state-icon">📦</div>
                    <h3>No orders yet</h3>
                    <p>Place your first order to see it here!</p>
                    <button class="btn-primary" style="max-width:200px;margin:1rem auto 0;" onclick="navigateTo('home')">Browse Restaurants</button>
                </div>
            `;
            return;
        }
        let ordersHTML = "";
        orders.forEach((order) => {
            let itemsListHTML = "";
            order.items.forEach((item) => {
                itemsListHTML += `
                    <li>
                        <span>${item.quantity}× ${item.menu_item_name || "Item"}</span>
                        <span>₹${(item.price * item.quantity).toFixed(2)}</span>
                    </li>
                `;
            });
            const date = new Date(order.created_at).toLocaleString();
            ordersHTML += `
                <div class="order-card">
                    <div class="order-header">
                        <div>
                            <div class="order-restaurant">${order.restaurant_name || "Restaurant"}</div>
                            <div class="order-id">Order #${order.id}</div>
                        </div>
                        <span class="order-status status-${order.status}">${order.status.replace(/_/g, " ")}</span>
                    </div>
                    <ul class="order-items-list">${itemsListHTML}</ul>
                    <div class="order-footer">
                        <div>
                            <span class="order-total">Total: ₹${order.total_amount.toFixed(2)}</span>
                            <span class="order-meta" style="margin-left:1rem;">${order.payment_method} • ${order.payment_status}</span>
                        </div>
                        <span class="order-meta">${date}</span>
                    </div>
                    ${order.delivery_address ? `<p class="order-meta" style="margin-top:0.5rem;">📍 ${order.delivery_address}</p>` : ""}
                </div>
            `;
        });
        main.innerHTML = `<h2>Your Orders</h2>${ordersHTML}`;
    } catch (error) {
        main.innerHTML = `<div class="empty-state"><p>Error loading orders: ${error.message}</p></div>`;
    }
}

// ==================== PROFILE ====================
async function renderProfile() {
    const main = document.getElementById("main-content");
    if (!authToken || !currentUser) {
        main.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">👤</div>
                <h3>Please login to view your profile</h3>
                <button class="btn-primary" style="max-width:200px;margin:1rem auto 0;" onclick="openAuthModal()">Login Now</button>
            </div>
        `;
        return;
    }
    const initials = currentUser.full_name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2);
    main.innerHTML = `
        <div class="profile-view">
            <h2>My Profile</h2>
            <div class="profile-card">
                <div class="profile-avatar">${initials}</div>
                <form id="profile-form" class="auth-form" onsubmit="handleProfileUpdate(event)">
                    <div class="form-group">
                        <label>Full Name</label>
                        <input type="text" id="profile-name" value="${currentUser.full_name || ""}" required />
                    </div>
                    <div class="form-group">
                        <label>Email (cannot change)</label>
                        <input type="email" value="${currentUser.email || ""}" disabled />
                    </div>
                    <div class="form-group">
                        <label>Phone</label>
                        <input type="tel" id="profile-phone" value="${currentUser.phone || ""}" />
                    </div>
                    <div class="form-group">
                        <label>Address</label>
                        <textarea id="profile-address" rows="3">${currentUser.address || ""}</textarea>
                    </div>
                    <button type="submit" class="btn-primary">Update Profile</button>
                </form>
            </div>
        </div>
    `;
}

async function handleProfileUpdate(event) {
    event.preventDefault();
    const body = {
        full_name: document.getElementById("profile-name").value,
        phone: document.getElementById("profile-phone").value || null,
        address: document.getElementById("profile-address").value || null,
    };
    try {
        const updated = await apiCall("/auth/me", "PUT", body);
        currentUser = updated;
        localStorage.setItem("user", JSON.stringify(currentUser));
        updateNavForUser();
        showToast("Profile updated successfully!", "success");
    } catch (error) {
        showToast("Update failed: " + error.message, "error");
    }
}

// ==================== INIT ====================
document.addEventListener("DOMContentLoaded", async () => {
    updateNavForUser();
    // If user has token, fetch cart and verify token
    if (authToken) {
        try {
            currentUser = await apiCall("/auth/me");
            localStorage.setItem("user", JSON.stringify(currentUser));
            updateNavForUser();
            await fetchCart();
        } catch (error) {
            // Token expired or invalid
            logout();
        }
    }
    navigateTo("home");
});