# Control de Instrumentos GW Instek - Documentación

Este documento describe el funcionamiento del sistema de control de instrumentos GW Instek, una aplicación basada en Streamlit para automatizar mediciones utilizando un osciloscopio y un generador de funciones.

## Estructura del Proyecto

```
proyectoInstrumentos/
├── app.py                      # Aplicación Streamlit principal
├── modules/                    # Módulos del sistema
│   ├── __init__.py             # Hace que el directorio sea un paquete
│   ├── config.py               # Funciones para cargar/guardar configuraciones
│   ├── equipos.py              # Clases para conexión con osciloscopio y generador
│   ├── automatizacion.py       # Lógica de automatización de mediciones
│   ├── visualizacion.py        # Funciones para gráficos y visualización
├── data/                       # Directorio para almacenar datos
│   ├── perfiles_red.json       # Configuración de IP/puerto
│   ├── frecuencias.json        # Lista de frecuencias a medir
│   ├── datos_ganancia.json     # Resultados de mediciones
│   ├── progress_log.txt        # Registro de actividad
│   ├── progress_status.json    # Estado actual del proceso
│   ├── process_control.json    # Control de ejecución de procesos
```

## Componentes Principales

### 1. Interfaz de Usuario (`app.py`)

La interfaz de usuario está desarrollada en Streamlit y ofrece las siguientes secciones:

- **Sidebar**: Navegación principal con acceso a los módulos y selección de perfil de conexión.
- **Automatización**: Permite configurar y ejecutar secuencias automáticas de mediciones.
  - Configuración de frecuencias (número, rango, distribución)
  - Configuración de señal (amplitud, offset, forma de onda)
  - Tiempos de espera personalizables
  - Visualización de progreso y logs
- **Control Manual**: Permite controlar manualmente el osciloscopio y el generador.
  - Comandos rápidos preconfigurados
  - Envío de comandos SCPI personalizados
  - Configuración de canales y mediciones
- **Gráficas**: Visualización de resultados de mediciones.
  - Diagrama de Bode (respuesta en frecuencia)
  - Opciones de visualización configurables
  - Exportación de datos
- **Configuración**: Gestión de perfiles de conexión y frecuencias.
  - Crear, editar y eliminar perfiles
  - Probar conexiones
  - Generar listas de frecuencias personalizadas

### 2. Módulo de Equipos (`equipos.py`)

Contiene las clases que gestionan la comunicación con los instrumentos mediante el protocolo SCPI:

- **Equipo**: Clase base con funcionalidad común.
  - Conexión mediante PyVISA
  - Envío de comandos y consultas
  - Gestión de errores
- **Osciloscopio**: Clase específica para el osciloscopio.
  - Configuración de canales
  - Mediciones automatizadas
  - Control de adquisición
- **GeneradorFunciones**: Clase específica para el generador.
  - Configuración de forma de onda
  - Control de frecuencia, amplitud y offset
  - Activación/desactivación de salidas

### 3. Módulo de Automatización (`automatizacion.py`)

Contiene la lógica para realizar mediciones automatizadas:

- **ejecutar_medicion_automatica**: Realiza una medición en una frecuencia específica.
  - Configura el generador
  - Configura el osciloscopio
  - Realiza las mediciones
  - Calcula ganancias
  - Guarda resultados
- **ejecutar_secuencia_completa**: Realiza una secuencia de mediciones en todas las frecuencias.
  - Control de progreso
  - Manejo de errores
  - Detención segura del proceso

### 4. Módulo de Configuración (`config.py`)

Gestiona la carga y guardado de configuraciones:

- **cargar_perfiles_red**: Carga los perfiles de conexión guardados.
- **guardar_perfiles_red**: Guarda los perfiles de conexión.
- **cargar_frecuencias**: Carga o genera las frecuencias de medición.
- **cargar_datos_ganancia**: Carga los resultados de mediciones previas.
- **agregar_medicion_ganancia**: Añade una nueva medición al historial.

### 5. Módulo de Visualización (`visualizacion.py`)

Proporciona funciones para mostrar y graficar resultados:

- **crear_dataframe_ganancias**: Convierte los datos de ganancia en un DataFrame.
- **mostrar_tabla_ganancias**: Muestra una tabla con los resultados.
- **generar_grafico_bode**: Crea un diagrama de Bode para visualizar la respuesta en frecuencia.

## Funcionamiento

### Flujo de Trabajo Típico

