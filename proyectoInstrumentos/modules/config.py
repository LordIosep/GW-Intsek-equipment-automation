import os
import json
from datetime import datetime

# Directorio de datos
DATA_DIR = "data"

# Asegurar que el directorio de datos exista
def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

# Función para cargar perfiles de red
def cargar_perfiles_red():
    ensure_data_dir()
    archivo = os.path.join(DATA_DIR, "perfiles_red.json")
    
    if os.path.exists(archivo):
        try:
            with open(archivo, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar perfiles de red: {e}")
    
    # Perfil por defecto si no existe el archivo
    return {
        "perfiles": [
            {
                "nombre": "Perfil Predeterminado",
                "osciloscopio": {
                    "ip": "172.118.1.3",
                    "puerto": 3000
                },
                "generador": {
                    "ip": "172.118.1.246",
                    "puerto": 1026
                },
                "activo": True
            }
        ],
        "perfil_actual": "Perfil Predeterminado"
    }

# Función para guardar perfiles de red
def guardar_perfiles_red(perfiles):
    ensure_data_dir()
    archivo = os.path.join(DATA_DIR, "perfiles_red.json")
    
    try:
        with open(archivo, "w") as f:
            json.dump(perfiles, f, indent=4)
        return True
    except Exception as e:
        print(f"Error al guardar perfiles de red: {e}")
        return False

# Función para cargar lista de frecuencias

# Modificación para la función cargar_frecuencias() en config.py

def cargar_frecuencias():
    ensure_data_dir()
    archivo = os.path.join(DATA_DIR, "frecuencias.json")
    
    if os.path.exists(archivo):
        try:
            with open(archivo, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar frecuencias: {e}")
    
    # Generar frecuencias logarítmicas si no existe el archivo - cambiado a 30
    import numpy as np
    frecuencias = np.logspace(1, 6, 30).tolist()  # 30 frecuencias de 10Hz a 1MHz
    frecuencias = [round(f, 2) for f in frecuencias]
    
    # Guardar las frecuencias generadas
    try:
        with open(archivo, "w") as f:
            json.dump({"frecuencias": frecuencias}, f, indent=4)
    except Exception as e:
        print(f"Error al guardar frecuencias generadas: {e}")
    
    return {"frecuencias": frecuencias}

# Función para cargar datos de ganancia
def cargar_datos_ganancia():
    ensure_data_dir()
    archivo = os.path.join(DATA_DIR, "datos_ganancia.json")
    
    if os.path.exists(archivo):
        try:
            with open(archivo, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar datos de ganancia: {e}")
    
    # Estructura inicial si no existe el archivo
    return {
        "mediciones": [],
        "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# Función para guardar datos de ganancia
def guardar_datos_ganancia(datos_ganancia):
    ensure_data_dir()
    archivo = os.path.join(DATA_DIR, "datos_ganancia.json")
    
    # Actualizar fecha de última modificación
    datos_ganancia["ultima_actualizacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(archivo, "w") as f:
            json.dump(datos_ganancia, f, indent=4)
        return True
    except Exception as e:
        print(f"Error al guardar datos de ganancia: {e}")
        return False

# Función para agregar una nueva medición de ganancia
def agregar_medicion_ganancia(frecuencia, canal1_pk2pk, canal1_amplitud, 
                             canal2_pk2pk, canal2_amplitud, ganancia_pk2pk, 
                             ganancia_amplitud, ganancia_real):
    datos = cargar_datos_ganancia()
    
    # Verificar si ya existe una medición para esta frecuencia
    for i, medicion in enumerate(datos["mediciones"]):
        if medicion["frecuencia"] == frecuencia:
            # Actualizar medición existente
            datos["mediciones"][i] = {
                "frecuencia": frecuencia,
                "canal1_pk2pk": canal1_pk2pk,
                "canal1_amplitud": canal1_amplitud,
                "canal2_pk2pk": canal2_pk2pk,
                "canal2_amplitud": canal2_amplitud,
                "ganancia_pk2pk": ganancia_pk2pk,
                "ganancia_amplitud": ganancia_amplitud,
                "ganancia_real": ganancia_real,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return guardar_datos_ganancia(datos)
    
    # Agregar nueva medición
    datos["mediciones"].append({
        "frecuencia": frecuencia,
        "canal1_pk2pk": canal1_pk2pk,
        "canal1_amplitud": canal1_amplitud,
        "canal2_pk2pk": canal2_pk2pk,
        "canal2_amplitud": canal2_amplitud,
        "ganancia_pk2pk": ganancia_pk2pk,
        "ganancia_amplitud": ganancia_amplitud,
        "ganancia_real": ganancia_real,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    return guardar_datos_ganancia(datos)
