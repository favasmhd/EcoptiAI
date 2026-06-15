// Sample data for when backend is unreachable
const SAMPLE_EVENTS = [
    {
        id: "evt-001",
        event_type: "Product Added",
        timestamp: "2025-01-18T14:30:00Z",
        input_data: "New product: Wireless Bluetooth Headphones",
        agent_action: "Generated SEO-optimized product description and tags",
        outcome: "Success",
        details: "Product successfully added"
    },
    {
        id: "evt-002",
        event_type: "Customer Query",
        timestamp: "2025-01-18T15:45:00Z",
        input_data: "Customer asked: 'What's the battery life of the headphones?'",
        agent_action: "Retrieved product specs and generated personalized response",
        outcome: "Success",
        details: "Customer received accurate information"
    },
    {
        id: "evt-003",
        event_type: "Order Delayed",
        timestamp: "2025-01-18T16:20:00Z",
        input_data: "Order #12345 delayed due to weather conditions",
        agent_action: "Generated apology message",
        outcome: "Success",
        details: "Customer notified"
    },
    {
        id: "evt-004",
        event_type: "Inventory Alert",
        timestamp: "2025-01-18T17:10:00Z",
        input_data: "Gaming Mouse stock below threshold (5 units remaining)",
        agent_action: "Triggered reorder process and updated product availability",
        outcome: "Success",
        details: "Stock status updated"
    }
];

// Global state
let events = [];
let recentActions = [];
let isRefreshing = false;
let currentFilter = '';

// API Configuration
const API_BASE_URL = 'http://localhost:8000';
const REQUEST_TIMEOUT = 5000;

// Utility Functions
function formatTimestamp(timestamp) {
    try {
        const date = new Date(timestamp);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    } catch {
        return 'Invalid Date';
    }
}

function getEventTypeColor(eventType) {
    switch (eventType) {
        case 'Product Added': return 'bg-blue-500';
        case 'Customer Query': return 'bg-yellow-500';
        case 'Order Delayed': return 'bg-red-500';
        case 'Inventory Alert': return 'bg-orange-500';
        case 'Price Update': return 'bg-green-500';
        case 'Review Analysis': return 'bg-purple-500';
        default: return 'bg-gray-500';
    }
}

function getEventTypeTextColor(eventType) {
    switch (eventType) {
        case 'Product Added': return 'text-blue-700';
        case 'Customer Query': return 'text-yellow-700';
        case 'Order Delayed': return 'text-red-700';
        case 'Inventory Alert': return 'text-orange-700';
        case 'Price Update': return 'text-green-700';
        case 'Review Analysis': return 'text-purple-700';
        default: return 'text-gray-700';
    }
}

function getOutcomeColor(outcome) {
    switch (outcome.toLowerCase()) {
        case 'success': return 'bg-green-100 text-green-800';
        case 'failed': return 'bg-red-100 text-red-800';
        case 'pending': return 'bg-yellow-100 text-yellow-800';
        default: return 'bg-gray-100 text-gray-800';
    }
}

// API Functions
async function fetchAgentEvents() {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);
        
        const response = await fetch(`${API_BASE_URL}/agent_events`, {
            signal: controller.signal,
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.warn('Backend unreachable, using sample data:', error.message);
        return SAMPLE_EVENTS;
    }
}

// UI Functions
function showError(message) {
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorAlert.classList.remove('hidden');
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        errorAlert.classList.add('hidden');
    }, 5000);
}

function hideError() {
    document.getElementById('errorAlert').classList.add('hidden');
}

function showLoading() {
    document.getElementById('loadingState').classList.remove('hidden');
    document.getElementById('eventsContainer').classList.add('hidden');
}

function hideLoading() {
    document.getElementById('loadingState').classList.add('hidden');
    document.getElementById('eventsContainer').classList.remove('hidden');
}

function updateRefreshButton(isRefreshing) {
    const refreshBtn = document.getElementById('refreshBtn');
    const refreshIcon = document.getElementById('refreshIcon');
    const refreshText = document.getElementById('refreshText');
    
    refreshBtn.disabled = isRefreshing;
    
    if (isRefreshing) {
        refreshIcon.innerHTML = '<div class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>';
        refreshText.textContent = 'Refreshing...';
    } else {
        refreshIcon.textContent = '↻';
        refreshText.textContent = 'Refresh';
    }
}

function createEventRow(event) {
    const row = document.createElement('div');
    row.className = 'bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-all duration-200 shadow-sm event-row';
    row.id = `event-${event.id}`;
    
    // Desktop layout
    const desktopLayout = `
        <div class="hidden md:grid md:grid-cols-12 gap-4 items-center">
            <div class="col-span-2">
                <div class="px-3 py-1 rounded-full text-xs font-medium ${getEventTypeColor(event.event_type)} ${getEventTypeTextColor(event.event_type)}">
                    ${event.event_type}
                </div>
            </div>
            <div class="col-span-2">
                <div class="text-gray-600 text-sm font-mono">${formatTimestamp(event.timestamp)}</div>
            </div>
            <div class="col-span-3">
                <div class="text-gray-900 text-sm">${event.input_data}</div>
            </div>
            <div class="col-span-3">
                <div class="text-gray-700 text-sm">${event.agent_action}</div>
            </div>
            <div class="col-span-2">
                <div class="px-2 py-1 rounded-full text-xs font-medium ${getOutcomeColor(event.outcome)}">
                    ${event.outcome}
                </div>
            </div>
        </div>
    `;
    
    // Mobile layout
    const mobileLayout = `
        <div class="md:hidden space-y-3">
            <div class="flex justify-between items-start">
                <div class="px-3 py-1 rounded-full text-xs font-medium ${getEventTypeColor(event.event_type)} ${getEventTypeTextColor(event.event_type)}">
                    ${event.event_type}
                </div>
                <div class="px-2 py-1 rounded-full text-xs font-medium ${getOutcomeColor(event.outcome)}">
                    ${event.outcome}
                </div>
            </div>
            <div class="text-gray-600 text-sm font-mono">${formatTimestamp(event.timestamp)}</div>
            <div class="text-gray-900 text-sm"><strong>Input:</strong> ${event.input_data}</div>
            <div class="text-gray-700 text-sm"><strong>Action:</strong> ${event.agent_action}</div>
            ${event.details ? `<div class="text-gray-500 text-xs"><strong>Details:</strong> ${event.details}</div>` : ''}
        </div>
    `;
    
    row.innerHTML = desktopLayout + mobileLayout;
    return row;
}

