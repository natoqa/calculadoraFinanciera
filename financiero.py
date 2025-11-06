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

# --- Función de Conversión de Tasa (Requerimiento 83) ---
def convertir_tea_a_tep(tea, frecuencia_destino):
    """Convierte Tasa Efectiva Anual (TEA) a Tasa Efectiva Periódica (TEP)"""
    n_periodos = FRECUENCIAS.get(frecuencia_destino)
    if not n_periodos:
        raise ValueError("Frecuencia no válida")
    
    tep = (1 + tea)**(1 / n_periodos) - 1
    return tep

# ===================================================================
# LÓGICA MÓDULO A
# ===================================================================
def calcular_crecimiento_cartera(monto_inicial, aporte_periodico, frecuencia_aporte, tasa_anual, plazo_anios):
    """Calcula el crecimiento de la cartera período a período."""
    
    n_periodos_por_anio = FRECUENCIAS.get(frecuencia_aporte)
    n_periodos_total = plazo_anios * n_periodos_por_anio
    
    # 1. Convertir la TEA a la tasa del período de aporte
    tasa_periodica = convertir_tea_a_tep(tasa_anual, frecuencia_aporte)
    
    # 2. Generar la tabla de crecimiento
    data = []
    saldo_inicial = monto_inicial
    total_aportado = 0
    
    for periodo in range(1, n_periodos_total + 1):
        # El primer período incluye el monto inicial
        aporte_actual = aporte_periodico if periodo > 0 or monto_inicial == 0 else 0
        
        # Corrección: si hay monto inicial, no se hace aporte en el periodo 0
        if periodo == 1:
            saldo_con_aporte = saldo_inicial + aporte_actual
            interes_ganado = saldo_con_aporte * tasa_periodica
        else:
            aporte_actual = aporte_periodico
            saldo_con_aporte = saldo_inicial + aporte_actual
            interes_ganado = saldo_con_aporte * tasa_periodica

        saldo_final = saldo_con_aporte + interes_ganado
        
        data.append({
            "Periodo": periodo,
            "Saldo Inicial": saldo_inicial,
            "Aporte": aporte_actual,
            "Interés Ganado": interes_ganado,
            "Saldo Final": saldo_final
        })
        
        saldo_inicial = saldo_final
        total_aportado += aporte_actual

    # 3. Usar npf.fv para verificar el cálculo final (opcional pero bueno)
    # fv_calculado = -npf.fv(rate=tasa_periodica, nper=n_periodos_total, pmt=aporte_periodico, pv=monto_inicial)
    
    df = pd.DataFrame(data)
    capital_final = df["Saldo Final"].iloc[-1]
    
    return df, capital_final, total_aportado

# ===================================================================
# LÓGICA MÓDULO B
# ===================================================================
def calcular_impuestos(capital_final, total_aportado, tasa_impuesto):
    """Calcula el impuesto sobre la ganancia de capital."""
    ganancia = capital_final - total_aportado
    if ganancia <= 0:
        return 0.0, capital_final # No hay impuestos si no hay ganancia
        
    impuesto = ganancia * tasa_impuesto
    capital_neto = capital_final - impuesto
    return impuesto, capital_neto

def calcular_pension_mensual(capital_neto, tasa_anual_retiro, anios_pension):
    """Calcula la pensión mensual usando la fórmula de anualidad."""
    
    # Convertir TEA a Tasa Efectiva Mensual (TEM)
    tasa_mensual = convertir_tea_a_tep(tasa_anual_retiro, "Mensual")
    
    n_meses = anios_pension * 12
    
    if tasa_mensual == 0:
        return capital_neto / n_meses

    # Usamos npf.pmt para calcular el pago mensual
    pension = npf.pmt(rate=tasa_mensual, nper=n_meses, pv=-capital_neto, fv=0)
    
    return pension

# ===================================================================
# LÓGICA MÓDULO C
# ===================================================================
def calcular_pv_bono(valor_nominal, tasa_cupon_anual, frecuencia_pago, plazo_anios, tasa_retorno_anual):
    """Calcula el Valor Presente (PV) de un bono."""
    
    n_periodos_por_anio = FRECUENCIAS.get(frecuencia_pago)
    n_periodos_total = plazo_anios * n_periodos_por_anio
    
    # 1. Tasa de cupón *periódica* (basada en la Tasa Cupón Anual)
    tasa_cupon_periodica = tasa_cupon_anual / n_periodos_por_anio
    monto_cupon = valor_nominal * tasa_cupon_periodica
    
    # 2. Tasa de retorno *periódica* (basada en la TEA de mercado)
    tasa_retorno_periodica = convertir_tea_a_tep(tasa_retorno_anual, frecuencia_pago)
    
    # 3. Crear la lista de flujos de caja
    flujos = [monto_cupon] * n_periodos_total
    flujos[-1] += valor_nominal # Añadir el Valor Nominal al último flujo
    
    # 4. Calcular el PV de cada flujo y el total
    data_flujos = []
    pv_total = 0
    
    for t in range(1, n_periodos_total + 1):
        flujo = flujos[t-1]
        pv_flujo = flujo / (1 + tasa_retorno_periodica)**t
        pv_total += pv_flujo
        
        data_flujos.append({
            "Periodo": t,
            "Flujo (Cupón)": monto_cupon if t < n_periodos_total else monto_cupon + valor_nominal,
            "Flujo Descontado (PV)": pv_flujo
        })

    # 5. También se puede usar npf.pv (más directo)
    # pv_calculado = -npf.pv(rate=tasa_retorno_periodica, nper=n_periodos_total, pmt=monto_cupon, fv=valor_nominal)
    
    df_flujos = pd.DataFrame(data_flujos)
    
    return pv_total, df_flujos