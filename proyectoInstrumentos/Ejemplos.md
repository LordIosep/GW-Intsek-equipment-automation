# Ejemplos de Uso del Sistema de Automatización

Este documento proporciona ejemplos prácticos para diferentes escenarios de uso del sistema de control de instrumentos GW Instek.

## Ejemplo 1: Caracterización de un Filtro Paso Bajo

### Objetivo
Determinar la frecuencia de corte y pendiente de atenuación de un filtro paso bajo.

### Configuración

1. **Conexiones**:
   - Conectar el generador a la entrada del filtro.
   - Conectar el canal 1 del osciloscopio a la entrada del filtro.
   - Conectar el canal 2 del osciloscopio a la salida del filtro.

2. **Parámetros**:
   - **Frecuencias**: 30 puntos, de 10 Hz a 100 kHz, escala logarítmica.
   - **Señal**: Senoidal, 0.1 Vpp, 0V offset.
   - **Tiempo de estabilización**: 0.5s

3. **Procedimiento**:
   - Navegar a la sección "Automatización".
   - Configurar los parámetros indicados.
   - Hacer clic en "INICIAR SECUENCIA COMPLETA".
   - Esperar a que se complete la secuencia.

4. **Análisis**:
   - Navegar a la sección "Gráficas".
   - Observar el diagrama de Bode.
   - La frecuencia de corte (-3dB) se puede identificar en el gráfico.
   - La pendiente de atenuación se puede calcular observando la caída en dB por década.

### Resultados Esperados
- Ganancia plana (0 dB) en frecuencias bajas.
- Caída de 3 dB en la frecuencia de corte.
- Pendiente de -20 dB/década para un filtro de primer orden o -40 dB/década para un filtro de segundo orden.

## Ejemplo 2: Respuesta en Frecuencia de un Amplificador

### Objetivo
Determinar el ancho de banda y ganancia de un amplificador operacional.

### Configuración

1. **Conexiones**:
   - Conectar el generador a la entrada del amplificador.
   - Conectar el canal 1 del osciloscopio a la entrada del amplificador.
   - Conectar el canal 2 del osciloscopio a la salida del amplificador.

2. **Parámetros**:
   - **Frecuencias**: 50 puntos, de 10 Hz a 1 MHz, escala logarítmica.
   - **Señal**: Senoidal, 0.05 Vpp, 0V offset.
   - **Tiempo de estabilización**: 0.5s

3. **Procedimiento**:
   - Navegar a la sección "Automatización".
   - Configurar los parámetros indicados.
   - Hacer clic en "INICIAR SECUENCIA COMPLETA".
   - Esperar a que se complete la secuencia.

4. **Análisis**:
   - Navegar a la sección "Gráficas".
   - Observar el diagrama de Bode.
   - Determinar la ganancia en la zona plana.
   - Identificar las frecuencias de corte inferior y superior (-3dB respecto a la ganancia máxima).
   - Calcular el ancho de banda (frecuencia superior - frecuencia inferior).

### Resultados Esperados
- Ganancia constante en la banda media.
- Caída de ganancia en frecuencias altas (limitación por producto ganancia-ancho de banda).
- Posible caída de ganancia en frecuencias muy bajas si hay capacitores de acoplamiento.

## Ejemplo 3: Análisis de un Filtro Paso Banda

### Objetivo
Caracterizar un filtro paso banda, identificando su frecuencia central, factor de calidad y ancho de banda.

### Configuración

1. **Conexiones**:
   - Conectar el generador a la entrada del filtro.
   - Conectar el canal 1 del osciloscopio a la entrada del filtro.
   - Conectar el canal 2 del osciloscopio a la salida del filtro.

2. **Parámetros**:
   - **Frecuencias**: 100 puntos, rango adaptado según el filtro (por ejemplo, 100 Hz a 10 kHz), escala logarítmica.
   - **Señal**: Senoidal, 0.1 Vpp, 0V offset.
   - **Tiempo de estabilización**: 0.8s (mayor para mejor precisión en la resonancia).

3. **Procedimiento**:
   - Primero realizar una medición rápida con pocos puntos para identificar aproximadamente la zona de resonancia.
   - Ajustar el rango de frecuencias para centrarse en esa zona.
   - Aumentar el número de puntos y realizar la secuencia completa.

4. **Análisis**:
   - Identificar la frecuencia de resonancia (ganancia máxima).
   - Determinar las frecuencias de corte inferior y superior (-3dB respecto al máximo).
   - Calcular el ancho de banda (BW = f_superior - f_inferior).
   - Calcular el factor de calidad (Q = f_resonancia / BW).

### Resultados Esperados
- Pico de ganancia en la frecuencia de resonancia.
- Caída de ganancia a ambos lados de la resonancia.
- Ancho de banda y factor Q que correspondan con el diseño del filtro.

