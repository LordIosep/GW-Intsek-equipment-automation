# Manual de Instrucciones Básicas para Automatización de Equipos GW-Instek

## Requisitos Previos
- Python 3.7 o superior instalado
- Entorno virtual configurado con UV
- Bibliotecas PyVISA y PyVISA-py instaladas
- Equipos GW-Instek conectados a la red local

## Pasos para la Configuración Inicial

1. **Creación del entorno virtual**:
   ```
   pip install uv
   uv venv
   ```

2. **Activación del entorno virtual**:
   ```
   .\venv\Scripts\Activate.ps1
   ```

3. **Instalación de dependencias**:
   ```
   pip install pyvisa pyvisa-py numpy matplotlib streamlit matplotlib
   ```

4. **Verificación de la conexión de red**:
   - Asegúrese de que los equipos estén conectados a la misma red que su computadora
   - Verifique las direcciones IP de los instrumentos
   - Pruebe la conectividad usando ping

## Ejecución de los Scripts

1. **Verificación de Conexión**:
   ```
   python osciloscopio_conexion.py
   python generador_conexion.py
   ```

2. **Automatización Integrada**:
   ```
   python automatizacion_integrada.py
   ```

## Solución de Problemas Comunes

- **Error de conexión**: Verificar que las direcciones IP y puertos sean correctos
- **Tiempo de espera agotado**: Comprobar que los instrumentos estén encendidos y conectados a la red
- **Errores de comando**: Consultar el manual específico del modelo para verificar la sintaxis SCPI correcta
