// API Base URL
const API_BASE = '/api';

// Toast Notification System
function showToast(message, type = 'success') {
    // Remove existing toasts
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Update Connection Status
function updateConnectionStatus(connected) {
    const indicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    
    if (connected) {
        indicator.classList.remove('disconnected');
        statusText.textContent = 'Conectado';
    } else {
        indicator.classList.add('disconnected');
        statusText.textContent = 'Desconectado';
    }
}

// Update CLP Configuration
async function updateConfig() {
    const ip = document.getElementById('clpIp').value;
    const port = document.getElementById('clpPort').value;

    try {
        const response = await fetch(`${API_BASE}/config`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ip, port: parseInt(port) })
        });

        const data = await response.json();
        
        if (data.success) {
            showToast(`✅ Configuração atualizada: ${data.ip}:${data.port}`, 'success');
            updateConnectionStatus(true);
            loadVariables();
        } else {
            showToast('❌ Erro ao atualizar configuração', 'error');
        }
    } catch (error) {
        showToast(`❌ Erro: ${error.message}`, 'error');
        updateConnectionStatus(false);
    }
}

// Load Variables Configuration
async function loadVariables() {
    try {
        const response = await fetch(`${API_BASE}/variables`);
        const variables = await response.json();

        renderBoolVariables(variables.bool);
        renderIntVariables(variables.int);
        renderRealVariables(variables.real);

        updateConnectionStatus(true);
    } catch (error) {
        console.error('Erro ao carregar variáveis:', error);
        updateConnectionStatus(false);
        showToast('❌ Erro ao carregar variáveis', 'error');
    }
}

// Render Bool Variables
function renderBoolVariables(variables) {
    const container = document.getElementById('boolVariables');
    container.innerHTML = '';

    variables.forEach(variable => {
        const item = document.createElement('div');
        item.className = 'variable-item';
        item.innerHTML = `
            <div class="variable-header">
                <div class="variable-info">
                    <h3>${variable.name}</h3>
                    <p>${variable.description}</p>
                </div>
                <span class="variable-address">@${variable.address}</span>
            </div>
            <div class="variable-controls">
                <div 
                    class="toggle-switch" 
                    id="toggle-${variable.address}"
                    onclick="toggleBool(${variable.address})"
                ></div>
                <div class="current-value" id="bool-value-${variable.address}">--</div>
            </div>
        `;
        container.appendChild(item);

        // Read initial value
        readBoolVariable(variable.address);
    });
}

// Render Int Variables
function renderIntVariables(variables) {
    const container = document.getElementById('intVariables');
    container.innerHTML = '';

    variables.forEach(variable => {
        const item = document.createElement('div');
        item.className = 'variable-item';
        item.innerHTML = `
            <div class="variable-header">
                <div class="variable-info">
                    <h3>${variable.name}</h3>
                    <p>${variable.description}</p>
                </div>
                <span class="variable-address">@${variable.address}</span>
            </div>
            <div class="variable-controls">
                <input 
                    type="number" 
                    class="variable-value" 
                    id="int-input-${variable.address}"
                    placeholder="Digite o valor"
                >
                <button class="btn btn-primary" onclick="writeInt(${variable.address})">
                    ✍️ Escrever
                </button>
                <button class="btn btn-success" onclick="readInt(${variable.address})">
                    📖 Ler
                </button>
            </div>
            <div class="current-value" id="int-value-${variable.address}">--</div>
        `;
        container.appendChild(item);

        // Read initial value
        readInt(variable.address);
    });
}

// Render Real Variables
function renderRealVariables(variables) {
    const container = document.getElementById('realVariables');
    container.innerHTML = '';

    variables.forEach(variable => {
        const item = document.createElement('div');
        item.className = 'variable-item';
        item.innerHTML = `
            <div class="variable-header">
                <div class="variable-info">
                    <h3>${variable.name}</h3>
                    <p>${variable.description}</p>
                </div>
                <span class="variable-address">@${variable.address}</span>
            </div>
            <div class="variable-controls">
                <input 
                    type="number" 
                    step="0.01" 
                    class="variable-value" 
                    id="real-input-${variable.address}"
                    placeholder="Digite o valor"
                >
                <button class="btn btn-primary" onclick="writeReal(${variable.address})">
                    ✍️ Escrever
                </button>
                <button class="btn btn-success" onclick="readReal(${variable.address})">
                    📖 Ler
                </button>
            </div>
            <div class="current-value" id="real-value-${variable.address}">--</div>
        `;
        container.appendChild(item);

        // Read initial value
        readReal(variable.address);
    });
}

