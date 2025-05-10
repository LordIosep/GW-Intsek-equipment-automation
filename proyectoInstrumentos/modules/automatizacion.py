# Archivo modules/automatizacion.py - Versión actualizada

import time
from modules.equipos import Osciloscopio, GeneradorFunciones
from modules.config import cargar_frecuencias, agregar_medicion_ganancia

def ejecutar_medicion_automatica(gen_ip, gen_puerto, osc_ip, osc_puerto, 
                                frecuencia, amplitud=0.05, progreso_callback=None,
                                tiempo_estabilizacion=0.5, offset=0.0, forma_onda="SINusoid",
                                funcion_verificar_detencion=None):
    """
    Ejecuta una medición automática para una frecuencia específica
    
    Args:
        gen_ip: IP del generador de funciones
        gen_puerto: Puerto del generador de funciones
        osc_ip: IP del osciloscopio
        osc_puerto: Puerto del osciloscopio
        frecuencia: Frecuencia a configurar en el generador
        amplitud: Amplitud de la señal en Vpp
        progreso_callback: Función callback para informar progreso
        tiempo_estabilizacion: Tiempo de espera para estabilización
        offset: Offset de la señal en V
        forma_onda: Forma de onda (SINusoid, SQUare, etc.)
        funcion_verificar_detencion: Función para verificar si debe detenerse
        
    Returns:
        dict: Resultados de la medición o None en caso de error
        str: Mensaje de error o None en caso de éxito
    """
    # Inicializar equipos
    generador = None
    osciloscopio = None
    
    resultados = {}
    error_msg = None
    
    try:
        # Verificar si debemos detener la ejecución
        if funcion_verificar_detencion and funcion_verificar_detencion():
            return None, "Proceso detenido por el usuario"
            
        generador = GeneradorFunciones(gen_ip, gen_puerto)
        osciloscopio = Osciloscopio(osc_ip, osc_puerto)
        
        # Conectar generador
        if progreso_callback:
            progreso_callback(f"Conectando al generador de funciones ({gen_ip}:{gen_puerto})...")
        
        conectado, error = generador.conectar()
        if not conectado:
            return None, f"Error al conectar con el generador: {error}"
        
        # Verificar si debemos detener la ejecución
        if funcion_verificar_detencion and funcion_verificar_detencion():
            generador.desconectar()
            return None, "Proceso detenido por el usuario"
        
        # Identificar generador
        id_gen, error = generador.identificar()
        if error:
            generador.desconectar()
            return None, f"Error al identificar el generador: {error}"
            
        if progreso_callback:
            progreso_callback(f"Generador identificado: {id_gen}")
        
        # Verificar si debemos detener la ejecución
        if funcion_verificar_detencion and funcion_verificar_detencion():
            generador.desconectar()
            return None, "Proceso detenido por el usuario"
        
        # Configurar generador con los nuevos parámetros
        if progreso_callback:
            progreso_callback(f"Configurando generador a {frecuencia} Hz (forma: {forma_onda}, amplitud: {amplitud}V, offset: {offset}V)...")
        
        config, error = generador.configuracion_completa(
            canal=1, 
            forma=forma_onda,  # Usar el parámetro de forma de onda
            frecuencia=frecuencia,
            amplitud=amplitud,
            offset=offset  # Usar el parámetro de offset
        )
        
        if error:
            generador.desconectar()
            return None, f"Error al configurar el generador: {error}"
        
        # Verificar si debemos detener la ejecución
        if funcion_verificar_detencion and funcion_verificar_detencion():
            generador.desactivar_salida(1)
            generador.desconectar()
            return None, "Proceso detenido por el usuario"
        
        # Activar salida del generador
        if progreso_callback:
            progreso_callback("Activando salida del generador...")
        
        generador.activar_salida(1)
        time.sleep(tiempo_estabilizacion)  # Tiempo personalizado
        
        # Verificar si debemos detener la ejecución
        if funcion_verificar_detencion and funcion_verificar_detencion():
            generador.desactivar_salida(1)
            generador.desconectar()
            return None, "Proceso detenido por el usuario"
        
        # Conectar osciloscopio
        if progreso_callback:
            progreso_callback(f"Conectando al osciloscopio ({osc_ip}:{osc_puerto})...")
        
        conectado, error = osciloscopio.conectar()
        if not conectado:
            generador.desactivar_salida(1)
            generador.desconectar()
            return None, f"Error al conectar con el osciloscopio: {error}"
        
        # Verificar si debemos detener la ejecución
        if funcion_verificar_detencion and funcion_verificar_detencion():
            generador.desactivar_salida(1)
            generador.desconectar()
            osciloscopio.desconectar()
            return None, "Proceso detenido por el usuario"
        
        # Identificar osciloscopio
        id_osc, error = osciloscopio.identificar()
        if error:
            generador.desactivar_salida(1)
            generador.desconectar()
            osciloscopio.desconectar()
            return None, f"Error al identificar el osciloscopio: {error}"
            
        if progreso_callback:
            progreso_callback(f"Osciloscopio identificado: {id_osc}")
        
        # Verificar si debemos detener la ejecución
        if funcion_verificar_detencion and funcion_verificar_detencion():
            generador.desactivar_salida(1)
            generador.desconectar()
            osciloscopio.desconectar()
            return None, "Proceso detenido por el usuario"
        
        # Configurar osciloscopio
        if progreso_callback:
            progreso_callback("Configurando osciloscopio...")
        
        # Auto setup para ajustar escala y trigger - tiempo reducido
        osciloscopio.auto_setup()
        time.sleep(tiempo_estabilizacion)  # Tiempo personalizado
        
        # Verificar si debemos detener la ejecución
        if funcion_verificar_detencion and funcion_verificar_detencion():
            generador.desactivar_salida(1)
            generador.desconectar()
            osciloscopio.desconectar()
            return None, "Proceso detenido por el usuario"
        
        # Configurar canales
        osciloscopio.configurar_canal(1, acoplamiento="AC", display="ON", posicion=0)
        osciloscopio.configurar_canal(2, acoplamiento="AC", display="ON", posicion=0)
        
        # Detener adquisición para mediciones más precisas
        osciloscopio.detener()
        time.sleep(0.2)  # Tiempo reducido
        
        # Verificar si debemos detener la ejecución
        if funcion_verificar_detencion and funcion_verificar_detencion():
            generador.desactivar_salida(1)
            generador.desconectar()
            osciloscopio.desconectar()
            return None, "Proceso detenido por el usuario"
        
        # Realizar mediciones
        if progreso_callback:
            progreso_callback("Realizando mediciones en Canal 1...")
        
        # Mediciones en Canal 1 (entrada)
        canal1_pk2pk, error = osciloscopio.obtener_medicion("CH1", "PK2PK")
        if error:
            if progreso_callback:
                progreso_callback(f"Error en medición PK2PK CH1: {error}")
            canal1_pk2pk = 0
        
        # Verificar si debemos detener la ejecución
        if funcion_verificar_detencion and funcion_verificar_detencion():
            generador.desactivar_salida(1)
            generador.desconectar()
            osciloscopio.desconectar()
            return None, "Proceso detenido por el usuario"
            
        canal1_amplitud, error = osciloscopio.obtener_medicion("CH1", "AMPLITUDE")
        if error:
            if progreso_callback:
                progreso_callback(f"Error en medición AMPLITUDE CH1: {error}")
            canal1_amplitud = 0
        
        # Verificar si debemos detener la ejecución
        if funcion_verificar_detencion and funcion_verificar_detencion():
            generador.desactivar_salida(1)
            generador.desconectar()
            osciloscopio.desconectar()
            return None, "Proceso detenido por el usuario"
            
        if progreso_callback:
            progreso_callback("Realizando mediciones en Canal 2...")
            
        # Mediciones en Canal 2 (salida)
        canal2_pk2pk, error = osciloscopio.obtener_medicion("CH2", "PK2PK")
        if error:
            if progreso_callback:
                progreso_callback(f"Error en medición PK2PK CH2: {error}")
            canal2_pk2pk = 0
        
        # Verificar si debemos detener la ejecución
        if funcion_verificar_detencion and funcion_verificar_detencion():
            generador.desactivar_salida(1)
            generador.desconectar()
            osciloscopio.desconectar()
            return None, "Proceso detenido por el usuario"
            
        canal2_amplitud, error = osciloscopio.obtener_medicion("CH2", "AMPLITUDE")
        if error:
            if progreso_callback:
                progreso_callback(f"Error en medición AMPLITUDE CH2: {error}")
            canal2_amplitud = 0
        
        # Calcular ganancia
        if canal1_pk2pk and canal2_pk2pk:
            ganancia_pk2pk = canal2_pk2pk / canal1_pk2pk if canal1_pk2pk != 0 else 0
            ganancia_amplitud = canal2_amplitud / canal1_amplitud if canal1_amplitud != 0 else 0
            ganancia_real = (ganancia_pk2pk + ganancia_amplitud) / 2
            
            # También calcular en dB
            import math
            ganancia_pk2pk_db = 20 * math.log10(ganancia_pk2pk) if ganancia_pk2pk > 0 else float('-inf')
            ganancia_amplitud_db = 20 * math.log10(ganancia_amplitud) if ganancia_amplitud > 0 else float('-inf')
            ganancia_real_db = 20 * math.log10(ganancia_real) if ganancia_real > 0 else float('-inf')
            
            # Resultados
            resultados = {
                "frecuencia": frecuencia,
                "canal1_pk2pk": canal1_pk2pk,
                "canal1_amplitud": canal1_amplitud,
                "canal2_pk2pk": canal2_pk2pk,
                "canal2_amplitud": canal2_amplitud,
                "ganancia_pk2pk": ganancia_pk2pk,
                "ganancia_amplitud": ganancia_amplitud,
                "ganancia_real": ganancia_real,
                "ganancia_pk2pk_db": ganancia_pk2pk_db,
                "ganancia_amplitud_db": ganancia_amplitud_db,
                "ganancia_real_db": ganancia_real_db
            }
            
            # Guardar resultados
            if progreso_callback:
                progreso_callback("Guardando resultados...")
                
            # Guardar en el archivo JSON de ganancias
            try:
                guardado = agregar_medicion_ganancia(
                    frecuencia=frecuencia,
                    canal1_pk2pk=canal1_pk2pk,
                    canal1_amplitud=canal1_amplitud,
                    canal2_pk2pk=canal2_pk2pk,
                    canal2_amplitud=canal2_amplitud,
                    ganancia_pk2pk=ganancia_pk2pk,
                    ganancia_amplitud=ganancia_amplitud,
                    ganancia_real=ganancia_real
                )
                
                if not guardado and progreso_callback:
                    progreso_callback("Advertencia: No se pudieron guardar los resultados en el archivo.")
            except Exception as e:
                if progreso_callback:
                    progreso_callback(f"Error al guardar resultados: {str(e)}")
        else:
            error_msg = "No se pudieron obtener mediciones válidas para calcular la ganancia."
        
    except Exception as e:
        error_msg = f"Error durante la medición automática: {str(e)}"
    finally:
        # Limpiar
        try:
            if generador is not None and hasattr(generador, 'instrumento') and generador.instrumento:
                if progreso_callback:
                    progreso_callback("Desactivando salida del generador...")
                generador.desactivar_salida(1)
                generador.desconectar()
        except Exception as e:
            if progreso_callback:
                progreso_callback(f"Error al desconectar generador: {str(e)}")
            
        try:
            if osciloscopio is not None and hasattr(osciloscopio, 'instrumento') and osciloscopio.instrumento:
                osciloscopio.desconectar()
        except Exception as e:
            if progreso_callback:
                progreso_callback(f"Error al desconectar osciloscopio: {str(e)}")
            
        if progreso_callback:
            if error_msg:
                progreso_callback(f"Proceso completado con errores: {error_msg}")
            else:
                progreso_callback("Proceso completado exitosamente.")
    
    return resultados, error_msg