1. **Configuración Inicial**:
   - Seleccionar o crear un perfil de conexión con las direcciones IP y puertos correctos.
   - Configurar la lista de frecuencias que se utilizarán en la medición.
   - Configurar los parámetros de la señal (amplitud, offset, forma de onda).

2. **Ejecución de Mediciones Automáticas**:
   - Iniciar la secuencia completa desde la pestaña de Automatización.
   - El sistema realizará mediciones para cada frecuencia configurada.
   - Mostrará el progreso en tiempo real y registrará los resultados.
   - El proceso puede ser detenido en cualquier momento.

3. **Visualización de Resultados**:
   - Acceder a la pestaña de Gráficas para visualizar los resultados.
   - Generar diagramas de Bode con diferentes métricas.
   - Exportar datos a CSV o Excel para análisis adicional.

4. **Control Manual** (opcional):
   - Utilizar la pestaña de Control Manual para operaciones específicas.
   - Enviar comandos SCPI personalizados a los instrumentos.
   - Realizar mediciones individuales.

### Diagrama de Ejecución Automática

```
INICIO
  ├── Cargar configuración de frecuencias
  ├── Inicializar estado
  ├── Para cada frecuencia:
  │    ├── Conectar generador
  │    ├── Configurar generador (frecuencia, amplitud, offset, forma)
  │    ├── Activar salida del generador
  │    ├── Esperar estabilización
  │    ├── Conectar osciloscopio
  │    ├── Configurar osciloscopio
  │    ├── Medir canal 1 (entrada)
  │    ├── Medir canal 2 (salida)
  │    ├── Calcular ganancias
  │    ├── Guardar resultados
  │    ├── Desactivar salida del generador
  │    ├── Desconectar equipos
  │    └── Esperar tiempo entre mediciones
  └── Finalizar secuencia
FIN
```

## Características Avanzadas

### Configuración Flexible de Frecuencias

El sistema permite configurar el número exacto de frecuencias a medir (entre 10 y 100) y su distribución:

- **Distribución logarítmica**: Ideal para diagramas de Bode, distribuye las frecuencias para dar mayor detalle en las zonas de menor frecuencia.
- **Distribución lineal**: Distribución uniforme de frecuencias a lo largo del rango.

### Control de Procesos en Tiempo Real

- **Auto-refresco**: Actualización automática de la interfaz durante la ejecución.
- **Detención segura**: El proceso puede detenerse de forma segura en cualquier momento.
- **Registro detallado**: Registro detallado de todas las operaciones y errores.

### Optimización de Comunicación

- **Tiempos configurables**: Tiempos de espera personalizables para balancear velocidad y precisión.
- **Conexión eficiente**: Reutilización de recursos de conexión para mejorar la velocidad.
- **Manejo de errores**: Sistema robusto para manejar errores de comunicación.

## Tecnologías Utilizadas

- **Streamlit**: Framework para la interfaz de usuario.
- **PyVISA**: Biblioteca para comunicación con equipos mediante VISA.
- **Pandas**: Manipulación y análisis de datos.
- **Plotly**: Visualización interactiva de gráficos.
- **NumPy**: Operaciones numéricas para cálculos.

## Requerimientos del Sistema

- Python 3.8 o superior
- Streamlit 1.20.0 o superior
- PyVISA y PyVISA-py para comunicación con equipos
- Pandas, Plotly y NumPy para manipulación y visualización de datos
- Acceso a red para comunicarse con los equipos

## Ejecución

```
streamlit run app.py
```

## Solución de Problemas

### Problemas de Conexión
- Verificar que las direcciones IP y puertos sean correctos.
- Comprobar que los equipos estén encendidos y conectados a la red.
- Verificar que no haya otros programas utilizando los equipos.

### Errores de Medición
- Asegurarse de que las conexiones físicas entre instrumentos sean correctas.
- Verificar que la configuración de amplitud sea adecuada para el circuito bajo prueba.
- Comprobar que los tiempos de estabilización sean suficientes para la señal.

### Problemas de Interfaz
- Limpiar la caché del navegador si la interfaz no se actualiza correctamente.
- Reiniciar la aplicación si se producen errores persistentes.
- Verificar los archivos de registro para identificar posibles errores.

---

Este documento proporciona una visión general del sistema. Para detalles específicos sobre comandos SCPI y configuraciones avanzadas, consulte la documentación de los instrumentos GW Instek o los comentarios en el código fuente.
