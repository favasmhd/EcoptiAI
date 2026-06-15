// logistics.js — UI ONLY

const API_BASE_URL = "http://localhost:8000";

// ---------- UI Helpers ----------

function showLoading() {
    document.getElementById("loadingState").classList.remove("hidden");
    document.getElementById("ordersContainer").classList.add("hidden");
}

function hideLoading() {
    document.getElementById("loadingState").classList.add("hidden");
    document.getElementById("ordersContainer").classList.remove("hidden");
}

function showError(message) {
    document.getElementById("errorMessage").innerText = message;
    document.getElementById("errorAlert").classList.remove("hidden");
}

function hideError() {
    document.getElementById("errorAlert").classList.add("hidden");
}

// ---------- Backend Calls ----------

async function fetchOrders() {
    const res = await fetch(`${API_BASE_URL}/orders`);
    if (!res.ok) throw new Error("Failed to fetch orders");
    return await res.json();
}

async function updateOrderStatus(orderId, status) {
    const res = await fetch(`${API_BASE_URL}/orders/${orderId}/status`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status })
    });
    if (!res.ok) throw new Error("Failed to update order status");
}

// ---------- Rendering ----------

function renderOrders(orders) {
    const list = document.getElementById("ordersList");
    list.innerHTML = "";

    let counts = {
        "On the Way": 0,
        "In Transit": 0,
        "Delayed": 0,
        "Delivered": 0
    };

    orders.forEach(order => {
        counts[order.status]++;

        const row = document.createElement("div");
        row.className = "bg-white border border-gray-200 rounded-lg p-4 shadow-sm grid grid-cols-12 gap-4 items-center";

        row.innerHTML = `
            <div class="col-span-2 font-mono text-sm">${order.order_id}</div>
            <div class="col-span-3">${order.product_name}</div>
            <div class="col-span-2">${order.customer_name}</div>
            <div class="col-span-2 text-sm text-gray-500">${order.eta || "-"}</div>
            <div class="col-span-3 flex gap-2">
                <button onclick="changeStatus('${order.order_id}', 'Delayed')" class="px-2 py-1 bg-yellow-100 text-yellow-800 rounded">Delay</button>
                <button onclick="changeStatus('${order.order_id}', 'Delivered')" class="px-2 py-1 bg-green-100 text-green-800 rounded">Deliver</button>
            </div>
        `;

        list.appendChild(row);
    });

    document.getElementById("onTheWayCount").innerText = counts["On the Way"] || 0;
    document.getElementById("inTransitCount").innerText = counts["In Transit"] || 0;
    document.getElementById("delayedCount").innerText = counts["Delayed"] || 0;
    document.getElementById("deliveredCount").innerText = counts["Delivered"] || 0;
}

// ---------- Actions ----------

async function changeStatus(orderId, newStatus) {
    try {
        await updateOrderStatus(orderId, newStatus);
        await loadOrders();
    } catch (err) {
        showError(err.message);
    }
}

// ---------- Init ----------

async function loadOrders() {
    showLoading();
    hideError();

    try {
        const orders = await fetchOrders();
        renderOrders(orders);
    } catch (err) {
        showError(err.message);
    } finally {
        hideLoading();
    }
}

loadOrders();