// Read Bool Variable
async function readBoolVariable(address) {
    try {
        const response = await fetch(`${API_BASE}/read/bool/${address}`);
        const data = await response.json();

        if (data.success) {
            updateBoolDisplay(address, data.value);
        } else {
            showToast(`❌ Erro ao ler BOOL @${address}: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error(`Erro ao ler BOOL @${address}:`, error);
    }
}

// Update Bool Display
function updateBoolDisplay(address, value) {
    const toggle = document.getElementById(`toggle-${address}`);
    const display = document.getElementById(`bool-value-${address}`);

    if (toggle && display) {
        if (value) {
            toggle.classList.add('active');
            display.textContent = 'ON';
            display.classList.add('bool-true');
            display.classList.remove('bool-false');
        } else {
            toggle.classList.remove('active');
            display.textContent = 'OFF';
            display.classList.add('bool-false');
            display.classList.remove('bool-true');
        }
    }
}

// Toggle Bool Variable
async function toggleBool(address) {
    const toggle = document.getElementById(`toggle-${address}`);
    const currentValue = toggle.classList.contains('active');
    const newValue = !currentValue;

    try {
        const response = await fetch(`${API_BASE}/write/bool/${address}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ value: newValue })
        });

        const data = await response.json();

        if (data.success) {
            updateBoolDisplay(address, newValue);
            showToast(`✅ BOOL @${address} = ${newValue ? 'ON' : 'OFF'}`, 'success');
        } else {
            showToast(`❌ Erro ao escrever BOOL @${address}: ${data.error}`, 'error');
        }
    } catch (error) {
        showToast(`❌ Erro: ${error.message}`, 'error');
    }
}

// Write Int Variable
async function writeInt(address) {
    const input = document.getElementById(`int-input-${address}`);
    const value = parseInt(input.value);

    if (isNaN(value)) {
        showToast('❌ Digite um valor válido', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/write/int/${address}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ value })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`✅ INT @${address} = ${value}`, 'success');
            readInt(address); // Update display
            input.value = ''; // Clear input
        } else {
            showToast(`❌ Erro ao escrever INT @${address}: ${data.error}`, 'error');
        }
    } catch (error) {
        showToast(`❌ Erro: ${error.message}`, 'error');
    }
}

// Read Int Variable
async function readInt(address) {
    try {
        const response = await fetch(`${API_BASE}/read/int/${address}`);
        const data = await response.json();

        if (data.success) {
            const display = document.getElementById(`int-value-${address}`);
            if (display) {
                display.textContent = data.value;
            }
        } else {
            showToast(`❌ Erro ao ler INT @${address}: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error(`Erro ao ler INT @${address}:`, error);
    }
}

// Write Real Variable
async function writeReal(address) {
    const input = document.getElementById(`real-input-${address}`);
    const value = parseFloat(input.value);

    if (isNaN(value)) {
        showToast('❌ Digite um valor válido', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/write/real/${address}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ value })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`✅ REAL @${address} = ${value.toFixed(2)}`, 'success');
            readReal(address); // Update display
            input.value = ''; // Clear input
        } else {
            showToast(`❌ Erro ao escrever REAL @${address}: ${data.error}`, 'error');
        }
    } catch (error) {
        showToast(`❌ Erro: ${error.message}`, 'error');
    }
}

// Read Real Variable
async function readReal(address) {
    try {
        const response = await fetch(`${API_BASE}/read/real/${address}`);
        const data = await response.json();

        if (data.success) {
            const display = document.getElementById(`real-value-${address}`);
            if (display) {
                display.textContent = data.value.toFixed(2);
            }
        } else {
            showToast(`❌ Erro ao ler REAL @${address}: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error(`Erro ao ler REAL @${address}:`, error);
    }
}

// Read All Variables
async function readAllVariables() {
    try {
        showToast('🔄 Lendo todas as variáveis...', 'success');
        
        const response = await fetch(`${API_BASE}/read_all`);
        const result = await response.json();

        if (result.success) {
            const data = result.data;

            // Update Bool variables
            Object.entries(data.bool).forEach(([name, info]) => {
                if (!info.error) {
                    updateBoolDisplay(info.address, info.value);
                }
            });

            // Update Int variables
            Object.entries(data.int).forEach(([name, info]) => {
                if (!info.error) {
                    const display = document.getElementById(`int-value-${info.address}`);
                    if (display) {
                        display.textContent = info.value;
                    }
                }
            });

            // Update Real variables
            Object.entries(data.real).forEach(([name, info]) => {
                if (!info.error) {
                    const display = document.getElementById(`real-value-${info.address}`);
                    if (display) {
                        display.textContent = info.value.toFixed(2);
                    }
                }
            });

            showToast('✅ Todas as variáveis atualizadas!', 'success');
        } else {
            showToast(`❌ Erro ao ler variáveis: ${result.error}`, 'error');
        }
    } catch (error) {
        showToast(`❌ Erro: ${error.message}`, 'error');
    }
}

// Auto-refresh values every 5 seconds
let autoRefreshInterval;

function startAutoRefresh() {
    autoRefreshInterval = setInterval(() => {
        readAllVariables();
    }, 5000);
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    loadVariables();
    startAutoRefresh();
});

// Stop refresh on page unload
window.addEventListener('beforeunload', () => {
    stopAutoRefresh();
});
