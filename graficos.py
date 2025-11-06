import plotly.graph_objects as go
import pandas as pd

def generar_grafico_crecimiento(df: pd.DataFrame):
    """Genera un gráfico de líneas y áreas apiladas con Plotly."""
    
    fig = go.Figure()

    # Calcular Aporte Acumulado
    df['Aporte Acumulado'] = df['Aporte'].cumsum() + df['Saldo Inicial'].iloc[0]

    # Área 1: Capital Inicial + Aportes
    fig.add_trace(go.Scatter(
        x=df['Periodo'],
        y=df['Aporte Acumulado'],
        mode='lines',
        fill='tozeroy',
        name='Total Aportado',
        line=dict(color='blue')
    ))
    
    # Área 2: Intereses (encima de los aportes)
    fig.add_trace(go.Scatter(
        x=df['Periodo'],
        y=df['Saldo Final'], # El saldo final ya incluye los intereses
        mode='lines',
        fill='tonexty', # Rellena hasta la traza anterior
        name='Interés Ganado',
        line=dict(color='green')
    ))

    fig.update_layout(
        title="Crecimiento de la Cartera en el Tiempo",
        xaxis_title="Período",
        yaxis_title="Monto (USD)",
        hovermode="x unified"
    )
    return fig