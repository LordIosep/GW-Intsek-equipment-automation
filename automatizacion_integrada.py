import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime

def barrido_frecuencias_automatizado():
    # Crear directorio para guardar resultados
    os.makedirs("resultados", exist_ok=True)
    
    # Configuración de conexión
    rm = pyvisa.ResourceManager('@py')
    
    # Configuración de conexión para el generador de funciones
    generador_ip = '172.118.1.233'
    generador_puerto = 1026
    generador_recurso = f'TCPIP0::{generador_ip}::{generador_puerto}::SOCKET'
    
    # Configuración de conexión para el osciloscopio
    osciloscopio_ip = '172.118.1.235'
    osciloscopio_puerto = 3000
    osciloscopio_recurso = f'TCPIP0::{osciloscopio_ip}::{osciloscopio_puerto}::SOCKET'
    
    # Generar 15 frecuencias logarítmicas entre 10 Hz y 1 MHz
    frecuencias = np.logspace(1, 6, 15)  # 10 Hz a 1 MHz, 15 puntos
    
    # Variables para almacenar resultados
    resultados = []
    
    try:
        print("=== INICIANDO BARRIDO DE FRECUENCIAS PARA DIAGRAMA DE BODE ===\n")
        
        # Conectar con el generador de funciones
        print("Conectando con el generador de funciones...")
        generador = rm.open_resource(generador_recurso)
        generador.timeout = 10000
        generador.read_termination = '\n'
        generador.write_termination = '\n'
        
        # Verificar conexión con el generador
        id_generador = generador.query('*IDN?').strip()
        print(f"Generador identificado: {id_generador}")
        
        # Conectar con el osciloscopio
        print("\nConectando con el osciloscopio...")
        osciloscopio = rm.open_resource(osciloscopio_recurso)
        osciloscopio.timeout = 10000
        osciloscopio.read_termination = '\n'
        osciloscopio.write_termination = '\n'
        
        # Verificar conexión con el osciloscopio
        id_osciloscopio = osciloscopio.query('*IDN?').strip()
        print(f"Osciloscopio identificado: {id_osciloscopio}")
        
        # Realizar barrido de frecuencias
        print("\n=== INICIANDO BARRIDO DE FRECUENCIAS ===")
        print(f"Se medirán {len(frecuencias)} frecuencias entre 10 Hz y 1 MHz")
        
        for i, frecuencia in enumerate(frecuencias):
            frecuencia_redondeada = round(frecuencia, 2)
            print(f"\n[{i+1}/{len(frecuencias)}] Midiendo a {frecuencia_redondeada} Hz")
            
            # 1. Configurar el generador para esta frecuencia
            print(f"Configurando generador a {frecuencia_redondeada} Hz...")
            generador.write('*RST')  # Reset
            time.sleep(0.5)
            
            # Configuración de la señal
            generador.write('SOURce1:FUNCtion SINusoid')  # Senoidal
            generador.write(f'SOURce1:FREQuency {frecuencia_redondeada}')  # Frecuencia
            generador.write('SOURce1:AMPlitude 0.05')  # Amplitud: 50 mVpp
            generador.write('SOURce1:DCOffset 0')  # Sin offset
            
            # Activar salida del generador
            generador.write('OUTPut1 ON')
            time.sleep(1)  # Esperar a que la señal se estabilice
            
            # 2. Configurar el osciloscopio y realizar mediciones
            print("Configurando osciloscopio...")
            osciloscopio.write(':AUTOSet')  # Ajuste automático
            time.sleep(2)  # Esperar a que complete el autoajuste
            
            # 3. Medir señal de entrada (Canal 1)
            print("Midiendo señal de entrada (CH1)...")
            # Limpiar mediciones previas
            osciloscopio.write(':MEASure:CLEar ALL')
            time.sleep(0.5)
            
            # Configurar medición para el Canal 1
            osciloscopio.write(':MEASure:SOURce1 CH1')
            osciloscopio.write(':MEASure:SOURce2 CH1')
            time.sleep(0.5)
            
            osciloscopio.write(':AUTOSet')  # Ajuste automático
            time.sleep(2)  # Esperar a que complete el autoajuste
            
            # Medir pico a pico
            osciloscopio.write(':MEASure:PK2PK ON')
            time.sleep(0.5)
            pk2pk_ch1_str = osciloscopio.query(':MEASure:PK2PK?').strip()
            
            try:
                pk2pk_ch1 = float(pk2pk_ch1_str)
            except ValueError:
                print(f"Error al convertir pk2pk_ch1: '{pk2pk_ch1_str}'")
                pk2pk_ch1 = 0
            
            # 4. Medir señal de salida (Canal 2)
            print("Midiendo señal de salida (CH2)...")
            # Limpiar mediciones previas
            osciloscopio.write(':MEASure:CLEar ALL')
            time.sleep(0.5)
            
            # Configurar medición para el Canal 2
            osciloscopio.write(':MEASure:SOURce1 CH2')
            osciloscopio.write(':MEASure:SOURce2 CH2')
            time.sleep(0.5)
            
            # Medir pico a pico
            osciloscopio.write(':MEASure:PK2PK ON')
            time.sleep(0.5)
            pk2pk_ch2_str = osciloscopio.query(':MEASure:PK2PK?').strip()
            
            try:
                pk2pk_ch2 = float(pk2pk_ch2_str)
            except ValueError:
                print(f"Error al convertir pk2pk_ch2: '{pk2pk_ch2_str}'")
                pk2pk_ch2 = 0
            
            # 5. Calcular ganancia
            if pk2pk_ch1 > 0:
                ganancia = pk2pk_ch2 / pk2pk_ch1
                ganancia_db = 20 * np.log10(ganancia)  # Convertir a dB
            else:
                ganancia = 0
                ganancia_db = float('-inf')
            
            # Mostrar resultados de esta frecuencia
            print(f"Resultados a {frecuencia_redondeada} Hz:")
            print(f"- Entrada (CH1): {pk2pk_ch1:.6f} Vpp")
            print(f"- Salida (CH2): {pk2pk_ch2:.6f} Vpp")
            print(f"- Ganancia: {ganancia:.6f}")
            print(f"- Ganancia (dB): {ganancia_db:.2f} dB")
            
            # Guardar resultados
            resultados.append({
                "frecuencia": frecuencia_redondeada,
                "entrada_vpp": pk2pk_ch1,
                "salida_vpp": pk2pk_ch2,
                "ganancia": ganancia,
                "ganancia_db": ganancia_db
            })
            
            # Desactivar salida entre mediciones
            generador.write('OUTPut1 OFF')
            time.sleep(0.5)
        
        # Mostrar tabla de resultados
        print("\n=== RESULTADOS DEL BARRIDO DE FRECUENCIAS ===")
        print("Frecuencia (Hz) | Entrada (Vpp) | Salida (Vpp) | Ganancia | Ganancia (dB)")
        print("-" * 80)
        
        for r in resultados:
            print(f"{r['frecuencia']:<14.2f} | {r['entrada_vpp']:<13.6f} | {r['salida_vpp']:<12.6f} | {r['ganancia']:<8.6f} | {r['ganancia_db']:<12.2f}")
        
        # Generar diagrama de Bode
        print("\nGenerando diagrama de Bode...")
        
        # Extraer datos para el gráfico
        x_freq = [r['frecuencia'] for r in resultados]
        y_gain = [r['ganancia_db'] for r in resultados]
        
        # Crear figura
        plt.figure(figsize=(12, 8))
        plt.semilogx(x_freq, y_gain, 'o-', linewidth=2, markersize=8, color='blue')
        plt.grid(True, which="both", ls="-", alpha=0.7)
        
        # Configurar etiquetas y título
        plt.title("Diagrama de Bode - Respuesta en Frecuencia", fontsize=16)
        plt.xlabel("Frecuencia (Hz)", fontsize=14)
        plt.ylabel("Ganancia (dB)", fontsize=14)
        
        # Guardar diagrama
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resultados/diagrama_bode_{timestamp}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Diagrama de Bode guardado como: {filename}")
        
        # Guardar datos en CSV
        csv_filename = f"resultados/datos_bode_{timestamp}.csv"
        with open(csv_filename, 'w') as f:
            f.write("Frecuencia,Entrada_Vpp,Salida_Vpp,Ganancia,Ganancia_dB\n")
            for r in resultados:
                f.write(f"{r['frecuencia']},{r['entrada_vpp']},{r['salida_vpp']},{r['ganancia']},{r['ganancia_db']}\n")
        
        print(f"Datos guardados en CSV: {csv_filename}")
        
        # Mostrar el diagrama
        plt.show()
        
        # 6. FINALIZAR PRUEBA Y DESCONECTAR
        print("\nFinalizando barrido de frecuencias...")
        # Desactivar salida del generador
        generador.write('OUTPut1 OFF')
        
        # Cerrar conexiones
        generador.close()
        osciloscopio.close()
        print("Conexiones cerradas correctamente")
        print("=== BARRIDO DE FRECUENCIAS COMPLETADO ===")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print(f"Tipo de error: {type(e).__name__}")
        print("Verificar conexiones y direcciones IP")
        
        # Asegurar que las conexiones se cierren en caso de error
        try:
            generador.close()
            print("Conexión con generador cerrada")
        except:
            pass
        
        try:
            osciloscopio.close()
            print("Conexión con osciloscopio cerrada")
        except:
            pass

# Ejecutar el barrido de frecuencias
if __name__ == "__main__":
    barrido_frecuencias_automatizado()
