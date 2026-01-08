// API Base URL - usa o mesmo host que está acessando (funciona no PC e celular)
const API_URL = `http://${window.location.hostname}:5000/api`;

// Function to show messages
function showMessage(message, type = 'success') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.textContent = message;
    document.body.appendChild(messageDiv);

    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}

// Generic read variable function
async function readVariable(name, type, address) {
    const valueDisplayEl = document.getElementById(`value_${name}`);
    valueDisplayEl.textContent = '...';

    try {
        let endpoint, addressIndex;

        if (type === 'BOOL') {
            endpoint = `${API_URL}/bool/read`;
            addressIndex = address - 1; // Coil address to 0-based index
        } else if (type === 'INT') {
            endpoint = `${API_URL}/int/read`;
            addressIndex = address - 40001; // HR address to 0-based index
        } else if (type === 'REAL') {
            endpoint = `${API_URL}/real/read`;
            addressIndex = address - 40001; // HR address to 0-based index
        }

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ address: addressIndex })
        });

        const data = await response.json();

        if (data.error) {
            valueDisplayEl.textContent = '❌';
            showMessage(`Erro ao ler ${name}: ${data.error}`, 'error');
        } else {
            if (type === 'BOOL') {
                valueDisplayEl.textContent = data.value ? 'True (1)' : 'False (0)';
            } else if (type === 'INT') {
                valueDisplayEl.textContent = data.value.toString();
            } else if (type === 'REAL') {
                valueDisplayEl.textContent = data.value.toFixed(2) + ' °C';
            }
            showMessage(`✅ ${name} lido com sucesso!`, 'success');
        }

    } catch (error) {
        valueDisplayEl.textContent = '❌';
        showMessage(`Erro: ${error.message}`, 'error');
    }
}

// Generic write variable function
async function writeVariable(name, type, address) {
    const inputEl = document.getElementById(`input_${name}`);
    const valueDisplayEl = document.getElementById(`value_${name}`);

    try {
        let endpoint, addressIndex, value;

        if (type === 'BOOL') {
            endpoint = `${API_URL}/bool/write`;
            addressIndex = address - 1; // Coil address to 0-based index
            value = parseInt(inputEl.value) === 1;
        } else if (type === 'INT') {
            endpoint = `${API_URL}/int/write`;
            addressIndex = address - 40001; // HR address to 0-based index
            value = parseInt(inputEl.value);

            if (isNaN(value) || value < -32768 || value > 32767) {
                showMessage('Valor INT inválido (-32768 a 32767)', 'error');
                return;
            }
        } else if (type === 'REAL') {
            endpoint = `${API_URL}/real/write`;
            addressIndex = address - 40001; // HR address to 0-based index
            value = parseFloat(inputEl.value);

            if (isNaN(value)) {
                showMessage('Valor REAL inválido', 'error');
                return;
            }
        }

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ address: addressIndex, value: value })
        });

        const data = await response.json();

        if (data.error) {
            showMessage(`Erro ao escrever ${name}: ${data.error}`, 'error');
        } else {
            showMessage(`✅ ${name} escrito com sucesso!`, 'success');
            // Auto-read after write
            setTimeout(() => readVariable(name, type, address), 500);
        }

    } catch (error) {
        showMessage(`Erro: ${error.message}`, 'error');
    }
}

// Auto-read all values on page load
window.addEventListener('DOMContentLoaded', function () {
    // Wait a bit for page to fully load
    setTimeout(() => {
        // Read all variables
        readVariable('PC_Start', 'BOOL', 1);
        readVariable('PC_Stop', 'BOOL', 2);
        readVariable('PC_Estado', 'INT', 40003);
    }, 1000);

    // Auto-refresh removed for control page
});
