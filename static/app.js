const API_BASE_URL = 'http://localhost:5000';
let feeChart, mempoolChart, txVolumeChart;
let lowFeeTimeout;
let ws;

// Fallback data for offline mode
const FALLBACK_DATA = {
    fees: { fastestFee: 50, halfHourFee: 30, hourFee: 20, minimumFee: 10 },
    mempool: { count: 5000, vsize: 1000000 },
    savings: 0.0005,
    difficulty: 88000000000000,
    adjustmentTime: new Date().toISOString()
};

// Debug: Log script load
console.log('app.js loaded at', new Date().toISOString());

// Update Auth UI
function updateAuthUI() {
    console.log('updateAuthUI called');
    const loginBtn = document.getElementById('login-btn');
    const registerBtn = document.getElementById('register-btn');
    const usernameDisplay = document.getElementById('username-display');
    const logoutBtn = document.getElementById('logout-btn');
    const authSection = document.getElementById('auth-section');
    const username = localStorage.getItem('username');

    console.log('Username from localStorage:', username);

    if (username && usernameDisplay && authSection) {
        console.log('Updating UI for logged-in user:', username);
        if (loginBtn) loginBtn.remove();
        if (registerBtn) registerBtn.remove();
        usernameDisplay.classList.remove('hidden');
        if (logoutBtn) logoutBtn.classList.remove('hidden');
        usernameDisplay.classList.add('bg-gradient-to-r', 'from-green-400', 'to-blue-500', 'text-gray-900', 'px-4', 'py-2', 'rounded-lg');
        usernameDisplay.textContent = username;
    } else {
        console.log('Updating UI for logged-out state');
        if (!loginBtn && authSection) {
            const newLoginBtn = document.createElement('a');
            newLoginBtn.id = 'login-btn';
            newLoginBtn.href = 'user.html';
            newLoginBtn.className = 'bg-gradient-to-r from-green-400 to-blue-500 text-gray-900 px-4 py-2 rounded-lg hover:from-green-500 hover:to-blue-600 transition';
            newLoginBtn.textContent = 'Login';
            authSection.insertBefore(newLoginBtn, usernameDisplay);
        }
        if (!registerBtn && authSection) {
            const newRegisterBtn = document.createElement('a');
            newRegisterBtn.id = 'register-btn';
            newRegisterBtn.href = 'user.html';
            newRegisterBtn.className = 'bg-gray-700 text-gray-100 px-4 py-2 rounded-lg hover:bg-gray-600 transition';
            newRegisterBtn.textContent = 'Register';
            authSection.insertBefore(newRegisterBtn, usernameDisplay);
        }
        if (usernameDisplay) {
            usernameDisplay.classList.add('hidden');
            usernameDisplay.classList.remove('bg-gradient-to-r', 'from-green-400', 'to-blue-500', 'text-gray-900', 'px-4', 'py-2', 'rounded-lg');
            usernameDisplay.textContent = '';
        }
        if (logoutBtn) logoutBtn.classList.add('hidden');
    }
}

// Logout function
async function logout() {
    try {
        console.log('Initiating logout');
        const response = await fetch(`${API_BASE_URL}/logout`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
        });
        console.log('Logout response status:', response.status);
        localStorage.removeItem('username');
        updateAuthUI();
        window.location.href = 'user.html';
    } catch (error) {
        console.error('Logout error:', error.message, error.stack);
        localStorage.removeItem('username');
        updateAuthUI();
        window.location.href = 'user.html';
    }
}

function connectWebSocket() {
    let ports = [8765, 8766];
    let currentPortIndex = 0;

    function tryConnect() {
        const port = ports[currentPortIndex];
        ws = new WebSocket(`ws://localhost:${port}`);
        
        ws.onopen = () => {
            console.log(`WebSocket connected on port ${port}`);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (!data.fees || !data.mempool) {
                    console.error('Invalid WebSocket data:', data);
                    return;
                }
                updateDashboard(data);
            } catch (e) {
                console.error('Error parsing WebSocket data:', e);
            }
        };

        ws.onclose = () => {
            console.log(`WebSocket disconnected from port ${port}, trying next port...`);
            currentPortIndex = (currentPortIndex + 1) % ports.length;
            setTimeout(tryConnect, 5000);
        };

        ws.onerror = (error) => {
            console.error(`WebSocket error on port ${port}:`, error);
        };
    }

    tryConnect();
}

