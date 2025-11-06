import streamlit as st
import pandas as pd
import financiero # Nuestro módulo de cálculos
import graficos   # Nuestro módulo de gráficos
import exportar_pdf # Nuestro módulo de PDF

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Simulador Financiero Corporativo",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Simulador de Finanzas Corporativas y Jubilación")
st.caption("Desarrollado para el Examen Parcial de Finanzas Corporativas")

# --- Usar st.session_state para compartir datos entre módulos ---
# Necesitamos esto para que el Módulo B use el resultado del Módulo A
if 'capital_final_A' not in st.session_state:
    st.session_state.capital_final_A = 0.0
    st.session_state.aportes_totales_A = 0.0
    st.session_state.df_crecimiento = pd.DataFrame()


# --- Definición de las Pestañas (Módulos) ---
tab_A, tab_B, tab_C = st.tabs([
    "📈 Módulo A: Crecimiento de Cartera", 
    "🏖️ Módulo B: Proyección de Jubilación", 
    "📜 Módulo C: Valoración de Bonos"
])


# ===================================================================
# MÓDULO A: Crecimiento de Cartera
# ===================================================================
with tab_A:
    st.header("Simulación de Crecimiento de Cartera")
    st.markdown("Calcule cómo crece su capital en el tiempo por interés compuesto.")

    # --- Entradas de Usuario (Formulario) ---
    with st.form(key="form_cartera"):
        col1, col2 = st.columns(2)
        with col1:
            monto_inicial = st.number_input("Monto Inicial (USD)", min_value=0.0, step=1000.0, value=10000.0)
            aporte_periodico = st.number_input("Aporte Periódico (USD)", min_value=0.0, step=100.0, value=500.0)
            frecuencia_aporte = st.selectbox("Frecuencia de Aportes", 
                                             ["Mensual", "Trimestral", "Semestral", "Anual"], index=0)
        with col2:
            edad_actual = st.number_input("Edad Actual", min_value=18, max_value=80, value=30)
            edad_jubilacion = st.number_input("Edad de Jubilación", min_value=edad_actual + 1, max_value=100, value=65)
            tea = st.slider("Tasa Efectiva Anual (TEA) Esperada (%)", min_value=0.0, max_value=50.0, value=8.0, step=0.5)

        submit_button_A = st.form_submit_button(label="Calcular Crecimiento 🚀")

    # --- Lógica de Cálculo y Salidas ---
    if submit_button_A:
        plazo_anios = edad_jubilacion - edad_actual
        tasa_anual = tea / 100.0
        
        # 1. Llamar a la función de cálculo
        try:
            df_crecimiento, capital_final, total_aportado = financiero.calcular_crecimiento_cartera(
                monto_inicial=monto_inicial,
                aporte_periodico=aporte_periodico,
                frecuencia_aporte=frecuencia_aporte,
                tasa_anual=tasa_anual,
                plazo_anios=plazo_anios
            )
            
            # Guardar resultados para Módulo B
            st.session_state.capital_final_A = capital_final
            st.session_state.aportes_totales_A = total_aportado + monto_inicial
            st.session_state.df_crecimiento = df_crecimiento

            # 2. Mostrar Métricas Clave
            st.subheader("Resultados de la Simulación")
            col_res1, col_res2, col_res3 = st.columns(3)
            col_res1.metric("Capital Final Acumulado", f"${capital_final:,.2f}")
            col_res2.metric("Total Aportado", f"${(total_aportado + monto_inicial):,.2f}")
            col_res3.metric("Ganancia Total (Intereses)", f"${(capital_final - (total_aportado + monto_inicial)):,.2f}")

            # 3. Mostrar Gráfica
            st.plotly_chart(graficos.generar_grafico_crecimiento(df_crecimiento), use_container_width=True)

            # 4. Mostrar Reporte Detallado
            with st.expander("Ver reporte detallado del crecimiento (Tabla)"):
                st.dataframe(df_crecimiento.style.format({
                    "Saldo Inicial": "${:,.2f}",
                    "Aporte": "${:,.2f}",
                    "Interés Ganado": "${:,.2f}",
                    "Saldo Final": "${:,.2f}"
                }))

        except Exception as e:
            st.error(f"Error en el cálculo: {e}")


