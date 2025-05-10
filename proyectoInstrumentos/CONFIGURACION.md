# Guía de Configuración para la Automatización

Esta guía proporciona instrucciones detalladas sobre cómo configurar correctamente el sistema de automatización para mediciones con instrumentos GW Instek.

## Perfiles de Conexión

### Crear un Nuevo Perfil

1. Accede a la sección **Configuración** en el menú principal.
2. En la pestaña "Perfiles de Red", completa el formulario "Añadir Nuevo Perfil":
   - **Nombre**: Un nombre descriptivo para el perfil.
   - **IP Osciloscopio**: Dirección IP del osciloscopio (ej. 172.118.1.3).
   - **Puerto Osciloscopio**: Puerto de comunicación (típicamente 3000).
   - **IP Generador**: Dirección IP del generador de funciones (ej. 172.118.1.246).
   - **Puerto Generador**: Puerto de comunicación (típicamente 1026).
3. Activa la casilla "Activo" si deseas que este sea el perfil por defecto.
4. Haz clic en "Añadir".

### Probar la Conexión

Una vez creado el perfil, verifica que la conexión funciona correctamente:

1. Selecciona el perfil en la lista desplegable del sidebar.
2. En la sección "Probar Conexión", haz clic en "Probar Conexión con Osciloscopio" y "Probar Conexión con Generador".
3. Deberías recibir mensajes de confirmación con la identificación de los instrumentos.

### Errores Comunes de Conexión

- **Error de tiempo de espera**: Verifica que la dirección IP y el puerto sean correctos, y que el equipo esté encendido.
- **Error de conexión rechazada**: Puede indicar un firewall activo o que otro software está utilizando el instrumento.
- **Instrumento no responde**: Comprueba que el instrumento esté en modo remoto o que permita comunicación SCPI.

## Configuración de Frecuencias

### Generar Lista de Frecuencias

1. Accede a la pestaña "Configuración de Frecuencias" en la sección **Automatización**.
2. Selecciona el número de frecuencias que deseas medir (recomendado: 30).
3. Define el rango de frecuencias:
   - **Frecuencia mínima**: Típicamente 10 Hz.
   - **Frecuencia máxima**: Típicamente 1,000,000 Hz (1 MHz).
4. Selecciona el tipo de escala:
   - **Logarítmica**: Recomendada para diagramas de Bode (mayor detalle en bajas frecuencias).
   - **Lineal**: Distribución uniforme en todo el rango.
5. Haz clic en "Generar lista de frecuencias".

### Importar Frecuencias Personalizadas

Si tienes una lista específica de frecuencias:

1. Prepara un archivo CSV con una columna llamada "Frecuencia".
2. En la sección "Importar/Exportar Frecuencias", haz clic en "Examinar".
3. Selecciona tu archivo CSV y haz clic en el botón para importar.

## Configuración de Señal

Estos parámetros determinan cómo se generará la señal para cada medición:

### Parámetros Básicos

- **Amplitud**: Define la amplitud pico a pico de la señal (recomendado: 0.05 Vpp para circuitos sensibles, hasta 1 Vpp para circuitos robustos).
- **Offset**: Desplazamiento DC de la señal (típicamente 0 V).
- **Forma de onda**: Tipo de señal a generar:
  - **SINusoid**: Onda senoidal, ideal para respuesta en frecuencia.
  - **SQUare**: Onda cuadrada, útil para tiempo de subida/bajada.
  - **RAMP**: Rampa, útil para pruebas de linealidad.
  - **PULSe**: Pulso, útil para respuesta transitoria.
  - **NOISe**: Ruido, útil para pruebas de inmunidad.

### Tiempos de Espera

- **Tiempo de estabilización**: Tiempo de espera después de cambiar la frecuencia (0.5s por defecto).
  - Aumentar si las mediciones son inestables.
  - Reducir para mediciones más rápidas si el circuito responde rápidamente.
- **Tiempo entre mediciones**: Pausa entre frecuencias consecutivas (0.5s por defecto).
  - Puede reducirse para acelerar la secuencia completa.

## Ejecución de Mediciones

### Iniciar una Secuencia Completa

1. En la sección **Automatización**, verifica todos los parámetros.
2. Haz clic en "INICIAR SECUENCIA COMPLETA".
3. Observa la barra de progreso y el registro de actividad.
4. El proceso se completará automáticamente y guardará los resultados.

### Detener una Secuencia en Curso

1. Si necesitas detener el proceso, haz clic en "DETENER PROCESO".
2. El sistema detendrá de forma segura la ejecución después de completar la medición actual.
3. Todos los datos recogidos hasta ese momento se conservarán.

### Realizar una Medición Individual

Para probar un punto de frecuencia específico:

1. En la sección "Comandos Rápidos", haz clic en "Medir Una Frecuencia".
2. Introduce la frecuencia deseada.
3. Haz clic en "Ejecutar Medición".
4. Los resultados se mostrarán en pantalla pero no se guardarán automáticamente.

## Visualización de Resultados

### Diagramas de Bode

Los resultados se pueden visualizar en la sección **Gráficas**:

1. El diagrama principal muestra la ganancia real en dB vs. frecuencia.
2. Se pueden seleccionar diferentes tipos de ganancia:
   - **Ganancia Real**: Promedio de ganancia pico a pico y amplitud.
   - **Ganancia Pico a Pico**: Basada en la medición de valor pico a pico.
   - **Ganancia Amplitud**: Basada en la medición de amplitud.

### Exportación de Datos

Para análisis posterior:

1. Haz clic en "Exportar a CSV" o "Exportar a Excel".
2. Guarda el archivo generado en tu sistema.
3. Los datos incluyen todas las mediciones realizadas, incluyendo los valores en dB.

## Consejos para Mediciones Óptimas

1. **Conexión física**:
   - Usa cables de alta calidad y de longitud adecuada.
   - Conecta el canal 1 a la entrada del circuito bajo prueba.
   - Conecta el canal 2 a la salida del circuito bajo prueba.

2. **Ajuste de señal**:
   - Comienza con una amplitud baja (0.05 Vpp) y aumenta gradualmente si es necesario.
   - La señal no debe saturar el circuito bajo prueba ni el osciloscopio.

3. **Frecuencias de interés**:
   - Para filtros, usa más puntos alrededor de la frecuencia de corte.
   - Para amplificadores, enfócate en el ancho de banda operativo.
   - Para resonancia, concentra puntos cerca de la frecuencia de resonancia.

4. **Optimización de tiempos**:
   - Reduce los tiempos de espera para mediciones rápidas si la precisión no es crítica.
   - Aumenta los tiempos para circuitos con constantes de tiempo largas.

5. **Verificación manual**:
   - Antes de iniciar una secuencia completa, prueba con una sola frecuencia.
   - Verifica visualmente la señal en el osciloscopio para confirmar niveles adecuados.

---

Esta guía proporciona información básica para configurar el sistema de automatización. Para casos específicos o configuraciones avanzadas, consulta la documentación de los instrumentos o ajusta los parámetros según las necesidades de tu circuito.