function updateDashboard(data) {
    try {
        console.log('Updating dashboard with data:', data);
        document.getElementById('currentFeeRange').textContent = `${data.fees.hourFee} - ${data.fees.fastestFee} sat/vB`;
        document.getElementById('recommendedFee').textContent = `${data.fees.hourFee} sat/vB`;
        document.getElementById('feeSavings').textContent = `${data.savings.toFixed(6)} BTC`;
        document.getElementById('mempoolSize').textContent = `${data.mempool.count.toLocaleString()} tx`;
        document.getElementById('networkDifficulty').textContent = `${(data.difficulty / 1e12).toLocaleString()} T`;
        document.getElementById('difficultyAdjustment').textContent = new Date(data.adjustmentTime).toLocaleDateString();
        document.getElementById('hashRate').textContent = `${(Math.random() * 350).toFixed(2)} EH/s`;
        document.getElementById('txRate').textContent = `${Math.floor(Math.random() * 10000)} tx/hr`;

        const bar = document.getElementById('feeRangeBar');
        const percent = (data.fees.hourFee / data.fees.fastestFee) * 100;
        bar.style.width = `${percent}%`;
    } catch (e) {
        console.error('Error updating dashboard:', e);
    }
}

async function fetchNetworkData() {
    try {
        console.log('Fetching network data');
        const res = await fetch(`${API_BASE_URL}/network-data`, { credentials: 'include' });
        console.log('Network data response status:', res.status);
        if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
        const data = await res.json();
        if (!data.fees || !data.mempool) {
            console.error('Invalid network data:', data);
            updateDashboard(FALLBACK_DATA);
            return;
        }
        updateDashboard(data);
    } catch (error) {
        console.error('Error fetching network data:', error);
        updateDashboard(FALLBACK_DATA);
    }
}

async function loadFeeHistory() {
    try {
        console.log('Fetching fee history');
        const res = await fetch(`${API_BASE_URL}/fee-history`, { credentials: 'include' });
        console.log('Fee history response status:', res.status);
        if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
        const history = await res.json();
        if (!Array.isArray(history) || history.length === 0) {
            console.error('Empty or invalid fee history:', history);
            throw new Error('Invalid fee history');
        }
        const dataPoints = history.map(entry => ({
            x: entry.timestamp,
            y: entry.hourFee
        })).filter(point => point.x && !isNaN(new Date(point.x).getTime()));
        console.log('Fee history data points:', dataPoints);
        feeChart.data.datasets[0].data = dataPoints;
        feeChart.update();
    } catch (error) {
        console.error('Error loading fee history:', error);
        const now = new Date();
        feeChart.data.datasets[0].data = Array.from({length: 60}, (_, i) => ({
            x: new Date(now - i * 60 * 1000).toISOString(),
            y: 10 + Math.random() * 40
        }));
        feeChart.update();
    }
}

async function loadMempoolHistory() {
    try {
        console.log('Fetching mempool history');
        const res = await fetch(`${API_BASE_URL}/mempool-history`, { credentials: 'include' });
        console.log('Mempool history response status:', res.status);
        if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
        const history = await res.json();
        if (!Array.isArray(history) || history.length === 0) {
            console.error('Empty or invalid mempool history:', history);
            throw new Error('Invalid mempool history');
        }
        const dataPoints = history.map(entry => ({
            x: entry.timestamp,
            y: entry.count
        })).filter(point => point.x && !isNaN(new Date(point.x).getTime()));
        console.log('Mempool history data points:', dataPoints);
        mempoolChart.data.datasets[0].data = dataPoints;
        mempoolChart.update();
    } catch (error) {
        console.error('Error loading mempool history:', error);
        const now = new Date();
        mempoolChart.data.datasets[0].data = Array.from({length: 60}, (_, i) => ({
            x: new Date(now - i * 60 * 1000).toISOString(),
            y: 3000 + Math.random() * 7000
        }));
        mempoolChart.update();
    }
}

