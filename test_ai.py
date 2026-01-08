"""
Teste rápido da integração com Google Gemini AI
"""

from ai_analyzer import TemperatureAIAnalyzer
from datetime import datetime, timedelta

# Criar analisador
analyzer = TemperatureAIAnalyzer()

# Dados de teste
readings = []
base_temp = 25.0
now = datetime.now()

for i in range(50):
    temp = base_temp + (i * 0.1) + (i % 5) * 0.5  # Simula crescimento com variação
    readings.append({
        'timestamp': (now - timedelta(minutes=50-i)).strftime('%Y-%m-%d %H:%M:%S'),
        'temperature': temp,
        'anomaly': temp > 30  # Marca anomalias acima de 30°C
    })

# Estatísticas
stats = {
    'count': len(readings),
    'min': min(r['temperature'] for r in readings),
    'max': max(r['temperature'] for r in readings),
    'avg': sum(r['temperature'] for r in readings) / len(readings),
    'stdev': 2.5,
    'anomalies': sum(1 for r in readings if r['anomaly']),
    'period_hours': 1,
}

print("=" * 70)
print("TESTE DE ANÁLISE DE TEMPERATURA COM IA")
print("=" * 70)
print()

# Testar análise
result = analyzer.analyze_temperature_data(readings, stats)

print(f"✅ Teste concluído!")
print(f"   Modo de IA ativo: {'SIM' if result['ai_powered'] else 'NÃO'}")
print(f"   Pontos analisados: {result['data_points']}")
print()
print("─" * 70)
print(result['analysis'])
print("─" * 70)
