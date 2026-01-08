// API Base URL - usa o mesmo host que está acessando (funciona no PC e celular)
const API_URL = `http://${window.location.hostname}:5000/api/temperature`;

// Global chart instance
let temperatureChart = null;
let chartDataLimit = 200;

// ==================== Initialization ====================
document.addEventListener('DOMContentLoaded', function () {
    initializeChart();
    startAutoUpdate();
    updateCurrentTemperature();
    updateStatistics();
});

// ==================== Chart Configuration ====================
function initializeChart() {
    const ctx = document.getElementById('temperatureChart').getContext('2d');

    temperatureChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Temperatura (°C)',
                data: [],
                borderColor: '#58a6ff',
                backgroundColor: 'rgba(88, 166, 255, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointRadius: function (context) {
                    // Highlight anomalies
                    const value = context.raw;
                    return value && value.anomaly ? 5 : 2;
                },
                pointBackgroundColor: function (context) {
                    const value = context.raw;
                    return value && value.anomaly ? '#f85149' : '#58a6ff';
                }
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#e6edf3'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            const value = context.raw;
                            if (typeof value === 'object') {
                                label += value.y.toFixed(2) + '°C';
                                if (value.anomaly) {
                                    label += ' ⚠️';
                                }
                            } else {
                                label += value.toFixed(2) + '°C';
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    ticks: {
                        color: '#7d8590',
                        callback: function (value) {
                            return value.toFixed(1) + '°C';
                        }
                    },
                    grid: {
                        color: '#30363d'
                    }
                },
                x: {
                    ticks: {
                        color: '#7d8590',
                        maxRotation: 45,
                        minRotation: 45
                    },
                    grid: {
                        color: '#30363d'
                    }
                }
            }
        }
    });

    updateChartData();
}

// ==================== Data Updates ====================
async function updateCurrentTemperature() {
    try {
        const response = await fetch(`${API_URL}/current`);
        const data = await response.json();

        if (data.error) {
            document.getElementById('currentTemp').textContent = '--';
            document.getElementById('tempStatus').textContent = data.error;
            return;
        }

        // Update temperature display
        document.getElementById('currentTemp').textContent = data.temperature.toFixed(1);

        // Update status
        const statusElem = document.getElementById('tempStatus');
        if (data.anomaly) {
            statusElem.textContent = '⚠️ Variação Anormal Detectada';
            statusElem.className = 'temp-status anomaly';
        } else {
            statusElem.textContent = '✅ Operação Normal';
            statusElem.className = 'temp-status';
        }

        // Update timestamp (horário local)
        const timestamp = new Date(data.timestamp);
        document.getElementById('lastUpdate').textContent = timestamp.toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

    } catch (error) {
        console.error('Error fetching current temperature:', error);
        document.getElementById('currentTemp').textContent = '--';
        document.getElementById('tempStatus').textContent = 'Erro de conexão';
    }
}

async function updateStatistics() {
    try {
        const response = await fetch(`${API_URL}/stats?hours=24`);
        const data = await response.json();

        if (data.error) {
            return;
        }

        document.getElementById('statMin').textContent = data.min.toFixed(1) + '°C';
        document.getElementById('statMax').textContent = data.max.toFixed(1) + '°C';
        document.getElementById('statAvg').textContent = data.avg.toFixed(1) + '°C';
        document.getElementById('statStdev').textContent = data.stdev.toFixed(1) + '°C';
        document.getElementById('statAnomalies').textContent = data.anomalies;
        document.getElementById('statCount').textContent = data.count;

    } catch (error) {
        console.error('Error fetching statistics:', error);
    }
}

async function updateChartData() {
    try {
        const response = await fetch(`${API_URL}/history?limit=${chartDataLimit}`);
        const result = await response.json();

        if (result.error || !result.data) {
            console.error('Error fetching history');
            return;
        }

        const data = result.data;

        // Prepare chart data (horário local)
        const labels = data.map(d => {
            const date = new Date(d.timestamp);
            return date.toLocaleTimeString('pt-BR', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        });

        const temperatures = data.map(d => ({
            x: new Date(d.timestamp),
            y: d.temperature,
            anomaly: d.anomaly
        }));

        // Update chart
        temperatureChart.data.labels = labels;
        temperatureChart.data.datasets[0].data = temperatures;
        temperatureChart.update('none'); // No animation for real-time updates

    } catch (error) {
        console.error('Error updating chart:', error);
    }
}

// ==================== Chart Controls ====================
function updateChartRange(limit) {
    chartDataLimit = limit;

    // Update active button
    document.querySelectorAll('.btn-chart').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    updateChartData();
}

// ==================== AI Analysis ====================
async function performAnalysis() {
    const btnAnalyze = document.querySelector('.btn-analyze');
    const aiAnalysis = document.getElementById('aiAnalysis');
    const aiTimestamp = document.getElementById('aiTimestamp');
    const aiStatus = document.getElementById('aiStatus');

    // Disable button and show loading
    btnAnalyze.disabled = true;
    btnAnalyze.textContent = '🔄 Analisando...';
    aiAnalysis.textContent = 'Analisando dados... Aguarde.';

    try {
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ limit: 200, hours: 24 })
        });

        const data = await response.json();

        if (data.error) {
            aiAnalysis.textContent = 'Erro: ' + data.error;
            return;
        }

        // Display analysis
        aiAnalysis.textContent = data.analysis;

        // Update footer (horário local)
        const timestamp = new Date(data.timestamp);
        aiTimestamp.textContent = 'Análise gerada em: ' + timestamp.toLocaleString('pt-BR');
        aiStatus.textContent = data.ai_powered ? '🤖 Powered by Google Gemini' : '📊 Análise Automática';

    } catch (error) {
        console.error('Error performing analysis:', error);
        aiAnalysis.textContent = 'Erro ao gerar análise: ' + error.message;
    } finally {
        btnAnalyze.disabled = false;
        btnAnalyze.textContent = '🔄 Analisar Agora';
    }
}

// ==================== Report Generation ====================
async function generateReport() {
    const reportOutput = document.getElementById('reportOutput');
    reportOutput.textContent = 'Gerando relatório...';

    try {
        const response = await fetch(`${API_URL}/report?hours=24`);
        const data = await response.json();

        if (data.error) {
            reportOutput.textContent = 'Erro: ' + data.error;
            return;
        }

        reportOutput.textContent = data.report;

    } catch (error) {
        console.error('Error generating report:', error);
        reportOutput.textContent = 'Erro ao gerar relatório: ' + error.message;
    }
}

// ==================== Auto Update ====================
function startAutoUpdate() {
    // Update every 5 seconds
    setInterval(() => {
        updateCurrentTemperature();
        updateChartData();
    }, 5000);

    // Update statistics every minute
    setInterval(() => {
        updateStatistics();
    }, 60000);
}