async function loadTxVolumeHistory() {
    try {
        console.log('Fetching transaction volume history');
        const res = await fetch(`${API_BASE_URL}/tx-volume-history`, { credentials: 'include' });
        console.log('Tx volume history response status:', res.status);
        if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
        const history = await res.json();
        if (!Array.isArray(history) || history.length === 0) {
            console.error('Empty or invalid transaction volume history:', history);
            throw new Error('Invalid transaction volume history');
        }
        const dataPoints = history.map(entry => ({
            x: entry.timestamp,
            y: entry.volume
        })).filter(point => point.x && !isNaN(new Date(point.x).getTime()));
        console.log('Transaction volume history data points:', dataPoints);
        txVolumeChart.data.datasets[0].data = dataPoints;
        txVolumeChart.update();
    } catch (error) {
        console.error('Error loading transaction volume history:', error);
        const now = new Date();
        txVolumeChart.data.datasets[0].data = Array.from({length: 60}, (_, i) => ({
            x: new Date(now - i * 60 * 1000).toISOString(),
            y: 100 + Math.random() * 900
        }));
        txVolumeChart.update();
    }
}

function createGradient(ctx, chartArea) {
    const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
    gradient.addColorStop(0, 'rgba(16, 185, 129, 0.1)');
    gradient.addColorStop(1, 'rgba(16, 185, 129, 0.5)');
    return gradient;
}

function initCharts() {
    try {
        console.log('Initializing charts');
        const feeCtx = document.getElementById('feeHeatmap').getContext('2d');
        feeChart = new Chart(feeCtx, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Fee Rate (hourFee)',
                    data: [],
                    borderColor: '#10B981',
                    tension: 0.4,
                    fill: true,
                    backgroundColor: (context) => {
                        const chart = context.chart;
                        const {ctx, chartArea} = chart;
                        if (!chartArea) return;
                        return createGradient(ctx, chartArea);
                    },
                    pointRadius: 4,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            title: (ctx) => new Date(ctx[0].parsed.x).toLocaleString(),
                            label: (ctx) => `${ctx.parsed.y} sat/vB`
                        }
                    },
                    annotation: {
                        annotations: {
                            line1: {
                                type: 'line',
                                yMin: 15,
                                yMax: 15,
                                borderColor: '#EF4444',
                                borderWidth: 2,
                                label: {
                                    content: 'Low Fee Threshold (15 sat/vB)',
                                    enabled: true,
                                    position: 'start'
                                }
                            }
                        }
                    }
                },
                scales: {
                    x: { 
                        type: 'time', 
                        time: { unit: 'minute' }, 
                        grid: { color: '#374151' },
                        title: { display: true, text: 'Time', color: '#D1D5DB' }
                    },
                    y: { 
                        beginAtZero: true, 
                        grid: { color: '#374151' },
                        title: { display: true, text: 'Fee Rate (sat/vB)', color: '#D1D5DB' }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeOutQuart'
                }
            }
        });

        const mempoolCtx = document.getElementById('mempoolChart').getContext('2d');
        mempoolChart = new Chart(mempoolCtx, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Mempool Count',
                    data: [],
                    borderColor: '#F59E0B',
                    tension: 0.4,
                    fill: true,
                    backgroundColor: (context) => {
                        const chart = context.chart;
                        const {ctx, chartArea} = chart;
                        if (!chartArea) return;
                        const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
                        gradient.addColorStop(0, 'rgba(245, 158, 11, 0.1)');
                        gradient.addColorStop(1, 'rgba(245, 158, 11, 0.5)');
                        return gradient;
                    },
                    pointRadius: 4,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            title: (ctx) => new Date(ctx[0].parsed.x).toLocaleString(),
                            label: (ctx) => `${ctx.parsed.y.toLocaleString()} tx`
                        }
                    }
                },
                scales: {
                    x: { 
                        type: 'time', 
                        time: { unit: 'minute' }, 
                        grid: { color: '#374151' },
                        title: { display: true, text: 'Time', color: '#D1D5DB' }
                    },
                    y: { 
                        beginAtZero: true, 
                        grid: { color: '#374151' },
                        title: { display: true, text: 'Transactions', color: '#D1D5DB' }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeOutQuart'
                }
            }
        });

        const txVolumeCtx = document.getElementById('txVolumeChart').getContext('2d');
        txVolumeChart = new Chart(txVolumeCtx, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Transaction Volume',
                    data: [],
                    borderColor: '#3B82F6',
                    tension: 0.4,
                    fill: true,
                    backgroundColor: (context) => {
                        const chart = context.chart;
                        const {ctx, chartArea} = chart;
                        if (!chartArea) return;
                        const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
                        gradient.addColorStop(0, 'rgba(59, 130, 246, 0.1)');
                        gradient.addColorStop(1, 'rgba(59, 130, 246, 0.5)');
                        return gradient;
                    },
                    pointRadius: 4,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            title: (ctx) => new Date(ctx[0].parsed.x).toLocaleString(),
                            label: (ctx) => `${ctx.parsed.y.toLocaleString()} BTC`
                        }
                    }
                },
                scales: {
                    x: { 
                        type: 'time', 
                        time: { unit: 'minute' }, 
                        grid: { color: '#374151' },
                        title: { display: true, text: 'Time', color: '#D1D5DB' }
                    },
                    y: { 
                        beginAtZero: true, 
                        grid: { color: '#374151' },
                        title: { display: true, text: 'Volume (BTC)', color: '#D1D5DB' }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeOutQuart'
                }
            }
        });
    } catch (e) {
        console.error('Error initializing charts:', e);
    }
}

