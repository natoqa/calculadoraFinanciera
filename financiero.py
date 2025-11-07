import pandas as pd
import numpy as np
import numpy_financial as npf

# --- Diccionario de Frecuencias ---
FRECUENCIAS = {
    "Mensual": 12,
    "Bimestral": 6,
    "Trimestral": 4,
    "Cuatrimestral": 3,
    "Semestral": 2,
    "Anual": 1
}

# --- Función de Conversión de Tasa ---
def convertir_tea_a_tep(tea, frecuencia_destino):
    """Convierte TEA a Tasa Efectiva Periódica (TEP)."""
    if tea < 0:
        raise ValueError("La TEA no puede ser negativa")
    n_periodos = FRECUENCIAS.get(frecuencia_destino)
    if not n_periodos:
        raise ValueError("Frecuencia no válida")
    tep = (1 + tea) ** (1 / n_periodos) - 1
    return tep

# ===================================================================
# Módulo A: Crecimiento de cartera
# ===================================================================
def calcular_crecimiento_cartera(monto_inicial, aporte_periodico, frecuencia_aporte, tasa_anual, plazo_anios):
    """Calcula el crecimiento de la cartera período a período."""
    # Validaciones
    if monto_inicial < 0 or aporte_periodico < 0:
        raise ValueError("Montos no pueden ser negativos")
    if tasa_anual < 0 or tasa_anual > 0.5:
        raise ValueError("TEA debe estar entre 0% y 50%")
    if plazo_anios < 1:
        raise ValueError("Plazo debe ser ≥ 1 año")

    n_periodos_por_anio = FRECUENCIAS[frecuencia_aporte]
    n_periodos_total = plazo_anios * n_periodos_por_anio
    tasa_periodica = convertir_tea_a_tep(tasa_anual, frecuencia_aporte)

    data = []
    saldo_inicial = monto_inicial
    total_aportado = 0

    for periodo in range(1, n_periodos_total + 1):
        aporte_actual = aporte_periodico if periodo > 1 else 0
        saldo_con_aporte = saldo_inicial + aporte_actual
        interes_ganado = saldo_inicial * tasa_periodica
        saldo_final = saldo_con_aporte + interes_ganado

        data.append({
            "Periodo": periodo,
            "Saldo Inicial": round(saldo_inicial,2),
            "Aporte": round(aporte_actual,2),
            "Interés Ganado": round(interes_ganado,2),
            "Saldo Final": round(saldo_final,2)
        })

        saldo_inicial = saldo_final
        total_aportado += aporte_actual

    df = pd.DataFrame(data)
    capital_final = df["Saldo Final"].iloc[-1]
    return df, capital_final, total_aportado + monto_inicial

# ===================================================================
# Módulo B: Jubilación
# ===================================================================
def calcular_impuestos(capital_final, total_aportado, tasa_impuesto):
    """Calcula impuesto sobre ganancia de capital."""
    ganancia = capital_final - total_aportado
    if ganancia <= 0:
        return 0.0, capital_final
    impuesto = ganancia * tasa_impuesto
    capital_neto = capital_final - impuesto
    return round(impuesto,2), round(capital_neto,2)

def calcular_pension_mensual(capital_neto, tasa_anual_retiro, anios_pension, factor=1.0):
    """Calcula pensión mensual usando TEA → TEM y opcional factor (%)."""
    if capital_neto <= 0:
        return 0.0
    tasa_mensual = convertir_tea_a_tep(tasa_anual_retiro, "Mensual")
    n_meses = anios_pension * 12
    if tasa_mensual == 0:
        return round(capital_neto * factor / n_meses,2)
    pension = npf.pmt(rate=tasa_mensual, nper=n_meses, pv=-capital_neto, fv=0)
    return round(pension * factor,2)

# Permite escenarios múltiples
def calcular_escenarios_jubilacion(capital_neto, tasas_retiro, edades_pension):
    """Devuelve DataFrame con pensión mensual para distintos escenarios."""
    resultados = []
    for tasa in tasas_retiro:
        for edad in edades_pension:
            anios_pension = edad
            pension = calcular_pension_mensual(capital_neto, tasa, anios_pension)
            resultados.append({
                "Tasa TEA Retiro (%)": tasa*100,
                "Años de Pensión": anios_pension,
                "Pensión Mensual (USD)": pension
            })
    return pd.DataFrame(resultados)

# ===================================================================
# Módulo C: Valoración de bonos
# ===================================================================
def calcular_pv_bono(valor_nominal, tasa_cupon_anual, frecuencia_pago, plazo_anios, tasa_retorno_anual):
    """Calcula PV de un bono con desglose por periodo."""
    if valor_nominal < 0 or tasa_cupon_anual < 0 or tasa_retorno_anual < 0:
        raise ValueError("Valores no pueden ser negativos")
    n_periodos_por_anio = FRECUENCIAS[frecuencia_pago]
    n_periodos_total = plazo_anios * n_periodos_por_anio
    tasa_cupon_periodica = tasa_cupon_anual / n_periodos_por_anio
    monto_cupon = valor_nominal * tasa_cupon_periodica
    tasa_retorno_periodica = convertir_tea_a_tep(tasa_retorno_anual, frecuencia_pago)

    flujos = [monto_cupon] * n_periodos_total
    flujos[-1] += valor_nominal
    data_flujos = []
    pv_total = 0

    for t in range(1, n_periodos_total + 1):
        flujo = flujos[t-1]
        pv_flujo = flujo / (1 + tasa_retorno_periodica)**t
        pv_total += pv_flujo
        data_flujos.append({
            "Periodo": t,
            "Flujo (Cupón)": round(flujo,2),
            "Flujo Descontado (PV)": round(pv_flujo,2)
        })

    df_flujos = pd.DataFrame(data_flujos)
    return round(pv_total,2), df_flujos
