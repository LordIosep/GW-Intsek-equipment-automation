import pyvisa
import time

def conectar_generador_funciones():
    rm = pyvisa.ResourceManager('@py')
    instrumento_ip = '172.118.1.233'
    instrumento_puerto = 1026
    cadena_recurso = f'TCPIP0::{instrumento_ip}::{instrumento_puerto}::SOCKET'

    try:
        # Abrir conexión con el generador de funciones
        instrumento = rm.open_resource(cadena_recurso)
        instrumento.timeout = 10000  # 10 segundos de timeout
        instrumento.read_termination = '\n'
        instrumento.write_termination = '\n'
        
        # Verificar conexión con comando de identificación
        print("Verificando conexión con *IDN?...")
        identificacion = instrumento.query('*IDN?').strip()
        print(f"Generador identificado: {identificacion}")
        
        # Cerrar conexión
        instrumento.close()
        print("Conexión cerrada correctamente")
        return True
    except Exception as e:
        print(f"Error al conectar con el generador: {e}")
        print(f"Tipo de error: {type(e).__name__}")
        print("Verificar que la dirección IP y puerto sean correctos")
        return False

if __name__ == "__main__":
    conectar_generador_funciones()