def ejecutar_secuencia_completa(gen_ip, gen_puerto, osc_ip, osc_puerto, 
                              amplitud=0.05, offset=0.0, forma_onda="SINusoid",
                              tiempo_estabilizacion=0.5, 
                              tiempo_entre_mediciones=0.5, progreso_callback=None,
                              funcion_verificar_detencion=None):
    """
    Ejecuta una secuencia completa de mediciones para todas las frecuencias definidas
    
    Args:
        gen_ip: IP del generador de funciones
        gen_puerto: Puerto del generador de funciones
        osc_ip: IP del osciloscopio
        osc_puerto: Puerto del osciloscopio
        amplitud: Amplitud de la señal en Vpp
        offset: Offset de la señal en V
        forma_onda: Forma de onda (SINusoid, SQUare, etc.)
        tiempo_estabilizacion: Tiempo de espera para estabilización
        tiempo_entre_mediciones: Tiempo de espera entre mediciones
        progreso_callback: Función callback para informar progreso
        funcion_verificar_detencion: Función para verificar si debe detenerse
        
    Returns:
        bool: True si todo fue exitoso, False en caso contrario
        str: Mensaje de error o None en caso de éxito
    """
    # Asegurar que el callback exista
    if progreso_callback is None:
        def progreso_callback(mensaje):
            print(mensaje)  # Solo imprime a consola si no hay callback
    
    # Cargar lista de frecuencias
    try:
        datos_frecuencias = cargar_frecuencias()
        frecuencias = datos_frecuencias.get("frecuencias", [])
        
        if not frecuencias:
            progreso_callback("No hay frecuencias definidas para medir.")
            return False, "No hay frecuencias definidas para medir."
        
        total_frecuencias = len(frecuencias)
        resultados_completos = []
        
        for i, frecuencia in enumerate(frecuencias):
            # Verificar si debemos detener la ejecución
            if funcion_verificar_detencion and funcion_verificar_detencion():
                progreso_callback("Secuencia detenida por el usuario.")
                return False, "Secuencia detenida por el usuario"
                
            progreso_callback(f"Iniciando medición {i+1}/{total_frecuencias}: Frecuencia {frecuencia} Hz", i+1, total_frecuencias)
            
            # Ejecutar medición para esta frecuencia
            try:
                resultado, error = ejecutar_medicion_automatica(
                    gen_ip, gen_puerto, osc_ip, osc_puerto, 
                    frecuencia, amplitud, progreso_callback,
                    tiempo_estabilizacion, offset, forma_onda,
                    funcion_verificar_detencion
                )
                
                if funcion_verificar_detencion and funcion_verificar_detencion():
                    progreso_callback("Secuencia detenida por el usuario.")
                    return False, "Secuencia detenida por el usuario"
                
                if error:
                    progreso_callback(f"Error en frecuencia {frecuencia} Hz: {error}")
                
                if resultado:
                    resultados_completos.append(resultado)
                    progreso_callback(f"Medición completada para {frecuencia} Hz")
            except Exception as e:
                progreso_callback(f"Excepción al medir frecuencia {frecuencia} Hz: {str(e)}")
                
            # Verificar si debemos detener la ejecución
            if funcion_verificar_detencion and funcion_verificar_detencion():
                progreso_callback("Secuencia detenida por el usuario.")
                return False, "Secuencia detenida por el usuario"
                
            # Pequeña pausa entre mediciones
            time.sleep(tiempo_entre_mediciones)
        
        progreso_callback(f"Secuencia completa finalizada. Se realizaron {len(resultados_completos)}/{total_frecuencias} mediciones.", total_frecuencias, total_frecuencias)
        
        return True, None
    
    except Exception as e:
        error_msg = f"Error en la secuencia completa: {str(e)}"
        progreso_callback(error_msg)
        return False, error_msg