## Ejemplo 4: Medición de Impedancia Relativa

### Objetivo
Estimar la impedancia relativa de un circuito en función de la frecuencia utilizando un divisor de tensión.

### Configuración

1. **Conexiones**:
   - Crear un divisor de tensión con una resistencia conocida (R) y el componente a medir (Z).
   - Conectar el generador a la entrada del divisor.
   - Conectar el canal 1 del osciloscopio a la entrada del divisor.
   - Conectar el canal 2 del osciloscopio a la salida del divisor (punto entre R y Z).

2. **Parámetros**:
   - **Frecuencias**: 50 puntos, de 10 Hz a 1 MHz, escala logarítmica.
   - **Señal**: Senoidal, 0.5 Vpp, 0V offset.
   - **Tiempo de estabilización**: 0.5s

3. **Procedimiento**:
   - Realizar la secuencia completa de mediciones.
   - Exportar los datos a CSV.
   - En una hoja de cálculo, calcular la impedancia Z a partir de la ganancia medida:
     - Para un divisor donde Z está conectado a tierra: Z = R * (Vin/Vout - 1)^-1
     - Para un divisor donde Z está conectado a la fuente: Z = R * (Vin/Vout - 1)

4. **Análisis**:
   - Graficar la impedancia vs. frecuencia.
   - Identificar cambios significativos que indiquen resonancias o comportamientos reactivos.

### Resultados Esperados
- Para componentes resistivos: impedancia constante en todas las frecuencias.
- Para capacitores: impedancia que disminuye con la frecuencia (Z = 1/(2πfC)).
- Para inductores: impedancia que aumenta con la frecuencia (Z = 2πfL).
- Para circuitos resonantes: picos o valles de impedancia en las frecuencias de resonancia.

## Ejemplo 5: Caracterización de un Transformador

### Objetivo
Medir la respuesta en frecuencia y relación de transformación de un transformador.

### Configuración

1. **Conexiones**:
   - Conectar el generador al primario del transformador.
   - Conectar el canal 1 del osciloscopio al primario del transformador.
   - Conectar el canal 2 del osciloscopio al secundario del transformador.
   - Colocar una resistencia de carga adecuada en el secundario.

2. **Parámetros**:
   - **Frecuencias**: 40 puntos, de 10 Hz a 500 kHz, escala logarítmica.
   - **Señal**: Senoidal, 0.2 Vpp, 0V offset.
   - **Tiempo de estabilización**: 0.7s

3. **Procedimiento**:
   - Realizar la secuencia completa de mediciones.
   - Observar los resultados de ganancia (que en este caso representarán la relación de transformación).

4. **Análisis**:
   - La relación de transformación es aproximadamente igual a la ganancia en la zona plana del diagrama de Bode.
   - Identificar la frecuencia mínima útil (donde comienza a caer la ganancia en bajas frecuencias).
   - Identificar la frecuencia máxima útil (donde comienza a caer la ganancia en altas frecuencias).

### Resultados Esperados
- Ganancia constante (igual a la relación de transformación) en la banda media.
- Caída de ganancia en frecuencias muy bajas (limitación por inductancia del primario).
- Caída de ganancia en frecuencias altas (limitación por capacitancias parásitas).

## Consideraciones Adicionales

### Optimización de Tiempo
Si necesitas realizar muchas mediciones y el tiempo es crítico:

1. Reduce el número de frecuencias (20-30 puntos suele ser suficiente para muchas aplicaciones).
2. Ajusta los tiempos de espera al mínimo funcional (prueba con 0.2s).
3. Concentra los puntos de medición en las zonas de interés (por ejemplo, alrededor de frecuencias de corte o resonancia).

### Alta Precisión
Para mediciones que requieren máxima precisión:

1. Aumenta el número de frecuencias (50-100 puntos).
2. Incrementa los tiempos de espera (0.8-1.0s).
3. Realiza varias mediciones y promedia los resultados.
4. Usa la forma de onda senoidal, que ofrece la mejor precisión.
5. Ajusta la amplitud para maximizar la relación señal/ruido sin saturar.

### Mediciones Diferenciales
Para medir ganancias de circuitos con entradas diferenciales:

1. Utiliza un divisor resistivo para crear dos señales desfasadas 180 grados.
2. Alternativamente, utiliza el canal 2 del generador si está disponible.
3. Mide ambas señales de entrada con un osciloscopio de 4 canales si es posible.
4. Calcula la ganancia considerando la entrada diferencial.

---

Estos ejemplos proporcionan un punto de partida para diversas aplicaciones. El sistema es flexible y puede adaptarse a muchos otros escenarios de medición.
