# Archivo modules/equipos.py - Optimizado para comunicaciones más rápidas

import pyvisa
import time

class Equipo:
    def __init__(self, ip, puerto, timeout=5000):  # Reducido el timeout por defecto
        self.ip = ip
        self.puerto = puerto
        self.timeout = timeout
        self.instrumento = None
        self.resource_manager = None
    
    def conectar(self):
        try:
            # Reutilizar el resource manager si ya existe
            if not self.resource_manager:
                self.resource_manager = pyvisa.ResourceManager('@py')
                
            cadena_recurso = f'TCPIP0::{self.ip}::{self.puerto}::SOCKET'
            
            self.instrumento = self.resource_manager.open_resource(cadena_recurso)
            self.instrumento.timeout = self.timeout
            self.instrumento.read_termination = '\n'
            self.instrumento.write_termination = '\n'
            
            return True, None
        except Exception as e:
            return False, str(e)
    
    def desconectar(self):
        if self.instrumento:
            try:
                self.instrumento.close()
                self.instrumento = None
                return True
            except Exception as e:
                return False
        return True
    
    def enviar_comando(self, comando):
        if not self.instrumento:
            return None, "No hay conexión con el instrumento"
        
        try:
            self.instrumento.write(comando)
            return True, None
        except Exception as e:
            return None, str(e)
    
    def enviar_query(self, query):
        if not self.instrumento:
            return None, "No hay conexión con el instrumento"
        
        try:
            respuesta = self.instrumento.query(query).strip()
            return respuesta, None
        except Exception as e:
            # Intentar recuperar la conexión si hay un timeout
            if "timeout" in str(e).lower():
                try:
                    # Limpiar búfer
                    self.instrumento.clear()
                    # Reintentar una vez
                    respuesta = self.instrumento.query(query).strip()
                    return respuesta, None
                except Exception as e2:
                    return None, f"Error en reintento: {str(e2)}"
            return None, str(e)
    
    def identificar(self):
        return self.enviar_query("*IDN?")

class Osciloscopio(Equipo):
    def __init__(self, ip, puerto, timeout=5000):
        super().__init__(ip, puerto, timeout)
    
    def auto_setup(self):
        return self.enviar_comando(":AUTOSet")
    
    def detener(self):
        return self.enviar_comando(":STOP")
    
    def iniciar(self):
        return self.enviar_comando(":RUN")
    
    def configurar_canal(self, canal, acoplamiento="AC", display="ON", posicion=0):
        try:
            # Enviar todos los comandos en una sola transmisión para mayor eficiencia
            comandos = [
                f":CHANnel{canal}:COUPling {acoplamiento}",
                f":CHANnel{canal}:DISPlay {display}",
                f":CHANnel{canal}:POSition {posicion}"
            ]
            
            for cmd in comandos:
                resultado, error = self.enviar_comando(cmd)
                if error:
                    return None, error
                    
            return True, None
        except Exception as e:
            return None, str(e)
    
    def obtener_medicion(self, canal, tipo_medicion):
        try:
            # Limpiar todas las mediciones actuales
            self.enviar_comando(':MEASure:CLEar ALL')
            time.sleep(0.2)  # Reducido de 0.5 a 0.2
            
            # Configurar las fuentes para la medición
            self.enviar_comando(f':MEASure:SOURce1 {canal}')
            self.enviar_comando(f':MEASure:SOURce2 {canal}')
            time.sleep(0.2)  # Reducido de 0.5 a 0.2
            
            # Activar la medición específica y obtener resultado
            if tipo_medicion == "PK2PK":
                self.enviar_comando(':MEASure:PK2PK ON')
                time.sleep(0.2)  # Reducido de 0.5 a 0.2
                resultado, error = self.enviar_query(':MEASure:PK2PK?')
            elif tipo_medicion == "AMPLITUDE":
                self.enviar_comando(':MEASure:AMPlitude ON')
                time.sleep(0.2)  # Reducido de 0.5 a 0.2
                resultado, error = self.enviar_query(':MEASure:AMPlitude?')
            elif tipo_medicion == "FREQUENCY":
                self.enviar_comando(':MEASure:FREQuency ON')
                time.sleep(0.2)  # Reducido de 0.5 a 0.2
                resultado, error = self.enviar_query(':MEASure:FREQuency?')
            elif tipo_medicion == "RMS":
                self.enviar_comando(':MEASure:RMS ON')
                time.sleep(0.2)  # Reducido de 0.5 a 0.2
                resultado, error = self.enviar_query(':MEASure:RMS?')
            else:
                return None, "Tipo de medición no reconocido"
            
            if error:
                return None, error
            
            try:
                # Convertir a número
                valor = float(resultado)
                return valor, None
            except ValueError:
                return resultado, None
            
        except Exception as e:
            return None, str(e)

class GeneradorFunciones(Equipo):
    def __init__(self, ip, puerto, timeout=5000):
        super().__init__(ip, puerto, timeout)
    
    def reset(self):
        return self.enviar_comando("*RST")
    
    def configurar_forma_onda(self, canal=1, forma="SINusoid"):
        return self.enviar_comando(f"SOURce{canal}:FUNCtion {forma}")
    
    def configurar_frecuencia(self, canal=1, frecuencia=1000):
        return self.enviar_comando(f"SOURce{canal}:FREQuency {frecuencia}")
    
    def configurar_amplitud(self, canal=1, amplitud=1):
        return self.enviar_comando(f"SOURce{canal}:AMPlitude {amplitud}")
    
    def configurar_offset(self, canal=1, offset=0):
        return self.enviar_comando(f"SOURce{canal}:DCOffset {offset}")
    
    def activar_salida(self, canal=1):
        return self.enviar_comando(f"OUTPut{canal} ON")
    
    def desactivar_salida(self, canal=1):
        return self.enviar_comando(f"OUTPut{canal} OFF")
    
    def obtener_estado_salida(self, canal=1):
        return self.enviar_query(f"OUTPut{canal}?")
    
    def configuracion_completa(self, canal=1, forma="SINusoid", frecuencia=1000, amplitud=0.05, offset=0):
        """Configura todos los parámetros de la señal de una vez"""
        try:
            # Enviamos la configuración sin reset para mayor velocidad
            self.configurar_forma_onda(canal, forma)
            self.configurar_frecuencia(canal, frecuencia)
            self.configurar_amplitud(canal, amplitud)
            self.configurar_offset(canal, offset)
            
            # Verificar configuración
            forma_actual, _ = self.enviar_query(f"SOURce{canal}:FUNCtion?")
            frecuencia_actual, _ = self.enviar_query(f"SOURce{canal}:FREQuency?")
            amplitud_actual, _ = self.enviar_query(f"SOURce{canal}:AMPlitude?")
            offset_actual, _ = self.enviar_query(f"SOURce{canal}:DCOffset?")
            
            return {
                "forma": forma_actual,
                "frecuencia": frecuencia_actual,
                "amplitud": amplitud_actual,
                "offset": offset_actual
            }, None
        except Exception as e:
            return None, str(e)
