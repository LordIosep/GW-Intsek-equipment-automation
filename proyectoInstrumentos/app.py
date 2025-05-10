# Archivo app.py - Versión mejorada con sidebar y nueva configuración de frecuencias

import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
import json
import os
from datetime import datetime
import threading
import queue
import signal  # Para manejo de señales para detener procesos

# Importar módulos propios
from modules.config import (
    cargar_perfiles_red, guardar_perfiles_red, 
    cargar_frecuencias, cargar_datos_ganancia
)
from modules.equipos import Osciloscopio, GeneradorFunciones
from modules.automatizacion import ejecutar_medicion_automatica, ejecutar_secuencia_completa
from modules.visualizacion import mostrar_tabla_ganancias, generar_grafico_bode

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Control de Instrumentos GW Instek",
    page_icon="🔌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Crear directorio de datos si no existe
os.makedirs("data", exist_ok=True)
# Archivo para comunicación entre hilos
LOG_FILE = os.path.join("data", "progress_log.txt")
PROGRESS_FILE = os.path.join("data", "progress_status.json")
CONTROL_FILE = os.path.join("data", "process_control.json")  # Archivo para control de procesos

# Inicializar archivo de progreso si no existe
if not os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({
            "estado": "Detenido", 
            "progreso": 0, 
            "total": 1
        }, f)

