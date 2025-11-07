import plotly.graph_objects as go
import pandas as pd

import plotly.express as px

def graficar_escenarios_barras(df_escenarios):
    """
    Genera un gráfico de barras agrupadas mostrando la pensión mensual
    según los años de pensión y la TEA de retiro.
    """
    fig = px.bar(
        df_escenarios,
        x="Años de Pensión",
        y="Pensión Mensual (USD)",
        color="Tasa TEA Retiro (%)",
        barmode="group",
        title="Comparación de Pensión Mensual según Escenarios",
        labels={"Pensión Mensual (USD)": "Pensión Mensual (USD)"}
    )
    fig.update_layout(
        legend_title_text="TEA Retiro (%)",
        yaxis_tickprefix="$",
        yaxis_tickformat=',.2f'
    )
    return fig


def graficar_escenarios_barras_agrupadas(df_escenarios):
    """
    Genera un gráfico de barras agrupadas mostrando la pensión mensual
    según los años de pensión y la TEA de retiro.
    Cada grupo de barras representa un año de pensión,
    y cada color representa una TEA distinta.
    """
    fig = go.Figure()

    # Crear una barra por cada TEA
    for tasa in df_escenarios["Tasa TEA Retiro (%)"].unique():
        datos = df_escenarios[df_escenarios["Tasa TEA Retiro (%)"] == tasa]
        fig.add_trace(go.Bar(
            x=datos["Años de Pensión"],
            y=datos["Pensión Mensual (USD)"],
            name=f"TEA {tasa}%",
        ))

    fig.update_layout(
        barmode='group',  # barras lado a lado (agrupadas)
        title="Comparación de Pensión Mensual según Años y TEA de Retiro",
        xaxis_title="Años de Pensión",
        yaxis_title="Pensión Mensual (USD)",
        yaxis_tickprefix="$",
        yaxis_tickformat=',.2f',
        legend_title_text="Tasa TEA Retiro (%)",
        template="plotly_white"
    )

    return fig

def graficar_escenarios_lineas(df_escenarios):
    """
    Genera un gráfico de líneas mostrando la pensión mensual
    según los años de pensión y la TEA de retiro.
    Cada TEA es una línea distinta.
    """
    fig = px.line(
        df_escenarios,
        x="Años de Pensión",
        y="Pensión Mensual (USD)",
        color="Tasa TEA Retiro (%)",
        markers=True,
        title="Pensión Mensual según Escenarios"
    )
    fig.update_layout(
        legend_title_text="TEA Retiro (%)",
        yaxis_tickprefix="$",
        yaxis_tickformat=',.2f'
    )
    return fig



def generar_grafico_crecimiento(df: pd.DataFrame):
    """Genera gráfico claro: aportes acumulados vs saldo final compuesto."""
    df['Aporte Acumulado'] = df['Aporte'].cumsum() + df['Saldo Inicial'].iloc[0]
    df['Aporte Acumulado'] = df['Aporte Acumulado'].round(2)

    fig = go.Figure()

    # Línea de aportes acumulados (recta ascendente)
    fig.add_trace(go.Scatter(
        x=df['Periodo'],
        y=df['Aporte Acumulado'],
        mode='lines+markers',
        name='Total Aportado',
        line=dict(color='blue', width=3)
    ))

    # Línea de saldo final (dinero compuesto)
    fig.add_trace(go.Scatter(
        x=df['Periodo'],
        y=df['Saldo Final'],
        mode='lines+markers',
        name='Saldo Final (con Interés)',
        line=dict(color='green', width=3)
    ))

    fig.update_layout(
        title="Crecimiento de la Cartera en el Tiempo",
        xaxis_title="Período",
        yaxis_title="Monto (USD)",
        hovermode="x unified",
        template="plotly_white"
    )
    return fig
