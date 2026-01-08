import logging
import asyncio
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSparseDataBlock

# Configuração de Logs
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

async def run_server():
    # Mapeamento de Memória (Endianness Big Endian é padrão no pymodbus)
    # Coil 00001 (Address 0): OPC_Start
    # HR 40001 (Address 0): OPC_Estado (INT)
    # HR 40002 (Address 1): OPC_Temp (REAL - 2 words) -> Ocupa 1 e 2
    # HR 40004 (Address 3): Watchdog (INT)

    # Inicializa com valores vazios/zeros
    # Coils (0x01)
    store_coils = ModbusSequentialDataBlock(0, [False]*100)
    
    # Holding Registers (0x03)
    # Address 0: INT
    # Address 1-2: FLOAT (2 words)
    # Address 3: INT
    # Vamos criar um bloco esparso ou sequencial grande o suficiente
    store_hr = ModbusSequentialDataBlock(0, [0]*100)

    # Cria o contexto do escravo (Slave ID 0 ou padrão é 0x00 broadcast ou unit=1 geralmente)
    # Pymodbus server geralmente responde a qualquer ID se single=True
    store = ModbusSlaveContext(
        di=None,            # Discrete Inputs
        co=store_coils,     # Coils
        hr=store_hr,        # Holding Registers
        ir=None,            # Input Registers
        zero_mode=True      # Endereçamento 0-based
    )
    
    context = ModbusServerContext(slaves=store, single=True)

    # Identificação do Dispositivo (Opcional)
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Mock Server'
    identity.ProductCode = 'MOCK'
    identity.VendorUrl = 'http://github.com/pymodbus-dev/pymodbus/'
    identity.ProductName = 'Mock Modbus Server'
    identity.ModelName = 'Mock Server'
    identity.MajorMinorRevision = '1.0'

    print("=== MOCK MODBUS SERVER INICIADO ===")
    print("Escutando em localhost:5020 (Porta alterada para não exigir admin)")
    print("Mapeamento:")
    print("  Coil 0: OPC_Start")
    print("  HR 0: OPC_Estado")
    print("  HR 1-2: OPC_Temp")
    print("  HR 3: Watchdog")
    
    # Inicia o servidor
    # Usando porta 5020 para evitar permissão de admin (502 requer)
    await StartAsyncTcpServer(context=context, identity=identity, address=("localhost", 5020))

if __name__ == "__main__":
    try:
        if hasattr(asyncio, "run"):
            asyncio.run(run_server())
        else:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(run_server())
    except KeyboardInterrupt:
        print("Servidor encerrado.")