# ===================================================================
# MÓDULO B: Proyección de Jubilación
# ===================================================================
with tab_B:
    st.header("Proyección de Retiro o Pensión Mensual")
    st.markdown("Use el capital acumulado en el Módulo A para proyectar su retiro.")

    # --- Validar si el Módulo A se ha calculado ---
    if st.session_state.capital_final_A == 0.0:
        st.warning("Por favor, primero realice un cálculo en el 'Módulo A' para tener un capital que proyectar.")
    else:
        st.info(f"Capital disponible para jubilación (calculado en Módulo A): **${st.session_state.capital_final_A:,.2f}**")

        with st.form(key="form_jubilacion"):
            col1, col2 = st.columns(2)
            with col1:
                tipo_impuesto = st.selectbox("Tipo de Impuesto sobre Ganancia", 
                                             ["29.5% (Fuente Extranjera)", "5% (Bolsa Local)"])
            with col2:
                # Requerimiento B.2: Tasa de retorno durante el retiro
                tea_retiro = st.slider("Tasa de Retorno durante el Retiro (TEA %)", 
                                       min_value=0.0, max_value=20.0, value=5.0, step=0.1,
                                       help="Tasa esperada que seguirá generando su capital *después* de jubilarse.")
                anios_pension = st.number_input("Años esperados de retiro (para cálculo de pensión)", 
                                                min_value=1, max_value=50, value=25)

            submit_button_B = st.form_submit_button(label="Calcular Proyección de Retiro 🏖️")

        if submit_button_B:
            # 1. Calcular Impuestos
            ganancia = st.session_state.capital_final_A - st.session_state.aportes_totales_A
            tasa_impuesto = 0.295 if "29.5%" in tipo_impuesto else 0.05
            
            impuesto_pagar, capital_neto = financiero.calcular_impuestos(
                capital_final=st.session_state.capital_final_A,
                total_aportado=st.session_state.aportes_totales_A,
                tasa_impuesto=tasa_impuesto
            )

            # 2. Calcular Pensión Mensual
            pension_mensual = financiero.calcular_pension_mensual(
                capital_neto=capital_neto,
                tasa_anual_retiro=tea_retiro / 100.0,
                anios_pension=anios_pension
            )

            # 3. Mostrar Resultados (Opciones de Jubilación)
            st.subheader("Resumen de Jubilación")
            
            col_tax1, col_tax2, col_tax3 = st.columns(3)
            col_tax1.metric("Ganancia de Capital", f"${ganancia:,.2f}")
            col_tax2.metric("Impuesto a Pagar", f"${impuesto_pagar:,.2f}")
            col_tax3.metric("Capital Neto (Post-Impuestos)", f"${capital_neto:,.2f}", delta_color="off")
            
            st.divider()

            col_op1, col_op2 = st.columns(2)
            # Opción 1: Cobro Total
            with col_op1:
                st.subheader("Opción 1: Cobro Total (Lump Sum)")
                st.success(f"Usted retiraría un pago único de **${capital_neto:,.2f}**.")
            
            # Opción 2: Pensión Mensual
            with col_op2:
                st.subheader(f"Opción 2: Pensión Mensual (por {anios_pension} años)")
                st.info(f"Recibiría una pensión estimada de **${pension_mensual:,.2f} USD** mensuales.")

# ===================================================================
# MÓDULO C: Valoración de Bonos
# ===================================================================
with tab_C:
    st.header("Valoración de Bonos")
    st.markdown("Calcule el Valor Presente (PV) de un bono.")
    
    with st.form(key="form_bonos"):
        col1, col2, col3 = st.columns(3)
        with col1:
            valor_nominal = st.number_input("Valor Nominal (USD)", min_value=0.0, value=1000.0)
            tasa_cupon_tea = st.number_input("Tasa Cupón (TEA %)", min_value=0.0, max_value=50.0, value=5.0)
        with col2:
            frecuencia_pago_bono = st.selectbox("Frecuencia de Pago (Cupón)", 
                                                ["Anual", "Semestral", "Cuatrimestral", "Trimestral", "Bimestral", "Mensual"])
            plazo_anios_bono = st.number_input("Plazo en Años (al vencimiento)", min_value=1, value=10)
        with col3:
            tea_retorno_bono = st.number_input("Tasa de Retorno Esperada (TIR / YTM %)", 
                                               min_value=0.0, max_value=50.0, value=6.0,
                                               help="Esta es la tasa de descuento del mercado (TEA).")

        submit_button_C = st.form_submit_button(label="Calcular Valor del Bono 📜")

    if submit_button_C:
        try:
            # 1. Llamar a la función de cálculo
            pv_bono, df_flujos = financiero.calcular_pv_bono(
                valor_nominal=valor_nominal,
                tasa_cupon_anual=tasa_cupon_tea / 100.0,
                frecuencia_pago=frecuencia_pago_bono,
                plazo_anios=plazo_anios_bono,
                tasa_retorno_anual=tea_retorno_bono / 100.0
            )

            # 2. Mostrar Resultado Principal
            st.subheader("Resultados de la Valoración")
            st.metric("Valor Presente (PV) del Bono", f"${pv_bono:,.2f}")
            
            if pv_bono > valor_nominal:
                st.success("El bono se cotiza **Sobre la Par** (Premium).")
            elif pv_bono < valor_nominal:
                st.warning("El bono se cotiza **Bajo la Par** (Discount).")
            else:
                st.info("El bono se cotiza **A la Par** (Par).")

            # 3. Mostrar Flujos
            with st.expander("Ver desglose de flujos de caja descontados"):
                st.dataframe(df_flujos.style.format({
                    "Flujo (Cupón)": "${:,.2f}",
                    "Flujo Descontado (PV)": "${:,.2f}"
                }))
        
        except Exception as e:
            st.error(f"Error en el cálculo: {e}")

# --- Barra Lateral para Exportación y Ayuda ---
with st.sidebar:
    st.header("Ayuda y Exportación")
    
    # 1. Ayuda Contextual (Requerimiento 91)
    st.info("Pase el cursor sobre los campos con un [?] para ver una explicación.")
    
    # 2. Exportación a PDF (Requerimiento 92)
    st.subheader("Exportar Reporte")
    if st.session_state.capital_final_A > 0:
        pdf_data = exportar_pdf.crear_reporte_jubilacion(
            df_crecimiento=st.session_state.df_crecimiento,
            capital_final=st.session_state.capital_final_A,
            total_aportado=st.session_state.aportes_totales_A
            # ... pasar más datos si es necesario
        )
        st.download_button(
            label="Descargar Reporte de Jubilación (PDF)",
            data=pdf_data,
            file_name="Reporte_Jubilacion.pdf",
            mime="application/pdf"
        )
    else:
        st.write("Complete el Módulo A para generar un reporte.")