# Inicializar archivo de control si no existe
if not os.path.exists(CONTROL_FILE):
    with open(CONTROL_FILE, "w") as f:
        json.dump({
            "ejecutando": False,
            "detener": False,
            "ultimo_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, f)

# Inicializar archivo de log si no existe
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("")

# Inicializar estado de sesión de manera segura
if 'menu_actual' not in st.session_state:
    st.session_state['menu_actual'] = "Automatizacion"

if 'auto_refresh' not in st.session_state:
    st.session_state['auto_refresh'] = True

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = None

# Función para leer el estado del progreso
def leer_estado_progreso():
    try:
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error al leer estado de progreso: {e}")
        return {"estado": "Detenido", "progreso": 0, "total": 1}

# Función para guardar el estado del progreso
def guardar_estado_progreso(estado, progreso=0, total=1):
    try:
        with open(PROGRESS_FILE, "w") as f:
            json.dump({
                "estado": estado,
                "progreso": progreso,
                "total": total,
                "timestamp": datetime.now().timestamp()  # Añadir timestamp para control
            }, f)
        return True
    except Exception as e:
        print(f"Error al guardar estado de progreso: {e}")
        return False

# Función para agregar mensajes al log
def agregar_log(mensaje):
    try:
        tiempo = datetime.now().strftime("%H:%M:%S")
        with open(LOG_FILE, "a") as f:
            f.write(f"[{tiempo}] {mensaje}\n")
        
        # Actualizar timestamp en archivo de control para trigger refresco
        actualizar_control(None, None)
        return True
    except Exception as e:
        print(f"Error al escribir en el log: {e}")
        return False

# Función para leer los mensajes del log
def leer_log(max_lines=100):
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()
            return lines[-max_lines:] if len(lines) > max_lines else lines
        return []
    except Exception as e:
        print(f"Error al leer el log: {e}")
        return []

# Función para limpiar el log
def limpiar_log():
    try:
        with open(LOG_FILE, "w") as f:
            f.write("")
        return True
    except Exception as e:
        print(f"Error al limpiar el log: {e}")
        return False

# Leer estado de control de proceso
def leer_control():
    try:
        with open(CONTROL_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error al leer control: {e}")
        return {"ejecutando": False, "detener": False, "ultimo_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

# Actualizar estado de control de proceso
def actualizar_control(ejecutando=None, detener=None):
    control = leer_control()
    
    if ejecutando is not None:
        control["ejecutando"] = ejecutando
    
    if detener is not None:
        control["detener"] = detener
    
    # Siempre actualizar timestamp
    control["ultimo_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(CONTROL_FILE, "w") as f:
            json.dump(control, f)
        return True
    except Exception as e:
        print(f"Error al actualizar control: {e}")
        return False

# Función para cambiar el menú actual
def cambiar_menu(nuevo_menu):
    st.session_state['menu_actual'] = nuevo_menu

# Función para verificar si debemos detener la ejecución
def debe_detenerse():
    control = leer_control()
    return control["detener"]

# Cargar perfiles
perfiles = cargar_perfiles_red()

# Sidebar para navegación y configuración rápida - MEJORADO
with st.sidebar:
    st.title("Control de Instrumentos")
    
    # Logo o imagen (usar placeholder)
    st.image("./asset/imagenes/logo_gw-instek.png", use_container_width=True)
    
    # Categorías con mejor estructura
    st.markdown("#### Módulos")
    
    # Botones de navegación con iconos
    if st.button("🔄 Automatización", key="btn_auto", use_container_width=True, 
                help="Ejecutar secuencia automática de mediciones"):
        cambiar_menu("Automatizacion")
        
    if st.button("📊 Gráficas", key="btn_graficas", use_container_width=True,
                help="Ver gráficos de resultados"):
        cambiar_menu("Graficas")
        
    if st.button("🎛️ Control Manual", key="btn_manual", use_container_width=True,
                help="Control manual de instrumentos"):
        cambiar_menu("Manual")
        
    if st.button("⚙️ Configuración", key="btn_config", use_container_width=True,
                help="Configurar perfiles de conexión"):
        cambiar_menu("Configuracion")
    
    st.markdown("---")
    
    # Sección de instrumentos conectados
    st.markdown("#### Instrumentos Conectados")
    
    # Obtener la lista de perfiles
    nombres_perfiles = [p["nombre"] for p in perfiles["perfiles"]]
    
    # Índice del perfil actual
    perfil_index = nombres_perfiles.index(perfiles["perfil_actual"]) if perfiles["perfil_actual"] in nombres_perfiles else 0
    
    # Selector de perfil
    perfil_seleccionado = st.selectbox(
        "Seleccionar perfil:",
        nombres_perfiles,
        index=perfil_index
    )
    
    # Actualizar perfil actual si cambió
    if perfil_seleccionado != perfiles["perfil_actual"]:
        perfiles["perfil_actual"] = perfil_seleccionado
        guardar_perfiles_red(perfiles)
    
    # Mostrar detalles del perfil seleccionado de forma más compacta
    for perfil in perfiles["perfiles"]:
        if perfil["nombre"] == perfil_seleccionado:
            st.info(f"""
            📡 **Osciloscopio:** {perfil["osciloscopio"]["ip"]}:{perfil["osciloscopio"]["puerto"]}
            
            📡 **Generador:** {perfil["generador"]["ip"]}:{perfil["generador"]["puerto"]}
            """)
            break
    
    # Opción para activar/desactivar refresco automático
    auto_refresh = st.checkbox("Auto-refresco", value=st.session_state['auto_refresh'], 
                              help="Actualizar automáticamente logs y progreso")
    if auto_refresh != st.session_state['auto_refresh']:
        st.session_state['auto_refresh'] = auto_refresh
    
    # Ayuda en un expander al final
    with st.expander("📘 Comandos SCPI Comunes"):
        st.info("""
        **Osciloscopio:**
        - `*IDN?` - Identificación
        - `:AUTOSet` - Config. automática
        - `:CHANnel<X>:COUPling {AC|DC|GND}`
        - `:CHANnel<X>:DISPlay {ON|OFF}`
        - `:MEASure:SOURce1 {CH1|CH2}`
        - `:MEASure:PK2PK?` - Valor pico a pico
        
        **Generador:**
        - `*IDN?` - Identificación
        - `*RST` - Reset
        - `SOURce<X>:FUNCtion {SIN|SQU|RAMP}`
        - `SOURce<X>:FREQuency <valor>`
        - `SOURce<X>:AMPlitude <valor>`
        - `OUTPut<X> {ON|OFF}`
        """)

# Contenido principal según el menú seleccionado
if st.session_state['menu_actual'] == "Automatizacion":
    st.title("Automatización de Mediciones")
    
    tabs = st.tabs(["Secuencia Automática", "Resultados de Ganancia"])
    
    with tabs[0]:
        st.header("Control de Secuencia Automática")
        
        # Obtener perfil activo
        perfil_activo = None
        for perfil in perfiles["perfiles"]:
            if perfil["nombre"] == perfiles["perfil_actual"]:
                perfil_activo = perfil
                break
        
        if not perfil_activo:
            st.error("No hay un perfil activo seleccionado.")
        else:
            # Parámetros de configuración
            st.header("Parámetros de Configuración")

            # Dividir en pestañas para mejor organización
            config_tabs = st.tabs(["Configuración de Frecuencias", "Configuración de Señal", "Tiempos de Espera"])

            with config_tabs[0]:  # Pestaña de frecuencias
                # Slider para seleccionar número de frecuencias
                num_frecuencias = st.slider(
                    "Número de frecuencias a medir:",
                    min_value=10,
                    max_value=100,
                    value=30,  # Valor por defecto ahora es 30
                    step=5,
                    help="Seleccione cuántas frecuencias desea medir entre 10Hz y 1MHz"
                )
                
                # Selección de los límites de frecuencia
                col1, col2 = st.columns(2)
                with col1:
                    freq_min = st.number_input(
                        "Frecuencia mínima (Hz):",
                        min_value=1.0,
                        max_value=1000.0,
                        value=10.0,
                        format="%.1f",
                        help="Frecuencia mínima para el barrido"
                    )
                
                with col2:
                    freq_max = st.number_input(
                        "Frecuencia máxima (Hz):",
                        min_value=1000.0,
                        max_value=2000000.0,
                        value=1000000.0,
                        format="%.1f",
                        help="Frecuencia máxima para el barrido"
                    )
                
                # Tipo de escala (logarítmica o lineal)
                escala = st.radio(
                    "Tipo de escala:",
                    options=["Logarítmica", "Lineal"],
                    index=0,
                    horizontal=True,
                    help="Escala logarítmica distribuye mejor las frecuencias para análisis de Bode"
                )
                
                # Botón para generar las frecuencias
                if st.button("Generar lista de frecuencias", key="gen_freq_btn"):
                    import numpy as np
                    
                    try:
                        # Generar frecuencias según la escala seleccionada
                        if escala == "Logarítmica":
                            nuevas_frecuencias = np.logspace(
                                np.log10(freq_min),
                                np.log10(freq_max),
                                num_frecuencias
                            ).tolist()
                        else:  # Lineal
                            nuevas_frecuencias = np.linspace(
                                freq_min,
                                freq_max,
                                num_frecuencias
                            ).tolist()
                        
                        # Redondear a 2 decimales
                        nuevas_frecuencias = [round(f, 2) for f in nuevas_frecuencias]
                        
                        # Guardar en archivo
                        os.makedirs("data", exist_ok=True)
                        with open(os.path.join("data", "frecuencias.json"), "w") as f:
                            json.dump({"frecuencias": nuevas_frecuencias}, f, indent=4)
                        
                        st.success(f"Se generaron {num_frecuencias} frecuencias correctamente")
                        
                        # Mostrar las primeras y últimas frecuencias generadas
                        if len(nuevas_frecuencias) > 0:
                            if len(nuevas_frecuencias) <= 10:
                                st.write(f"Frecuencias generadas: {', '.join([str(f) for f in nuevas_frecuencias])}")
                            else:
                                primeras = ', '.join([str(f) for f in nuevas_frecuencias[:5]])
                                ultimas = ', '.join([str(f) for f in nuevas_frecuencias[-5:]])
                                st.write(f"Primeras frecuencias: {primeras}")
                                st.write(f"Últimas frecuencias: {ultimas}")
                    except Exception as e:
                        st.error(f"Error al generar frecuencias: {str(e)}")
                
                # Carga de las frecuencias actuales para mostrar info
                frecuencias_data = cargar_frecuencias()
                frecuencias = frecuencias_data.get("frecuencias", [])
                
                # Información sobre la configuración actual
                if frecuencias:
                    st.info(f"""
                    **Configuración actual:**
                    - Total de frecuencias: {len(frecuencias)}
                    - Rango: {min(frecuencias):.2f} Hz - {max(frecuencias):.2f} Hz
                    - Escala: {"Logarítmica" if max(frecuencias)/min(frecuencias) > len(frecuencias) else "Lineal"}
                    """)
                    
                    # Opción para ver todas las frecuencias
                    if st.checkbox("Ver lista completa de frecuencias"):
                        # Mostrar tabla de frecuencias
                        df_frecuencias = pd.DataFrame({"Frecuencia (Hz)": frecuencias})
                        st.dataframe(df_frecuencias, height=200)

            with config_tabs[1]:  # Pestaña de configuración de señal
                # Amplitud de la señal
                amplitud = st.slider(
                    "Amplitud de la señal (Vpp):",
                    min_value=0.01,
                    max_value=1.0,
                    value=0.05,
                    step=0.01,
                    format="%.2f"
                )
                
                # Offset (opcional, si quieres añadirlo)
                offset = st.slider(
                    "Offset de la señal (V):",
                    min_value=-0.5,
                    max_value=0.5,
                    value=0.0,
                    step=0.01,
                    format="%.2f"
                )
                
                # Forma de onda (opcional, si quieres añadirlo)
                forma_onda = st.selectbox(
                    "Forma de onda:",
                    options=["SINusoid", "SQUare", "RAMP", "PULSe", "NOISe"],
                    index=0
                )

            with config_tabs[2]:  # Pestaña de tiempos de espera
                tiempo_estabilizacion = st.slider(
                    "Tiempo de estabilización (s):",
                    min_value=0.1,
                    max_value=2.0,
                    value=0.5,
                    step=0.1,
                    help="Tiempo de espera para estabilización de la señal"
                )
                
                tiempo_entre_mediciones = st.slider(
                    "Tiempo entre mediciones (s):",
                    min_value=0.1,
                    max_value=2.0,
                    value=0.5,
                    step=0.1,
                    help="Tiempo de espera entre mediciones consecutivas"
                )
            
            # Leer estado actual del proceso y control
            estado_progreso = leer_estado_progreso()
            control = leer_control()
            
            # Controles para iniciar/detener la secuencia
            col1, col2 = st.columns(2)
            
            # Botón de inicio
            with col1:
                start_button = st.button(
                    "INICIAR SECUENCIA COMPLETA",
                    type="primary",
                    use_container_width=True,
                    disabled=(estado_progreso["estado"] != "Detenido" or control["ejecutando"])
                )
            
            # Botón de detención
            with col2:
                stop_button = st.button(
                    "DETENER PROCESO",
                    type="secondary",
                    use_container_width=True,
                    disabled=(estado_progreso["estado"] == "Detenido" and not control["ejecutando"])
                )
            
            # Barra de progreso
            if estado_progreso["estado"] != "Detenido" and estado_progreso["total"] > 0:
                porcentaje = estado_progreso["progreso"] / estado_progreso["total"]
                progress_text = f"Progreso: {estado_progreso['progreso']}/{estado_progreso['total']} frecuencias ({int(porcentaje*100)}%)"
            else:
                porcentaje = 0
                progress_text = "Esperando inicio..."
            
            progress_bar = st.progress(porcentaje, text=progress_text)
            
            # Botón para refrescar manualmente
            refresco_col1, refresco_col2 = st.columns([1, 6])
            with refresco_col1:
                if st.button("🔄 Refrescar", key="refresh_btn") and not st.session_state['auto_refresh']:
                    pass  # La acción se realiza al hacer clic, no necesitamos código adicional
            
            with refresco_col2:
                if control["ejecutando"]:
                    st.info(f"Proceso en ejecución. Estado: {estado_progreso['estado']}")
                else:
                    if estado_progreso["estado"] == "Detenido":
                        st.info("No hay procesos en ejecución.")
                    else:
                        st.warning(f"Estado: {estado_progreso['estado']} - Puede haber un proceso incompleto.")
            
            # Área de log
            st.subheader("Log de Ejecución")
            log_container = st.container(height=300)
            
            with log_container:
                # Leer y mostrar los mensajes del log
                log_lines = leer_log()
                if log_lines:
                    st.code("".join(log_lines))
                else:
                    st.info("No hay mensajes en el log.")
            
            # Función modificada para actualizar la UI
            def actualizar_progreso(mensaje, progreso=None, total=None):
                agregar_log(mensaje)
                
                # Actualizar barra de progreso si es posible
                if progreso is not None and total is not None:
                    guardar_estado_progreso("Ejecutando", progreso, total)
                elif "frecuencia" in mensaje and "Iniciando medición" in mensaje:
                    try:
                        # Extraer el número de medición actual del formato "Iniciando medición X/Y"
                        partes = mensaje.split("Iniciando medición ")[1].split("/")
                        actual = int(partes[0])
                        total = int(partes[1].split(":")[0])
                        
                        # Actualizar progreso
                        guardar_estado_progreso("Ejecutando", actual, total)
                    except:
                        pass
            
            # Lógica para iniciar la secuencia
            if start_button:
                # Limpiar log
                limpiar_log()
                # Inicializar estado
                guardar_estado_progreso("Iniciando", 0, 1)
                # Configurar estado de control
                actualizar_control(True, False)
                
                # Mensaje inicial
                agregar_log("Iniciando secuencia automática...")
                
                # Ejecutar en un hilo separado para no bloquear la UI
                def ejecutar_en_segundo_plano():
                    try:
                        agregar_log("Iniciando proceso en segundo plano...")
                        
                        exito, error = ejecutar_secuencia_completa(
                            gen_ip=perfil_activo["generador"]["ip"],
                            gen_puerto=perfil_activo["generador"]["puerto"],
                            osc_ip=perfil_activo["osciloscopio"]["ip"],
                            osc_puerto=perfil_activo["osciloscopio"]["puerto"],
                            amplitud=amplitud,
                            offset=offset,  # Nuevo parámetro
                            forma_onda=forma_onda,  # Nuevo parámetro
                            tiempo_estabilizacion=tiempo_estabilizacion,
                            tiempo_entre_mediciones=tiempo_entre_mediciones,
                            progreso_callback=actualizar_progreso,
                            funcion_verificar_detencion=debe_detenerse
                        )
                        
                        if not exito and error:
                            agregar_log(f"Error en la secuencia: {error}")
                        
                        # Indicar que el proceso ha terminado
                        agregar_log("Proceso completado")
                        guardar_estado_progreso("Detenido")
                        actualizar_control(False, False)
                    except Exception as e:
                        # Capturar cualquier excepción
                        mensaje_error = f"Error inesperado: {str(e)}"
                        print(mensaje_error)  # Imprimir en consola para debug
                        
                        try:
                            agregar_log(mensaje_error)
                        except:
                            pass
                        
                        guardar_estado_progreso("Detenido")
                        actualizar_control(False, False)
                
                thread = threading.Thread(target=ejecutar_en_segundo_plano)
                thread.daemon = True
                thread.start()
                
                # Guardar ID del hilo
                st.session_state['thread_id'] = thread.ident
                
                # Recargar la página para iniciar el proceso
                time.sleep(0.1)
                st.rerun()
            
            # Detener proceso en curso
            if stop_button:
                actualizar_control(None, True)  # Indicar que debe detenerse
                guardar_estado_progreso("Deteniendo")
                agregar_log("Deteniendo proceso... Espere mientras se cierran las conexiones")
                time.sleep(1)  # Dar tiempo para detectar la señal de detención
                st.rerun()
            
            # Auto-refresco si está habilitado y hay un proceso en ejecución
            if st.session_state['auto_refresh'] and control["ejecutando"]:
                control_timestamp = datetime.strptime(control["ultimo_update"], "%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                
                # Si hubo una actualización en los últimos 2 segundos, refrescar
                if (now - control_timestamp).total_seconds() < 2:
                    time.sleep(0.5)  # Pequeña pausa para evitar recargas demasiado rápidas
                    st.rerun()
            
            # Botones rápidos para comandos simples
            st.markdown("---")
            st.subheader("Comandos Rápidos")
            
            # Crear 4 columnas para botones rápidos
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("AUTOSET Osciloscopio", use_container_width=True):
                    osciloscopio = Osciloscopio(
                        perfil_activo["osciloscopio"]["ip"],
                        perfil_activo["osciloscopio"]["puerto"]
                    )
                    
                    with st.spinner("Enviando comando AUTOSET..."):
                        conectado, error = osciloscopio.conectar()
                        if conectado:
                            osciloscopio.auto_setup()
                            time.sleep(1)  # Reducido de 2s a 1s
                            osciloscopio.desconectar()
                            st.success("AUTOSET completado")
                        else:
                            st.error(f"Error de conexión: {error}")
            
            with col2:
                if st.button("Activar Generador", use_container_width=True):
                    generador = GeneradorFunciones(
                        perfil_activo["generador"]["ip"],
                        perfil_activo["generador"]["puerto"]
                    )
                    
                    with st.spinner("Activando salida del generador..."):
                        conectado, error = generador.conectar()
                        if conectado:
                            generador.configuracion_completa(
                                canal=1, 
                                forma=forma_onda,  # Usar el parámetro seleccionado
                                frecuencia=1000,  # 1 kHz por defecto
                                amplitud=amplitud,
                                offset=offset  # Usar el parámetro seleccionado
                            )
                            generador.activar_salida(1)
                            st.success("Generador activado a 1 kHz")
                        else:
                            st.error(f"Error de conexión: {error}")
            
            with col3:
                if st.button("Desactivar Generador", use_container_width=True):
                    generador = GeneradorFunciones(
                        perfil_activo["generador"]["ip"],
                        perfil_activo["generador"]["puerto"]
                    )
                    
                    with st.spinner("Desactivando salida del generador..."):
                        conectado, error = generador.conectar()
                        if conectado:
                            generador.desactivar_salida(1)
                            generador.desconectar()
                            st.success("Generador desactivado")
                        else:
                            st.error(f"Error de conexión: {error}")
            
            with col4:
                if st.button("Medir Una Frecuencia", use_container_width=True):
                    # Obtener una frecuencia de prueba
                    frecuencia_prueba = st.number_input(
                        "Frecuencia a medir (Hz):",
                        min_value=10,
                        max_value=1000000,
                        value=1000,
                        step=100
                    )
                    
                    if st.button("Ejecutar Medición", type="primary"):
                        with st.spinner(f"Midiendo a {frecuencia_prueba} Hz..."):
                            # Limpiar log
                            limpiar_log()
                            
                            # Función para actualizar log
                            def actualizar_log(mensaje):
                                agregar_log(mensaje)
                            
                            # Ejecutar medición
                            resultado, error = ejecutar_medicion_automatica(
                                gen_ip=perfil_activo["generador"]["ip"],
                                gen_puerto=perfil_activo["generador"]["puerto"],
                                osc_ip=perfil_activo["osciloscopio"]["ip"],
                                osc_puerto=perfil_activo["osciloscopio"]["puerto"],
                                frecuencia=frecuencia_prueba,
                                amplitud=amplitud,
                                offset=offset,  # Nuevo parámetro
                                forma_onda=forma_onda,  # Nuevo parámetro
                                progreso_callback=actualizar_log,
                                tiempo_estabilizacion=tiempo_estabilizacion
                            )
                            
                            if error:
                                st.error(f"Error: {error}")
                            elif resultado:
                                st.success("Medición completada correctamente")
                                # Mostrar resultados
                                st.json(resultado)
    
    with tabs[1]:
        st.header("Resultados de Ganancia")
        
        # Mostrar tabla de resultados
        mostrar_tabla_ganancias()
        
        # Botones para exportar datos
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Exportar a CSV", use_container_width=True):
                # Crear DataFrame
                df = pd.DataFrame(cargar_datos_ganancia().get("mediciones", []))
                
                if not df.empty:
                    # Crear archivo CSV
                    csv = df.to_csv(index=False)
                    
                    # Botón de descarga
                    st.download_button(
                        label="Descargar CSV",
                        data=csv,
                        file_name=f"datos_ganancia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No hay datos para exportar.")
        
        with col2:
            if st.button("Exportar a Excel", use_container_width=True):
                # Crear DataFrame
                df = pd.DataFrame(cargar_datos_ganancia().get("mediciones", []))
                
                if not df.empty:
                    try:
                        # Crear archivo Excel
                        excel_file = f"datos_ganancia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                        df.to_excel(excel_file, index=False)
                        
                        # Leer el archivo para descarga
                        with open(excel_file, "rb") as f:
                            excel_data = f.read()
                        
                        # Botón de descarga
                        st.download_button(
                            label="Descargar Excel",
                            data=excel_data,
                            file_name=excel_file,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                        # Eliminar archivo temporal
                        os.remove(excel_file)
                    except Exception as e:
                        st.error(f"Error al crear archivo Excel: {str(e)}")
                else:
                    st.warning("No hay datos para exportar.")

elif st.session_state['menu_actual'] == "Manual":
    st.title("Control Manual de Instrumentos")
    
    tabs = st.tabs(["Osciloscopio", "Generador de Funciones"])
    
    # Obtener perfil activo
    perfil_activo = None
    for perfil in perfiles["perfiles"]:
        if perfil["nombre"] == perfiles["perfil_actual"]:
            perfil_activo = perfil
            break
    
    if not perfil_activo:
        st.error("No hay un perfil activo seleccionado.")
    else:
        with tabs[0]:
            st.header("Control Manual del Osciloscopio")
            
            st.write(f"""
            **Conexión actual:**
            - IP: {perfil_activo["osciloscopio"]["ip"]}
            - Puerto: {perfil_activo["osciloscopio"]["puerto"]}
            """)
            
            # Sección para comandos rápidos
            st.subheader("Comandos Rápidos")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("Identificar", key="osc_id", use_container_width=True):
                    osciloscopio = Osciloscopio(
                        perfil_activo["osciloscopio"]["ip"],
                        perfil_activo["osciloscopio"]["puerto"]
                    )
                    
                    with st.spinner("Conectando..."):
                        conectado, error = osciloscopio.conectar()
                        if conectado:
                            id_info, error = osciloscopio.identificar()
                            osciloscopio.desconectar()
                            
                            if error:
                                st.error(f"Error: {error}")
                            else:
                                st.success(f"Identificación: {id_info}")
                        else:
                            st.error(f"Error de conexión: {error}")
            
            with col2:
                if st.button("AUTOSET", key="osc_auto", use_container_width=True):
                    osciloscopio = Osciloscopio(
                        perfil_activo["osciloscopio"]["ip"],
                        perfil_activo["osciloscopio"]["puerto"]
                    )
                    
                    with st.spinner("Configurando..."):
                        conectado, error = osciloscopio.conectar()
                        if conectado:
                            osciloscopio.auto_setup()
                            time.sleep(1)  # Reducido a 1s
                            osciloscopio.desconectar()
                            st.success("AUTOSET completado")
                        else:
                            st.error(f"Error de conexión: {error}")
            
            with col3:
                if st.button("STOP", key="osc_stop", use_container_width=True):
                    osciloscopio = Osciloscopio(
                        perfil_activo["osciloscopio"]["ip"],
                        perfil_activo["osciloscopio"]["puerto"]
                    )
                    
                    with st.spinner("Deteniendo..."):
                        conectado, error = osciloscopio.conectar()
                        if conectado:
                            osciloscopio.detener()
                            osciloscopio.desconectar()
                            st.success("Adquisición detenida")
                        else:
                            st.error(f"Error de conexión: {error}")
            
            with col4:
                if st.button("RUN", key="osc_run", use_container_width=True):
                    osciloscopio = Osciloscopio(
                        perfil_activo["osciloscopio"]["ip"],
                        perfil_activo["osciloscopio"]["puerto"]
                    )
                    
                    with st.spinner("Iniciando..."):
                        conectado, error = osciloscopio.conectar()
                        if conectado:
                            osciloscopio.iniciar()
                            osciloscopio.desconectar()
                            st.success("Adquisición iniciada")
                        else:
                            st.error(f"Error de conexión: {error}")
            
            # Sección para configuración de canales
            st.subheader("Configuración de Canales")
            
            canal_tabs = st.tabs(["Canal 1", "Canal 2"])
            
            for i, canal_tab in enumerate(canal_tabs, 1):
                with canal_tab:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        acoplamiento = st.radio(
                            f"Acoplamiento CH{i}:",
                            options=["AC", "DC", "GND"],
                            key=f"ac_{i}"
                        )
                        
                        display = st.radio(
                            f"Visualización CH{i}:",
                            options=["ON", "OFF"],
                            key=f"disp_{i}"
                        )
                    
                    with col2:
                        posicion = st.slider(
                            f"Posición CH{i}:",
                            min_value=-10.0,
                            max_value=10.0,
                            value=0.0,
                            step=0.5,
                            key=f"pos_{i}"
                        )
                    
                    if st.button(f"Aplicar Configuración CH{i}", key=f"apply_{i}", use_container_width=True):
                        osciloscopio = Osciloscopio(
                            perfil_activo["osciloscopio"]["ip"],
                            perfil_activo["osciloscopio"]["puerto"]
                        )
                        
                        with st.spinner(f"Configurando CH{i}..."):
                            conectado, error = osciloscopio.conectar()
                            if conectado:
                                osciloscopio.configurar_canal(
                                    canal=i,
                                    acoplamiento=acoplamiento,
                                    display=display,
                                    posicion=posicion
                                )
                                osciloscopio.desconectar()
                                st.success(f"Configuración de CH{i} aplicada")
                            else:
                                st.error(f"Error de conexión: {error}")
            
            # Sección para mediciones
            st.subheader("Mediciones")
            
            col1, col2 = st.columns(2)
            
            with col1:
                canal_medicion = st.selectbox(
                    "Canal a medir:",
                    options=["CH1", "CH2"],
                    key="medir_canal"
                )
            
            with col2:
                tipo_medicion = st.selectbox(
                    "Tipo de medición:",
                    options=["PK2PK", "AMPLITUDE", "FREQUENCY", "RMS"],
                    key="medir_tipo"
                )
            
            if st.button("Realizar Medición", key="btn_medir", use_container_width=True):
                osciloscopio = Osciloscopio(
                    perfil_activo["osciloscopio"]["ip"],
                    perfil_activo["osciloscopio"]["puerto"]
                )
                
                with st.spinner("Realizando medición..."):
                    conectado, error = osciloscopio.conectar()
                    if conectado:
                        valor, error = osciloscopio.obtener_medicion(
                            canal=canal_medicion,
                            tipo_medicion=tipo_medicion
                        )
                        osciloscopio.desconectar()
                        
                        if error:
                            st.error(f"Error al medir: {error}")
                        else:
                            st.success(f"Resultado: {valor}")
                            
                            # Mostrar el resultado en una tabla
                            df = pd.DataFrame({
                                "Canal": [canal_medicion],
                                "Tipo": [tipo_medicion],
                                "Valor": [f"{valor:.6f}" if isinstance(valor, (int, float)) else valor]
                            })
                            st.table(df)
                    else:
                        st.error(f"Error de conexión: {error}")
            
            # Sección para comandos manuales
            st.subheader("Comandos SCPI Manuales")
            
            comando = st.text_input(
                "Comando SCPI:",
                value="*IDN?",
                key="cmd_osc"
            )
            
            tipo_comando = st.radio(
                "Tipo de comando:",
                options=["Query (espera respuesta)", "Comando (sin respuesta)"],
                key="tipo_cmd_osc"
            )
            
            if st.button("Enviar Comando", key="btn_cmd_osc", use_container_width=True):
                osciloscopio = Osciloscopio(
                    perfil_activo["osciloscopio"]["ip"],
                    perfil_activo["osciloscopio"]["puerto"]
                )
                
                with st.spinner(f"Enviando comando: {comando}"):
                    conectado, error = osciloscopio.conectar()
                    if conectado:
                        if tipo_comando == "Query (espera respuesta)":
                            respuesta, error = osciloscopio.enviar_query(comando)
                            osciloscopio.desconectar()
                            
                            if error:
                                st.error(f"Error: {error}")
                            else:
                                st.success("Comando enviado exitosamente")
                                st.code(respuesta)
                        else:
                            resultado, error = osciloscopio.enviar_comando(comando)
                            osciloscopio.desconectar()
                            
                            if error:
                                st.error(f"Error: {error}")
                            else:
                                st.success("Comando enviado exitosamente")
                    else:
                        st.error(f"Error de conexión: {error}")
        
        with tabs[1]:
            st.header("Control Manual del Generador de Funciones")
            
            st.write(f"""
            **Conexión actual:**
            - IP: {perfil_activo["generador"]["ip"]}
            - Puerto: {perfil_activo["generador"]["puerto"]}
            """)
            
            # Sección para comandos rápidos
            st.subheader("Comandos Rápidos")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("Identificar", key="gen_id", use_container_width=True):
                    generador = GeneradorFunciones(
                        perfil_activo["generador"]["ip"],
                        perfil_activo["generador"]["puerto"]
                    )
                    
                    with st.spinner("Conectando..."):
                        conectado, error = generador.conectar()
                        if conectado:
                            id_info, error = generador.identificar()
                            generador.desconectar()
                            
                            if error:
                                st.error(f"Error: {error}")
                            else:
                                st.success(f"Identificación: {id_info}")
                        else:
                            st.error(f"Error de conexión: {error}")
            
            with col2:
                if st.button("RESET", key="gen_reset", use_container_width=True):
                    generador = GeneradorFunciones(
                        perfil_activo["generador"]["ip"],
                        perfil_activo["generador"]["puerto"]
                    )
                    
                    with st.spinner("Reseteando..."):
                        conectado, error = generador.conectar()
                        if conectado:
                            generador.reset()
                            time.sleep(0.5)  # Reducido a 0.5s
                            generador.desconectar()
                            st.success("RESET completado")
                        else:
                            st.error(f"Error de conexión: {error}")
            
            with col3:
                if st.button("Activar Salida", key="gen_on", use_container_width=True):
                    generador = GeneradorFunciones(
                        perfil_activo["generador"]["ip"],
                        perfil_activo["generador"]["puerto"]
                    )
                    
                    with st.spinner("Activando salida..."):
                        conectado, error = generador.conectar()
                        if conectado:
                            generador.activar_salida(1)
                            generador.desconectar()
                            st.success("Salida activada")
                        else:
                            st.error(f"Error de conexión: {error}")
            
            with col4:
                if st.button("Desactivar Salida", key="gen_off", use_container_width=True):
                    generador = GeneradorFunciones(
                        perfil_activo["generador"]["ip"],
                        perfil_activo["generador"]["puerto"]
                    )
                    
                    with st.spinner("Desactivando salida..."):
                        conectado, error = generador.conectar()
                        if conectado:
                            generador.desactivar_salida(1)
                            generador.desconectar()
                            st.success("Salida desactivada")
                        else:
                            st.error(f"Error de conexión: {error}")
            
            # Sección para configuración de señal
            st.subheader("Configuración de Señal")
            
            # Formulario para configurar la señal
            with st.form(key="config_senal"):
                col1, col2 = st.columns(2)
                
                with col1:
                    forma_onda = st.selectbox(
                        "Forma de onda:",
                        options=["SINusoid", "SQUare", "RAMP", "PULSe", "NOISe"],
                        index=0,
                        key="forma_onda"
                    )
                    
                    frecuencia = st.number_input(
                        "Frecuencia (Hz):",
                        min_value=0.1,
                        max_value=25000000.0,
                        value=1000.0,
                        format="%.2f",
                        key="frecuencia"
                    )
                
                with col2:
                    amplitud = st.number_input(
                        "Amplitud (Vpp):",
                        min_value=0.01,
                        max_value=10.0,
                        value=0.05,
                        format="%.3f",
                        key="amplitud"
                    )
                    
                    offset = st.number_input(
                        "Offset (V):",
                        min_value=-5.0,
                        max_value=5.0,
                        value=0.0,
                        format="%.3f",
                        key="offset"
                    )
                
                canal = st.radio(
                    "Canal:",
                    options=["1", "2"],
                    index=0,
                    key="canal_gen"
                )
                
                submit_button = st.form_submit_button(
                    label="Aplicar Configuración",
                    use_container_width=True
                )
            
            if submit_button:
                generador = GeneradorFunciones(
                    perfil_activo["generador"]["ip"],
                    perfil_activo["generador"]["puerto"]
                )
                
                with st.spinner("Configurando señal..."):
                    conectado, error = generador.conectar()
                    if conectado:
                        config, error = generador.configuracion_completa(
                            canal=int(canal),
                            forma=forma_onda,
                            frecuencia=frecuencia,
                            amplitud=amplitud,
                            offset=offset
                        )
                        
                        if error:
                            st.error(f"Error al configurar: {error}")
                        else:
                            st.success("Configuración aplicada")
                            
                            # Mostrar configuración actual
                            st.json(config)
                        
                        generador.desconectar()
                    else:
                        st.error(f"Error de conexión: {error}")
            
            # Sección para comandos manuales
            st.subheader("Comandos SCPI Manuales")
            
            comando = st.text_input(
                "Comando SCPI:",
                value="*IDN?",
                key="cmd_gen"
            )
            
            tipo_comando = st.radio(
                "Tipo de comando:",
                options=["Query (espera respuesta)", "Comando (sin respuesta)"],
                key="tipo_cmd_gen"
            )
            
            if st.button("Enviar Comando", key="btn_cmd_gen", use_container_width=True):
                generador = GeneradorFunciones(
                    perfil_activo["generador"]["ip"],
                    perfil_activo["generador"]["puerto"]
                )
                
                with st.spinner(f"Enviando comando: {comando}"):
                    conectado, error = generador.conectar()
                    if conectado:
                        if tipo_comando == "Query (espera respuesta)":
                            respuesta, error = generador.enviar_query(comando)
                            generador.desconectar()
                            
                            if error:
                                st.error(f"Error: {error}")
                            else:
                                st.success("Comando enviado exitosamente")
                                st.code(respuesta)
                        else:
                            resultado, error = generador.enviar_comando(comando)
                            generador.desconectar()
                            
                            if error:
                                st.error(f"Error: {error}")
                            else:
                                st.success("Comando enviado exitosamente")
                    else:
                        st.error(f"Error de conexión: {error}")

elif st.session_state['menu_actual'] == "Graficas":
    st.title("Gráficas de Resultados")
    
    # Verificar si hay datos disponibles
    datos = cargar_datos_ganancia()
    if not "mediciones" in datos or not datos["mediciones"]:
        st.warning("No hay datos de mediciones disponibles para graficar.")
    else:
        try:
            # Crear DataFrame
            df = pd.DataFrame(datos["mediciones"])
            
            # Ordenar por frecuencia
            if "frecuencia" in df.columns:
                df = df.sort_values("frecuencia")
            
            # Calcular ganancia en dB si no existe
            if "ganancia_real_db" not in df.columns:
                import numpy as np
                df["ganancia_real_db"] = 20 * np.log10(
                    df["ganancia_real"].apply(lambda x: max(x, 1e-10))  # Evitar log(0)
                )
            
            # Crear gráfico de Bode
            st.subheader("Diagrama de Bode - Respuesta en Frecuencia")
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df["frecuencia"],
                y=df["ganancia_real_db"],
                mode="lines+markers",
                name="Ganancia (dB)",
                line=dict(color="blue", width=2),
                marker=dict(size=8, color="blue")
            ))
            
            fig.update_layout(
                xaxis_title="Frecuencia (Hz)",
                yaxis_title="Ganancia (dB)",
                xaxis_type="log",  # Escala logarítmica en X
                xaxis=dict(
                    showline=True,
                    showgrid=True,
                    gridwidth=1,
                    gridcolor="lightgray",
                    showticklabels=True,
                    ticks="outside"
                ),
                yaxis=dict(
                    showline=True,
                    showgrid=True,
                    gridwidth=1,
                    gridcolor="lightgray",
                    showticklabels=True,
                    ticks="outside"
                ),
                plot_bgcolor="white",
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Selector de visualización
            st.subheader("Opciones de Visualización")
            
            # Opción para mostrar diferentes tipos de ganancias
            tipo_ganancia = st.radio(
                "Tipo de ganancia a mostrar:",
                options=["Ganancia Real", "Ganancia Pico a Pico", "Ganancia Amplitud"],
                index=0,
                horizontal=True
            )
            
            # Crear nuevo gráfico según selección
            fig2 = go.Figure()
            
            if tipo_ganancia == "Ganancia Real":
                y_data = df["ganancia_real_db"]
                titulo = "Ganancia Real (dB)"
            elif tipo_ganancia == "Ganancia Pico a Pico":
                # Calcular en dB si no existe
                if "ganancia_pk2pk_db" not in df.columns:
                    import numpy as np
                    df["ganancia_pk2pk_db"] = 20 * np.log10(df["ganancia_pk2pk"].apply(
                        lambda x: max(x, 1e-10)  # Evitar log(0)
                    ))
                y_data = df["ganancia_pk2pk_db"]
                titulo = "Ganancia Pico a Pico (dB)"
            else:  # Ganancia Amplitud
                # Calcular en dB si no existe
                if "ganancia_amplitud_db" not in df.columns:
                    import numpy as np
                    df["ganancia_amplitud_db"] = 20 * np.log10(df["ganancia_amplitud"].apply(
                        lambda x: max(x, 1e-10)  # Evitar log(0)
                    ))
                y_data = df["ganancia_amplitud_db"]
                titulo = "Ganancia Amplitud (dB)"
            
            fig2.add_trace(go.Scatter(
                x=df["frecuencia"],
                y=y_data,
                mode="lines+markers",
                name=titulo,
                line=dict(color="green", width=2),
                marker=dict(size=8, color="green")
            ))
            
            fig2.update_layout(
                title=titulo,
                xaxis_title="Frecuencia (Hz)",
                yaxis_title="Ganancia (dB)",
                xaxis_type="log",  # Escala logarítmica en X
                xaxis=dict(
                    showline=True,
                    showgrid=True,
                    gridwidth=1,
                    gridcolor="lightgray",
                    showticklabels=True,
                    ticks="outside"
                ),
                yaxis=dict(
                    showline=True,
                    showgrid=True,
                    gridwidth=1,
                    gridcolor="lightgray",
                    showticklabels=True,
                    ticks="outside"
                ),
                plot_bgcolor="white"
            )
            
            st.plotly_chart(fig2, use_container_width=True)
            
            # Mostrar datos brutos
            with st.expander("Ver datos brutos"):
                st.dataframe(df)
        except Exception as e:
            st.error(f"Error al generar gráficos: {str(e)}")

elif st.session_state['menu_actual'] == "Configuracion":
    st.title("Configuración de Perfiles")
    
    tabs = st.tabs(["Perfiles de Red", "Configuración de Frecuencias"])
    
    with tabs[0]:
        st.header("Gestión de Perfiles de Conexión")
        
        # Mostrar perfiles existentes
        st.subheader("Perfiles Configurados")
        
        if perfiles["perfiles"]:
            # Crear DataFrame para mostrar los perfiles
            perfiles_df = pd.DataFrame([
                {
                    "Nombre": p["nombre"],
                    "Osciloscopio IP": p["osciloscopio"]["ip"],
                    "Osciloscopio Puerto": p["osciloscopio"]["puerto"],
                    "Generador IP": p["generador"]["ip"],
                    "Generador Puerto": p["generador"]["puerto"],
                    "Estado": "Activo" if p["activo"] else "Inactivo"
                } for p in perfiles["perfiles"]
            ])
            
            st.dataframe(perfiles_df, use_container_width=True)
            
            # Seleccionar perfil para editar
            perfil_names = [p["nombre"] for p in perfiles["perfiles"]]
            perfil_to_edit = st.selectbox(
                "Seleccionar perfil para editar:",
                perfil_names
            )
            
            # Encontrar el perfil seleccionado
            for i, p in enumerate(perfiles["perfiles"]):
                if p["nombre"] == perfil_to_edit:
                    # Formulario para editar
                    with st.form(key=f"edit_perfil_form_{i}"):
                        st.subheader(f"Editar: {p['nombre']}")
                        
                        nuevo_nombre = st.text_input("Nombre:", value=p["nombre"])
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Osciloscopio**")
                            osc_ip = st.text_input(
                                "IP Osciloscopio:",
                                value=p["osciloscopio"]["ip"]
                            )
                            osc_puerto = st.number_input(
                                "Puerto Osciloscopio:",
                                value=p["osciloscopio"]["puerto"],
                                min_value=1,
                                max_value=65535
                            )
                        
                        with col2:
                            st.markdown("**Generador de Funciones**")
                            gen_ip = st.text_input(
                                "IP Generador:",
                                value=p["generador"]["ip"]
                            )
                            gen_puerto = st.number_input(
                                "Puerto Generador:",
                                value=p["generador"]["puerto"],
                                min_value=1,
                                max_value=65535
                            )
                        
                        estado = st.checkbox("Activo", value=p["activo"])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            submit_button = st.form_submit_button(
                                label="Actualizar",
                                use_container_width=True
                            )
                        with col2:
                            delete_button = st.form_submit_button(
                                label="Eliminar",
                                use_container_width=True
                            )
                        
                        if submit_button:
                            perfiles["perfiles"][i] = {
                                "nombre": nuevo_nombre,
                                "osciloscopio": {
                                    "ip": osc_ip,
                                    "puerto": osc_puerto
                                },
                                "generador": {
                                    "ip": gen_ip,
                                    "puerto": gen_puerto
                                },
                                "activo": estado
                            }
                            
                            # Actualizar perfil actual si es necesario
                            if perfiles["perfil_actual"] == p["nombre"]:
                                perfiles["perfil_actual"] = nuevo_nombre
                            
                            if guardar_perfiles_red(perfiles):
                                st.success(f"Perfil {nuevo_nombre} actualizado correctamente")
                                # Recargar la página
                                st.rerun()
                            else:
                                st.error("Error al guardar los cambios")
                        
                        if delete_button:
                            # Verificar si es el único perfil
                            if len(perfiles["perfiles"]) <= 1:
                                st.error("No se puede eliminar el único perfil existente")
                            else:
                                perfiles["perfiles"].pop(i)
                                
                                # Actualizar perfil actual si es necesario
                                if perfiles["perfil_actual"] == p["nombre"]:
                                    perfiles["perfil_actual"] = perfiles["perfiles"][0]["nombre"]
                                
                                if guardar_perfiles_red(perfiles):
                                    st.success(f"Perfil {p['nombre']} eliminado correctamente")
                                    # Recargar la página
                                    st.rerun()
                                else:
                                    st.error("Error al guardar los cambios")
        
        # Formulario para añadir un nuevo perfil
        with st.form(key="new_perfil_form"):
            st.subheader("Añadir Nuevo Perfil")
            
            nuevo_nombre = st.text_input("Nombre:", value="Nuevo Perfil")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Osciloscopio**")
                osc_ip = st.text_input(
                    "IP Osciloscopio:",
                    value="172.118.1.3",
                    key="new_osc_ip"
                )
                osc_puerto = st.number_input(
                    "Puerto Osciloscopio:",
                    value=3000,
                    min_value=1,
                    max_value=65535,
                    key="new_osc_port"
                )
            
            with col2:
                st.markdown("**Generador de Funciones**")
                gen_ip = st.text_input(
                    "IP Generador:",
                    value="172.118.1.246",
                    key="new_gen_ip"
                )
                gen_puerto = st.number_input(
                    "Puerto Generador:",
                    value=1026,
                    min_value=1,
                    max_value=65535,
                    key="new_gen_port"
                )
            
            estado = st.checkbox("Activo", value=True, key="new_active")
            
            submit_button = st.form_submit_button(
                label="Añadir",
                use_container_width=True
            )
            
            if submit_button:
                # Verificar si ya existe un perfil con ese nombre
                nombres_existentes = [p["nombre"] for p in perfiles["perfiles"]]
                if nuevo_nombre in nombres_existentes:
                    st.error(f"Ya existe un perfil con el nombre {nuevo_nombre}")
                else:
                    perfiles["perfiles"].append({
                        "nombre": nuevo_nombre,
                        "osciloscopio": {
                            "ip": osc_ip,
                            "puerto": osc_puerto
                        },
                        "generador": {
                            "ip": gen_ip,
                            "puerto": gen_puerto
                        },
                        "activo": estado
                    })
                    
                    if guardar_perfiles_red(perfiles):
                        st.success(f"Perfil {nuevo_nombre} añadido correctamente")
                        # Recargar la página
                        st.rerun()
                    else:
                        st.error("Error al guardar los cambios")
        
        # Botón para probar conexión
        st.subheader("Probar Conexión")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Probar Conexión con Osciloscopio", use_container_width=True):
                # Obtener perfil actual
                perfil_actual = None
                for p in perfiles["perfiles"]:
                    if p["nombre"] == perfiles["perfil_actual"]:
                        perfil_actual = p
                        break
                
                if perfil_actual:
                    osciloscopio = Osciloscopio(
                        perfil_actual["osciloscopio"]["ip"],
                        perfil_actual["osciloscopio"]["puerto"]
                    )
                    
                    with st.spinner("Probando conexión..."):
                        conectado, error = osciloscopio.conectar()
                        if conectado:
                            id_info, _ = osciloscopio.identificar()
                            osciloscopio.desconectar()
                            st.success(f"Conexión exitosa: {id_info}")
                        else:
                            st.error(f"Error de conexión: {error}")
                else:
                    st.error("No hay un perfil activo seleccionado")
        
        with col2:
            if st.button("Probar Conexión con Generador", use_container_width=True):
                # Obtener perfil actual
                perfil_actual = None
                for p in perfiles["perfiles"]:
                    if p["nombre"] == perfiles["perfil_actual"]:
                        perfil_actual = p
                        break
                
                if perfil_actual:
                    generador = GeneradorFunciones(
                        perfil_actual["generador"]["ip"],
                        perfil_actual["generador"]["puerto"]
                    )
                    
                    with st.spinner("Probando conexión..."):
                        conectado, error = generador.conectar()
                        if conectado:
                            id_info, _ = generador.identificar()
                            generador.desconectar()
                            st.success(f"Conexión exitosa: {id_info}")
                        else:
                            st.error(f"Error de conexión: {error}")
                else:
                    st.error("No hay un perfil activo seleccionado")
    
    with tabs[1]:
        st.header("Configuración de Frecuencias")
        
        # Cargar frecuencias actuales
        frecuencias_data = cargar_frecuencias()
        frecuencias = frecuencias_data.get("frecuencias", [])
        
        # Mostrar frecuencias actuales
        st.subheader("Frecuencias Configuradas")
        
        if frecuencias:
            # Convertir a DataFrame para mejor visualización
            df_frecuencias = pd.DataFrame({"Frecuencia (Hz)": frecuencias})
            st.dataframe(df_frecuencias, use_container_width=True)
            
            # Información sobre la configuración
            st.info(f"""
            **Información de configuración:**
            - Total de frecuencias: {len(frecuencias)}
            - Rango: {min(frecuencias):.2f} Hz - {max(frecuencias):.2f} Hz
            - Escala: {"Logarítmica" if max(frecuencias)/min(frecuencias) > len(frecuencias) else "Lineal"}
            """)
        else:
            st.warning("No hay frecuencias configuradas.")
        
        # Opciones para regenerar frecuencias
        st.subheader("Generar Nuevas Frecuencias")
        
        with st.form(key="gen_freq_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                freq_min = st.number_input(
                    "Frecuencia mínima (Hz):",
                    min_value=1.0,
                    max_value=1000000.0,
                    value=10.0,
                    format="%.2f"
                )
            
            with col2:
                freq_max = st.number_input(
                    "Frecuencia máxima (Hz):",
                    min_value=10.0,
                    max_value=10000000.0,
                    value=1000000.0,
                    format="%.2f"
                )
            
            with col3:
                num_puntos = st.number_input(
                    "Número de puntos:",
                    min_value=10,
                    max_value=100,
                    value=30,  # Cambiado de 100 a 30
                    step=5
                )
            
            escala = st.radio(
                "Tipo de escala:",
                options=["Logarítmica", "Lineal"],
                index=0,
                horizontal=True
            )
            
            submit_button = st.form_submit_button(
                label="Generar Frecuencias",
                use_container_width=True
            )
            
            if submit_button:
                import numpy as np
                
                if freq_min >= freq_max:
                    st.error("La frecuencia mínima debe ser menor que la máxima")
                else:
                    try:
                        # Generar frecuencias según la escala seleccionada
                        if escala == "Logarítmica":
                            nuevas_frecuencias = np.logspace(
                                np.log10(freq_min),
                                np.log10(freq_max),
                                num_puntos
                            ).tolist()
                        else:  # Lineal
                            nuevas_frecuencias = np.linspace(
                                freq_min,
                                freq_max,
                                num_puntos
                            ).tolist()
                        
                        # Redondear a 2 decimales
                        nuevas_frecuencias = [round(f, 2) for f in nuevas_frecuencias]
                        
                        # Guardar en archivo
                        os.makedirs("data", exist_ok=True)  # Asegurar que exista el directorio
                        with open(os.path.join("data", "frecuencias.json"), "w") as f:
                            json.dump({"frecuencias": nuevas_frecuencias}, f, indent=4)
                        
                        st.success(f"Se generaron {num_puntos} frecuencias correctamente")
                        # Recargar página
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar frecuencias: {str(e)}")
        
        # Opción para importar/exportar frecuencias
        st.subheader("Importar/Exportar Frecuencias")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Exportar a CSV
            if st.button("Exportar a CSV", key="export_freq", use_container_width=True):
                if frecuencias:
                    # Crear CSV
                    df_export = pd.DataFrame({"Frecuencia": frecuencias})
                    csv = df_export.to_csv(index=False)
                    
                    # Botón de descarga
                    st.download_button(
                        label="Descargar CSV",
                        data=csv,
                        file_name="frecuencias.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No hay frecuencias para exportar")
        
        with col2:
            # Importar desde CSV
            uploaded_file = st.file_uploader("Importar desde CSV", type=["csv"])
            
            if uploaded_file is not None:
                try:
                    # Leer CSV
                    df_import = pd.read_csv(uploaded_file)
                    
                    # Verificar formato
                    if "Frecuencia" in df_import.columns:
                        frecuencias_importadas = df_import["Frecuencia"].tolist()
                        
                        # Guardar en archivo
                        os.makedirs("data", exist_ok=True)  # Asegurar que exista el directorio
                        with open(os.path.join("data", "frecuencias.json"), "w") as f:
                            json.dump({"frecuencias": frecuencias_importadas}, f, indent=4)
                        
                        st.success(f"Se importaron {len(frecuencias_importadas)} frecuencias correctamente")
                        # Recargar página
                        st.rerun()
                    else:
                        st.error("Formato de CSV incorrecto. Debe contener una columna 'Frecuencia'")
                except Exception as e:
                    st.error(f"Error al importar frecuencias: {str(e)}")

# Footer
st.markdown("---")
st.caption("Control de Instrumentos GW Instek - Desarrollado con Streamlit y PyVISA")