function simulateTransaction() {
    try {
        console.log('Simulating transaction');
        const confirmation = Math.floor(Math.random() * 60) + 1;
        const efficiency = `${Math.floor(Math.random() * 100)}%`;

        document.getElementById('txProgress').style.width = `${Math.random() * 100}%`;
        document.getElementById('estConfirmation').textContent = `${confirmation} min`;
        document.getElementById('costEfficiency').textContent = efficiency;
    } catch (e) {
        console.error('Error simulating transaction:', e);
    }
}

async function determineNextLowFeeWindow() {
    try {
        console.log('Fetching low fee window');
        const res = await fetch(`${API_BASE_URL}/fee-history`, { credentials: 'include' });
        console.log('Fee history response status:', res.status);
        if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
        const history = await res.json();
        if (!Array.isArray(history) || history.length === 0) {
            console.error('Empty or invalid fee history:', history);
            throw new Error('Invalid fee history');
        }

        const now = new Date();
        const lowFeeEntries = history
            .filter(h => h.hourFee < 15)
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

        const optimalWindow = document.getElementById('optimalWindow');
        const nextLowFee = document.getElementById('nextLowFee');

        if (!optimalWindow || !nextLowFee) {
            console.error('DOM elements #optimalWindow or #nextLowFee not found');
            return;
        }

        if (lowFeeEntries.length > 0) {
            const lowFeeEntry = lowFeeEntries[0];
            const ts = new Date(lowFeeEntry.timestamp);
            const mins = Math.round((now - ts) / 60000);
            console.log(`Low fee found at ${ts.toLocaleTimeString()}, ${mins} min ago, hourFee: ${lowFeeEntry.hourFee}`);

            optimalWindow.textContent = ts.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
            nextLowFee.textContent = mins >= 0 ? `${mins} min ago` : `Now`;
        } else {
            console.log('No low fee period found in history');
            optimalWindow.textContent = `Not in 60m`;
            nextLowFee.textContent = `--`;
        }
    } catch (error) {
        console.error('Error determining low fee window:', error);
        const optimalWindow = document.getElementById('optimalWindow');
        const nextLowFee = document.getElementById('nextLowFee');
        if (optimalWindow && nextLowFee) {
            optimalWindow.textContent = `Not in 60m`;
            nextLowFee.textContent = `--`;
        }
    }
}

async function refreshDashboard() {
    try {
        console.log('Refreshing dashboard');
        await Promise.all([
            fetchNetworkData(),
            loadFeeHistory(),
            loadMempoolHistory(),
            loadTxVolumeHistory(),
            determineNextLowFeeWindow()
        ]);
    } catch (e) {
        console.error('Error refreshing dashboard:', e);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    try {
        console.log('DOM loaded, initializing');
        updateAuthUI();
        initCharts();
        connectWebSocket();
        refreshDashboard();
        setInterval(refreshDashboard, 60000);

        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', logout);
        }
    } catch (e) {
        console.error('Error during initialization:', e);
    }
});