function renderEvents() {
    const eventsList = document.getElementById('eventsList');
    eventsList.innerHTML = '';
    
    // Filter events based on current filter
    const filteredEvents = currentFilter ? 
        events.filter(event => event.event_type === currentFilter) : 
        events;
    
    filteredEvents.forEach(event => {
        const row = createEventRow(event);
        eventsList.appendChild(row);
    });
    
    updateSummaryStats();
}

function updateSummaryStats() {
    const stats = {
        'Product Added': events.filter(e => e.event_type === 'Product Added').length,
        'Customer Query': events.filter(e => e.event_type === 'Customer Query').length,
        'Order Delayed': events.filter(e => e.event_type === 'Order Delayed').length,
        'Inventory Alert': events.filter(e => e.event_type === 'Inventory Alert').length,
        'Price Update': events.filter(e => e.event_type === 'Price Update').length,
        'Review Analysis': events.filter(e => e.event_type === 'Review Analysis').length
    };
    
    document.getElementById('productAddedCount').textContent = stats['Product Added'];
    document.getElementById('customerQueryCount').textContent = stats['Customer Query'];
    document.getElementById('orderDelayedCount').textContent = stats['Order Delayed'];
    document.getElementById('inventoryAlertCount').textContent = stats['Inventory Alert'];
    document.getElementById('priceUpdateCount').textContent = stats['Price Update'];
    document.getElementById('reviewAnalysisCount').textContent = stats['Review Analysis'];
}

function addRecentAction(event) {
    const action = {
        timestamp: new Date().toLocaleTimeString(),
        eventType: event.event_type,
        action: event.agent_action,
        outcome: event.outcome
    };
    
    recentActions.unshift(action);
    recentActions = recentActions.slice(0, 10); // Keep only last 10
    
    renderRecentActions();
}

function renderRecentActions() {
    const actionsPanel = document.getElementById('actionsPanel');
    
    if (recentActions.length === 0) {
        actionsPanel.innerHTML = '<div class="text-gray-500 text-sm text-center py-4">No recent actions</div>';
        return;
    }
    
    actionsPanel.innerHTML = recentActions.map((action, index) => `
        <div class="bg-gray-50 rounded p-3 border border-gray-200" style="animation: slideIn 0.3s ease-out ${index * 0.1}s both;">
            <div class="flex justify-between items-start mb-1">
                <div class="text-gray-700 text-sm font-medium">${action.eventType}</div>
                <div class="text-gray-500 text-xs">${action.timestamp}</div>
            </div>
            <div class="text-gray-900 text-sm mb-1">${action.action}</div>
            <div class="text-xs">
                <span class="px-2 py-1 rounded-full ${getOutcomeColor(action.outcome)}">${action.outcome}</span>
            </div>
        </div>
    `).join('');
}

// Event Handlers
async function loadEvents() {
    showLoading();
    hideError();
    
    try {
        events = await fetchAgentEvents();
        renderEvents();
        
        // Add new events to recent actions
        events.slice(0, 3).forEach(event => {
            addRecentAction(event);
        });
    } catch (error) {
        showError(`Failed to load events: ${error.message}`);
        events = SAMPLE_EVENTS;
        renderEvents();
        
        // Add sample events to recent actions
        events.slice(0, 3).forEach(event => {
            addRecentAction(event);
        });
    } finally {
        hideLoading();
    }
}

async function refreshEvents() {
    if (isRefreshing) return;
    
    isRefreshing = true;
    updateRefreshButton(true);
    
    try {
        const newEvents = await fetchAgentEvents();
        
        // Check for new events
        const newEventIds = newEvents.map(e => e.id);
        const currentEventIds = events.map(e => e.id);
        const actuallyNewEvents = newEvents.filter(e => !currentEventIds.includes(e.id));
        
        events = newEvents;
        renderEvents();
        
        // Add new events to recent actions
        actuallyNewEvents.forEach(event => {
            addRecentAction(event);
        });
        
        hideError();
    } catch (error) {
        showError(`Failed to refresh events: ${error.message}`);
    } finally {
        isRefreshing = false;
        updateRefreshButton(false);
    }
}

function handleFilterChange() {
    const filterSelect = document.getElementById('eventTypeFilter');
    currentFilter = filterSelect.value;
    renderEvents();
}

function toggleActionsPanel() {
    const panel = document.getElementById('actionsPanel');
    const button = document.getElementById('toggleActionsBtn');
    
    if (panel.style.display === 'none') {
        panel.style.display = 'block';
        button.textContent = '−';
    } else {
        panel.style.display = 'none';
        button.textContent = '+';
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Set up event listeners
    document.getElementById('refreshBtn').addEventListener('click', refreshEvents);
    document.getElementById('eventTypeFilter').addEventListener('change', handleFilterChange);
    document.getElementById('toggleActionsBtn').addEventListener('click', toggleActionsPanel);
    
    // Load initial data
    loadEvents();
    
    // Set up auto-refresh every 10 seconds
    setInterval(refreshEvents, 10000);
});
