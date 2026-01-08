"""
Analisador de padrões de temperatura usando Google Gemini AI
Requer: pip install google-generativeai python-dotenv
"""

import os
from datetime import datetime
from pathlib import Path

# Carregar variáveis do arquivo .env
try:
    from dotenv import load_dotenv
    # Carregar .env do diretório do script
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    print(f"[AI ANALYZER] Carregando configurações de: {env_path}")
except ImportError:
    print("[AI ANALYZER] python-dotenv não instalado - usando variáveis de ambiente do sistema")

# Verificar disponibilidade de APIs de IA
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None

if not GEMINI_AVAILABLE and not GROQ_AVAILABLE:
    print("[AI ANALYZER] ⚠️ Nenhuma API de IA disponível - rodando em modo automático")
    print("[AI ANALYZER] Instale: pip install google-generativeai groq")

class TemperatureAIAnalyzer:
    """Analisa padrões de temperatura usando IA"""
    
    def __init__(self, api_key=None, groq_api_key=None, provider=None):
        """
        Args:
            api_key: Google Gemini API key (ou usa variável GEMINI_API_KEY)
            groq_api_key: Groq API key (ou usa variável GROQ_API_KEY)
            provider: 'gemini', 'groq' ou None (auto-detecta)
        """
        self.gemini_key = api_key or os.getenv('GEMINI_API_KEY')
        self.groq_key = groq_api_key or os.getenv('GROQ_API_KEY')
        self.provider = provider
        self.model = None
        self.groq_client = None
        
        # Auto-detectar qual provider usar
        if not self.provider:
            if self.groq_key and GROQ_AVAILABLE:
                self.provider = 'groq'
            elif self.gemini_key and GEMINI_AVAILABLE:
                self.provider = 'gemini'
        
        # Inicializar Groq
        if self.provider == 'groq' and GROQ_AVAILABLE and self.groq_key:
            try:
                self.groq_client = Groq(api_key=self.groq_key)
                print("[AI ANALYZER] 🚀 Groq AI configurado ✅ (Rápido & Gratuito)")
            except Exception as e:
                print(f"[AI ANALYZER] Erro ao configurar Groq: {e}")
                self.groq_client = None
        
        # Inicializar Gemini
        elif self.provider == 'gemini' and GEMINI_AVAILABLE and self.gemini_key:
            try:
                genai.configure(api_key=self.gemini_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                print("[AI ANALYZER] Google Gemini configurado ✅")
            except Exception as e:
                print(f"[AI ANALYZER] Erro ao configurar Gemini: {e}")
                self.model = None
        
        if not self.model and not self.groq_client:
            print("[AI ANALYZER] Rodando sem IA (forneça GEMINI_API_KEY ou GROQ_API_KEY)")
    
    def analyze_temperature_data(self, readings, statistics=None):
        """
        Analisa padrões de temperatura e gera insights
        
        Args:
            readings: Lista de leituras [{timestamp, temperature, anomaly}, ...]
            statistics: Dict com estatísticas opcionais
            
        Returns:
            Dict com análise ou fallback sem IA
        """
        if not self.model and not self.groq_client:
            print("[AI ANALYZER] Modelo não configurado - usando fallback")
            return self._fallback_analysis(readings, statistics)
        
        try:
            # Preparar dados para IA
            prompt = self._build_prompt(readings, statistics)
            
            print(f"[AI ANALYZER] Chamando {self.provider.upper()} com {len(readings)} leituras...")
            
            # Chamar API com retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Groq API
                    if self.provider == 'groq' and self.groq_client:
                        response = self.groq_client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.7,
                            max_tokens=1024
                        )
                        response_text = response.choices[0].message.content
                    
                    # Gemini API
                    elif self.provider == 'gemini' and self.model:
                        response = self.model.generate_content(prompt)
                        if not response or not response.text:
                            raise ValueError("Resposta vazia do Gemini")
                        response_text = response.text
                    
                    else:
                        raise ValueError("Nenhum provider configurado")
                    
                    print(f"[AI ANALYZER] ✅ {self.provider.upper()} respondeu com sucesso!")
                    
                    return {
                        'ai_powered': True,
                        'provider': self.provider,
                        'analysis': response_text,
                        'timestamp': datetime.now().isoformat(),
                        'data_points': len(readings)
                    }
                    
                except Exception as retry_error:
                    print(f"[AI ANALYZER] Tentativa {attempt + 1}/{max_retries} falhou: {type(retry_error).__name__}: {retry_error}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(1)  # Aguardar antes de retry
                    else:
                        raise  # Re-raise na última tentativa
            
        except Exception as e:
            print(f"[AI ANALYZER] ❌ ERRO CRÍTICO {self.provider.upper() if self.provider else 'IA'}: {type(e).__name__}")
            print(f"[AI ANALYZER] Detalhes: {str(e)}")
            print(f"[AI ANALYZER] Voltando para modo automático...")
            return self._fallback_analysis(readings, statistics)
    
    def _build_prompt(self, readings, statistics):
        """Constrói prompt para Gemini"""
        
        # Resumo dos dados
        temps = [r['temperature'] for r in readings]
        anomalies = [r for r in readings if r.get('anomaly')]
        
        prompt = f"""
Você é um especialista em análise de processos industriais. Analise os seguintes dados de temperatura de um sistema industrial:

**Dados Coletados:**
- Total de leituras: {len(readings)}
- Período: {readings[0]['timestamp']} até {readings[-1]['timestamp']}
- Temperatura mínima: {min(temps):.2f}°C
- Temperatura máxima: {max(temps):.2f}°C
- Temperatura média: {sum(temps)/len(temps):.2f}°C
"""
        
        if statistics:
            prompt += f"""
**Estatísticas:**
- Desvio padrão: {statistics.get('stdev', 0):.2f}°C
- Anomalias detectadas: {statistics.get('anomalies', 0)}
"""
        
        # Amostra de valores recentes
        recent = readings[-20:]
        prompt += "\n**Últimas 20 leituras:**\n"
        for r in recent:
            marker = "⚠️" if r.get('anomaly') else "  "
            prompt += f"{marker} {r['timestamp']}: {r['temperature']:.2f}°C\n"
        
        prompt += """

**Tarefa:**
Analise estes dados e forneça:

1. **Tendência**: A temperatura está estável, crescente ou decrescente?
2. **Padrões**: Há ciclos ou variações periódicas?
3. **Anomalias**: As variações bruscas indicam problema?
4. **Recomendações**: Sugestões para otimização ou alertas

Seja conciso e objetivo. Foque em insights práticos para o operador.
"""
        
        return prompt
    
    def _fallback_analysis(self, readings, statistics):
        """Análise básica sem IA"""
        
        if not readings:
            return {
                'ai_powered': False,
                'analysis': 'Sem dados suficientes para análise',
                'timestamp': datetime.now().isoformat()
            }
        
        temps = [r['temperature'] for r in readings]
        anomalies = sum(1 for r in readings if r.get('anomaly'))
        
        # Calcular tendência simples
        if len(temps) >= 10:
            recent_avg = sum(temps[-10:]) / 10
            older_avg = sum(temps[:10]) / 10
            trend_diff = recent_avg - older_avg
            
            if trend_diff > 1:
                trend = "📈 Crescente (+" + f"{trend_diff:.1f}°C)"
            elif trend_diff < -1:
                trend = "📉 Decrescente (" + f"{trend_diff:.1f}°C)"
            else:
                trend = "➡️ Estável"
        else:
            trend = "Dados insuficientes"
        
        analysis = f"""
**Análise Automática** (sem IA)

🌡️ **Faixa de Temperatura**
   Mínima: {min(temps):.1f}°C | Máxima: {max(temps):.1f}°C | Média: {sum(temps)/len(temps):.1f}°C

📊 **Tendência Recente**
   {trend}

⚠️ **Anomalias**
   {anomalies} variações bruscas detectadas
   {'   ⚠️ ATENÇÃO: Muitas variações!' if anomalies > len(temps) * 0.1 else '   ✅ Comportamento normal'}

💡 **Recomendação**
   {'   Investigar causa das variações bruscas' if anomalies > 5 else '   Sistema operando dentro dos parâmetros esperados'}
"""
        
        if statistics:
            stdev = statistics.get('stdev', 0)
            if stdev > 5:
                analysis += f"\n   ⚠️ Alta variabilidade (σ={stdev:.1f}°C)"
        
        return {
            'ai_powered': False,
            'analysis': analysis.strip(),
            'timestamp': datetime.now().isoformat(),
            'data_points': len(readings),
            'trend': trend,
            'anomalies': anomalies
        }
    
    def generate_report(self, readings, statistics, analysis):
        """Gera relatório textual completo"""
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║        RELATÓRIO DE ANÁLISE DE TEMPERATURA                   ║
╚══════════════════════════════════════════════════════════════╝

Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Período analisado: {statistics.get('period_hours', 24)}h
Pontos de dados: {statistics.get('count', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ESTATÍSTICAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Temperatura Mínima:     {statistics.get('min', 0):.2f}°C
Temperatura Máxima:     {statistics.get('max', 0):.2f}°C
Temperatura Média:      {statistics.get('avg', 0):.2f}°C
Desvio Padrão:          {statistics.get('stdev', 0):.2f}°C
Anomalias Detectadas:   {statistics.get('anomalies', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ANÁLISE {'(IA - Google Gemini)' if analysis.get('ai_powered') else '(Automática)'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{analysis.get('analysis', 'Sem análise disponível')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return report
