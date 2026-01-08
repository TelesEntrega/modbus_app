from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian
import logging

class ModbusCLP:
    def __init__(self, ip='192.168.0.200', port=502):
        self.ip = ip
        self.port = port
        self.client = ModbusTcpClient(ip, port=port)

    def connect(self):
        """Conecta ao CLP. Retorna True se sucesso."""
        return self.client.connect()

    def close(self):
        """Fecha a conexão."""
        self.client.close()

    def write_bool(self, address, value):
        """
        Escreve um valor Booleano em uma Coil.
        address: Endereço 0-based (ex: Coil 00001 -> address 0)
        value: True ou False
        """
        try:
            # write_coil espera endereço 0-based
            result = self.client.write_coil(address, value)
            if result.isError():
                raise Exception(f"Erro Modbus: {result}")
            return True
        except Exception as e:
            print(f"Erro ao escrever BOOL em {address}: {e}")
            raise

    def read_bool(self, address):
        """
        Lê um valor Booleano de uma Coil.
        address: Endereço 0-based
        Retorna: True ou False
        """
        try:
            result = self.client.read_coils(address, 1)
            if result.isError():
                raise Exception(f"Erro Modbus: {result}")
            return result.bits[0]
        except Exception as e:
            print(f"Erro ao ler BOOL de {address}: {e}")
            raise

    def write_int(self, address, value):
        """
        Escreve um valor INT (16-bit) em um Holding Register.
        address: Endereço 0-based (ex: HR 40001 -> address 0)
        value: Inteiro (Signed 16-bit)
        """
        try:
            builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
            builder.add_16bit_int(value)
            payload = builder.build()
            
            result = self.client.write_registers(address, payload, skip_encode=True)
            if result.isError():
                raise Exception(f"Erro Modbus: {result}")
            return True
        except Exception as e:
            print(f"Erro ao escrever INT em {address}: {e}")
            raise

    def read_int(self, address):
        """
        Lê um valor INT (16-bit) de um Holding Register.
        address: Endereço 0-based
        """
        try:
            result = self.client.read_holding_registers(address, 1)
            if result.isError():
                raise Exception(f"Erro Modbus: {result}")
            
            decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
            return decoder.decode_16bit_int()
        except Exception as e:
            print(f"Erro ao ler INT de {address}: {e}")
            raise

    def write_real(self, address, value):
        """
        Escreve um valor REAL (32-bit float) em 2 Holding Registers.
        address: Endereço 0-based inicial
        value: Float
        """
        try:
            builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
            builder.add_32bit_float(value)
            payload = builder.build()
            
            result = self.client.write_registers(address, payload, skip_encode=True)
            if result.isError():
                raise Exception(f"Erro Modbus: {result}")
            return True
        except Exception as e:
            print(f"Erro ao escrever REAL em {address}: {e}")
            raise

    def read_real(self, address):
        """
        Lê um valor REAL (32-bit float) de 2 Holding Registers.
        address: Endereço 0-based inicial
        """
        try:
            result = self.client.read_holding_registers(address, 2)
            if result.isError():
                raise Exception(f"Erro Modbus: {result}")
            
            decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
            return decoder.decode_32bit_float()
        except Exception as e:
            print(f"Erro ao ler REAL de {address}: {e}")
            raise
