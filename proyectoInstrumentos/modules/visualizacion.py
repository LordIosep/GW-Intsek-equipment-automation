import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from modules.config import cargar_datos_ganancia

def crear_dataframe_ganancias():
    """
    Crea un DataFrame con los datos de ganancia
    
    Returns:
        pandas.DataFrame: DataFrame con los datos de ganancia
    """
    datos = cargar_datos_ganancia()
    
    if not datos or "mediciones" not in datos or not datos["mediciones"]:
        return pd.DataFrame()
    
    # Convertir a DataFrame
    df = pd.DataFrame(datos["mediciones"])
    
    # Ordenar por frecuencia
    if "frecuencia" in df.columns:
        df = df.sort_values("frecuencia")
    
    return df

def mostrar_tabla_ganancias():
    """
    Muestra una tabla con los datos de ganancia
    """
    df = crear_dataframe_ganancias()
    
    if df.empty:
        st.warning("No hay datos de ganancia disponibles.")
        return
    
    # Formatear columnas numéricas para mostrar
    for col in ["frecuencia", "canal1_pk2pk", "canal1_amplitud", 
                "canal2_pk2pk", "canal2_amplitud", "ganancia_pk2pk", 
                "ganancia_amplitud", "ganancia_real"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"{x:.6f}" if isinstance(x, (int, float)) else x)
    
    # Mostrar la tabla
    st.dataframe(df)

def generar_grafico_bode():
    """
    Genera un gráfico de Bode (diagrama de ganancia)
    
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly con el gráfico
    """
    df = crear_dataframe_ganancias()
    
    if df.empty:
        return None
    
    # Calcular ganancia en dB si no existe
    if "ganancia_real_db" not in df.columns:
        import numpy as np
        df["ganancia_real_db"] = 20 * np.log10(df["ganancia_real"])
    
    # Crear figura de Plotly
    fig = go.Figure()
    
    # Agregar traza de ganancia (dB vs frecuencia)
    fig.add_trace(go.Scatter(
        x=df["frecuencia"],
        y=df["ganancia_real_db"],
        mode="lines+markers",
        name="Ganancia (dB)",
        line=dict(color="blue", width=2),
        marker=dict(size=8, color="blue")
    ))
    
    # Configurar diseño del gráfico
    fig.update_layout(
        title="Diagrama de Bode - Respuesta en Frecuencia",
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
    
    return fig
