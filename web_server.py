from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from modbus_client import ModbusCLP
import threading
import time

app = Flask(__name__)
CORS(app)

# ============================================
# CONFIGURAÇÃO DO CLP - AJUSTE AQUI!
# ============================================
# Para conectar ao MOCK SERVER (testes):
#   CLP_IP = 'localhost'
#   CLP_PORT = 5020
# 
# Para conectar ao CLP REAL:
#   CLP_IP = '192.168.0.200'  # Substitua pelo IP do seu CLP
#   CLP_PORT = 502
# ============================================

CLP_IP = '192.168.0.200'  # ✅ Conectado ao CLP REAL
CLP_PORT = 502  # ✅ Porta Modbus padrão

# Instância global do cliente Modbus
clp = None
clp_lock = threading.Lock()

def get_clp_connection():
    """Retorna ou cria uma conexão com o CLP."""
    global clp
    with clp_lock:
        if clp is None:
            clp = ModbusCLP(ip=CLP_IP, port=CLP_PORT)
            if not clp.connect():
                raise Exception("Não foi possível conectar ao CLP")
        return clp

# Definição das variáveis disponíveis (conforme mapeamento do CLP)
# NOTA: Modbus usa endereços 0-based, então Coil 1 = address 0
VARIABLES = {
    'bool': [
        {'name': 'PC_Start', 'address': 0, 'description': 'Comando Start (Coil 1)'},
        {'name': 'PC_Stop', 'address': 1, 'description': 'Comando Stop (Coil 2)'},
        {'name': 'PC_Falha', 'address': 2, 'description': 'Indicação Falha (Coil 3)'},
    ],
    'int': [
        {'name': 'PC_Estado', 'address': 0, 'description': 'Estado da Máquina (HR 40001)'},
    ],
    'real': [
        {'name': 'PC_Temp', 'address': 1, 'description': 'Temperatura °C (HR 40002-40003)'},
    ]
}

@app.route('/')
def index():
    """Página principal."""
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Retorna a configuração atual do CLP."""
    return jsonify({
        'ip': CLP_IP,
        'port': CLP_PORT,
        'connected': clp is not None
    })

@app.route('/api/config', methods=['POST'])
def set_config():
    """Atualiza a configuração do CLP."""
    global CLP_IP, CLP_PORT, clp
    data = request.json
    
    with clp_lock:
        # Fecha conexão anterior
        if clp:
            clp.close()
            clp = None
        
        # Atualiza configuração
        CLP_IP = data.get('ip', CLP_IP)
        CLP_PORT = int(data.get('port', CLP_PORT))
        
    return jsonify({'success': True, 'ip': CLP_IP, 'port': CLP_PORT})

@app.route('/api/variables', methods=['GET'])
def get_variables():
    """Retorna todas as variáveis disponíveis."""
    return jsonify(VARIABLES)

@app.route('/api/read/<var_type>/<int:address>', methods=['GET'])
def read_variable(var_type, address):
    """Lê uma variável do CLP."""
    try:
        clp_conn = get_clp_connection()
        
        if var_type == 'bool':
            value = clp_conn.read_bool(address)
        elif var_type == 'int':
            value = clp_conn.read_int(address)
        elif var_type == 'real':
            value = clp_conn.read_real(address)
        else:
            return jsonify({'success': False, 'error': 'Tipo inválido'}), 400
        
        return jsonify({'success': True, 'value': value})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/write/<var_type>/<int:address>', methods=['POST'])
def write_variable(var_type, address):
    """Escreve uma variável no CLP."""
    try:
        data = request.json
        value = data.get('value')
        
        if value is None:
            return jsonify({'success': False, 'error': 'Valor não fornecido'}), 400
        
        clp_conn = get_clp_connection()
        
        if var_type == 'bool':
            clp_conn.write_bool(address, bool(value))
        elif var_type == 'int':
            clp_conn.write_int(address, int(value))
        elif var_type == 'real':
            clp_conn.write_real(address, float(value))
        else:
            return jsonify({'success': False, 'error': 'Tipo inválido'}), 400
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/read_all', methods=['GET'])
def read_all_variables():
    """Lê todas as variáveis do CLP."""
    try:
        clp_conn = get_clp_connection()
        results = {'bool': {}, 'int': {}, 'real': {}}
        
        for var_type, variables in VARIABLES.items():
            for var in variables:
                try:
                    address = var['address']
                    if var_type == 'bool':
                        value = clp_conn.read_bool(address)
                    elif var_type == 'int':
                        value = clp_conn.read_int(address)
                    elif var_type == 'real':
                        value = clp_conn.read_real(address)
                    
                    results[var_type][var['name']] = {
                        'value': value,
                        'address': address,
                        'description': var['description']
                    }
                except Exception as e:
                    results[var_type][var['name']] = {
                        'error': str(e),
                        'address': address,
                        'description': var['description']
                    }
        
        return jsonify({'success': True, 'data': results})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("  🚀 WEB SERVER MODBUS CLP")
    print("=" * 60)
    print(f"  📡 CLP: {CLP_IP}:{CLP_PORT}")
    print(f"  🌐 Servidor Web: http://localhost:5000")
    print("=" * 60)
    print("\n  Abra o navegador em: http://localhost:5000\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
