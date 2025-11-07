import streamlit as st
import pandas as pd
import financiero
import graficos
import exportar_pdf
from google import genai
import plotly.graph_objects as go
from graficos import generar_grafico_crecimiento, graficar_escenarios_lineas, graficar_escenarios_barras_agrupadas


# =========================
# Configuración API Gemini
# =========================
API_KEY = "AIzaSyBBHVQiFu_BqS1lUTgIWrIyDeG1AwYEG1s"  # <-- reemplaza aquí
client = genai.Client(api_key=API_KEY)

def interpretar(texto):
    """
    Envía un texto a la API de Gemini y devuelve la interpretación.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Explica de forma clara para un usuario no técnico el siguiente resultado financiero:\n{texto}\nExplicación:"
        )
        return response.text
    except Exception as e:
        return f"No se pudo generar interpretación: {e}"

# =========================
# Configuración de la página
# =========================
st.set_page_config(
    page_title="Simulador Financiero Corporativo",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Simulador de Finanzas Corporativas y Jubilación")
st.caption("Desarrollado para el Examen Parcial de Finanzas Corporativas")

# =========================
# Session State
# =========================
if 'capital_final_A' not in st.session_state:
    st.session_state.capital_final_A = 0.0
    st.session_state.aportes_totales_A = 0.0
    st.session_state.df_crecimiento = pd.DataFrame()
    st.session_state.df_escenarios = pd.DataFrame()

# =========================
# Pestañas
# =========================
tab_A, tab_B, tab_C = st.tabs([
    "📈 Módulo A: Crecimiento de Cartera",
    "🏖️ Módulo B: Proyección de Jubilación",
    "📜 Módulo C: Valoración de Bonos"
])

# =========================
# MÓDULO A
# =========================
with tab_A:
    st.header("Simulación de Crecimiento de Cartera")
    st.markdown("Calcule cómo crece su capital en el tiempo por interés compuesto.")

    with st.form(key="form_cartera"):
        col1, col2 = st.columns(2)
        with col1:
            monto_inicial = st.number_input("Monto Inicial (USD)", min_value=0.0, step=1000.0, value=10000.0)
            aporte_periodico = st.number_input("Aporte Periódico (USD)", min_value=0.0, step=100.0, value=500.0)
            frecuencia_aporte = st.selectbox("Frecuencia de Aportes", ["Mensual", "Trimestral", "Semestral", "Anual"], index=0)
        with col2:
            edad_actual = st.number_input("Edad Actual", min_value=18, max_value=80, value=30)
            edad_jubilacion = st.number_input("Edad de Jubilación", min_value=edad_actual+1, max_value=100, value=65)
            tea = st.slider("Tasa Efectiva Anual (TEA) (%)", min_value=0.0, max_value=50.0, value=8.0, step=0.5)

        submit_button_A = st.form_submit_button("Calcular Crecimiento 🚀")

    if submit_button_A:
        try:
            plazo_anios = edad_jubilacion - edad_actual
            tasa_anual = tea / 100.0
            df_crecimiento, capital_final, total_aportado = financiero.calcular_crecimiento_cartera(
                monto_inicial, aporte_periodico, frecuencia_aporte, tasa_anual, plazo_anios
            )
            st.session_state.capital_final_A = capital_final
            st.session_state.aportes_totales_A = total_aportado
            st.session_state.df_crecimiento = df_crecimiento

            

# Gráfico comparativo: aportes acumulados vs capital sin intereses vs capital con intereses
            df_crecimiento['Aportes Acumulados'] = df_crecimiento['Aporte'].cumsum()
            fig_comparativo = go.Figure()
            fig_comparativo.add_trace(go.Scatter(
                x=df_crecimiento.index,
                y=df_crecimiento['Aportes Acumulados'],
                mode='lines+markers',
                name='Aportes Acumulados',
                line=dict(color='blue', dash='dot')
            ))
            fig_comparativo.add_trace(go.Scatter(
                x=df_crecimiento.index,
                y=df_crecimiento['Saldo Inicial'] + df_crecimiento['Aporte'].cumsum(),
                mode='lines+markers',
                name='Capital sin intereses',
                line=dict(color='orange', dash='dash')
            ))
            fig_comparativo.add_trace(go.Scatter(
                x=df_crecimiento.index,
                y=df_crecimiento['Saldo Final'],
                mode='lines+markers',
                name='Capital con intereses',
                line=dict(color='green', width=3)
            ))
            fig_comparativo.update_layout(
                title="Comparación de Crecimiento de Capital",
                xaxis_title="Período",
                yaxis_title="USD",
                yaxis_tickprefix="$",
                template="plotly_white",
                legend_title="Líneas"
            )
            st.plotly_chart(fig_comparativo, use_container_width=True)

            # Mostrar métricas
            st.subheader("Resultados de la Simulación")
            col1, col2, col3 = st.columns(3)
            col1.metric("Capital Final Acumulado", f"${capital_final:,.2f}")
            col2.metric("Total Aportado", f"${total_aportado:,.2f}")
            col3.metric("Ganancia Total (Intereses)", f"${capital_final - total_aportado:,.2f}")

            # Interpretación IA
            texto_contexto = f"Capital final: ${capital_final:,.2f}, Total aportado: ${total_aportado:,.2f}, Ganancia: ${capital_final - total_aportado:,.2f}"
            st.info("Interpretación de la IA:")
            st.write(interpretar(texto_contexto))

            # Gráfico
            st.plotly_chart(graficos.generar_grafico_crecimiento(df_crecimiento), use_container_width=True)

            # Reporte detallado
            with st.expander("Ver reporte detallado del crecimiento (Tabla)"):
                st.dataframe(df_crecimiento.style.format({
                    "Saldo Inicial": "${:,.2f}",
                    "Aporte": "${:,.2f}",
                    "Interés Ganado": "${:,.2f}",
                    "Saldo Final": "${:,.2f}"
                }))

        except Exception as e:
            st.error(f"Error en el cálculo: {e}")

# =========================
# MÓDULO B
# =========================
with tab_B:
    st.header("Proyección de Retiro o Pensión Mensual")
    st.markdown("Use el capital acumulado en el Módulo A para proyectar su retiro.")

    if st.session_state.capital_final_A == 0.0:
        st.warning("Por favor, primero realice un cálculo en el 'Módulo A'.")
    else:
        st.info(f"Capital disponible para jubilación: **${st.session_state.capital_final_A:,.2f}**")

        with st.form(key="form_jubilacion"):
            col1, col2 = st.columns(2)
            with col1:
                tipo_impuesto = st.selectbox("Tipo de Impuesto sobre Ganancia", ["29.5% (Fuente Extranjera)", "5% (Bolsa Local)"])
            with col2:
                tea_retiro = st.slider("Tasa de Retorno durante el Retiro (TEA %)", min_value=0.0, max_value=20.0, value=5.0, step=0.1)
                anios_pension = st.number_input("Años esperados de retiro", min_value=1, max_value=50, value=25)
                factor_pension = st.checkbox("Aplicar pensión al 50% del rendimiento", value=True)

            comparacion_checkbox = st.checkbox("Comparar escenarios adicionales", value=False)
            if comparacion_checkbox:
                tasas_extra = st.text_input("TEA de retiro (separadas por coma)", value="5")
                edades_extra = st.text_input("Años de pensión (separadas por coma)", value=f"{anios_pension}")
                tasas_extra = [float(t.strip())/100 for t in tasas_extra.split(",") if t.strip()]
                edades_extra = [int(e.strip()) for e in edades_extra.split(",") if e.strip()]

            submit_button_B = st.form_submit_button("Calcular Proyección 🏖️")

        if submit_button_B:
            ganancia = st.session_state.capital_final_A - st.session_state.aportes_totales_A
            tasa_impuesto = 0.295 if "29.5%" in tipo_impuesto else 0.05
            impuesto_pagar, capital_neto = financiero.calcular_impuestos(
                st.session_state.capital_final_A, st.session_state.aportes_totales_A, tasa_impuesto
            )
            factor = 0.5 if factor_pension else 1.0
            pension_mensual = financiero.calcular_pension_mensual(
                capital_neto, tea_retiro/100.0, anios_pension, factor=factor
            )

            st.subheader("Resumen de Jubilación")
            col1, col2, col3 = st.columns(3)
            col1.metric("Ganancia de Capital", f"${ganancia:,.2f}")
            col2.metric("Impuesto a Pagar", f"${impuesto_pagar:,.2f}")
            col3.metric("Capital Neto (Post-Impuestos)", f"${capital_neto:,.2f}", delta_color="off")

            st.divider()
            col_op1, col_op2 = st.columns(2)
            with col_op1:
                st.subheader("Opción 1: Cobro Total")
                st.success(f"Pago único: **${capital_neto:,.2f}**")
            with col_op2:
                st.subheader(f"Opción 2: Pensión Mensual ({anios_pension} años)")
                st.info(f"Recibiría aproximadamente **${pension_mensual:,.2f} USD** mensuales")

            # Interpretación IA
            texto_contexto = f"Pensión mensual estimada: ${pension_mensual:,.2f}, Capital neto: ${capital_neto:,.2f}, Impuesto a pagar: ${impuesto_pagar:,.2f}"
            st.info("Interpretación de la IA:")
            st.write(interpretar(texto_contexto))

            # Escenarios comparativos
            if comparacion_checkbox and tasas_extra and edades_extra:
                st.subheader("Comparación de Escenarios")
                df_escenarios = financiero.calcular_escenarios_jubilacion(capital_neto, tasas_extra, edades_extra)
                st.session_state.df_escenarios = df_escenarios
                st.dataframe(df_escenarios.style.format({"Pensión Mensual (USD)":"${:,.2f}"}))

                fig = graficar_escenarios_barras_agrupadas(df_escenarios)
                st.plotly_chart(fig, use_container_width=True)

                # Gráfico de barras
                import plotly.express as px
                fig = px.bar(
                    df_escenarios,
                    x="Años de Pensión",
                    y="Pensión Mensual (USD)",
                    color="Tasa TEA Retiro (%)",
                    barmode="group",
                    title="Comparación de Pensión Mensual según Escenarios"
                )
                fig.update_layout(yaxis_tickprefix="$", yaxis_tickformat=',.2f')
                st.plotly_chart(fig, use_container_width=True)

                fig = graficar_escenarios_lineas(df_escenarios)
                st.plotly_chart(fig, use_container_width=True)
                
# =========================
# MÓDULO C
# =========================
with tab_C:
    st.header("Valoración de Bonos")
    st.markdown("Calcule el Valor Presente (PV) de un bono.")

    with st.form(key="form_bonos"):
        col1, col2, col3 = st.columns(3)
        with col1:
            valor_nominal = st.number_input("Valor Nominal (USD)", min_value=0.0, value=1000.0)
            tasa_cupon_tea = st.number_input("Tasa Cupón (TEA %)", min_value=0.0, max_value=50.0, value=5.0)
        with col2:
            frecuencia_pago_bono = st.selectbox("Frecuencia de Pago", ["Anual","Semestral","Cuatrimestral","Trimestral","Bimestral","Mensual"])
            plazo_anios_bono = st.number_input("Plazo en Años", min_value=1, value=10)
        with col3:
            tea_retorno_bono = st.number_input("Tasa de Retorno Esperada (TEA %)", min_value=0.0, max_value=50.0, value=6.0)

        submit_button_C = st.form_submit_button("Calcular Valor del Bono 📜")

    if submit_button_C:
        try:
            pv_bono, df_flujos = financiero.calcular_pv_bono(
                valor_nominal, tasa_cupon_tea/100.0, frecuencia_pago_bono, plazo_anios_bono, tea_retorno_bono/100.0
            )
            st.subheader("Resultados de la Valoración")
            st.metric("Valor Presente (PV) del Bono", f"${pv_bono:,.2f}")

            if pv_bono > valor_nominal:
                st.success("Bono cotiza **Sobre la Par** (Premium).")
            elif pv_bono < valor_nominal:
                st.warning("Bono cotiza **Bajo la Par** (Discount).")
            else:
                st.info("Bono cotiza **A la Par** (Par).")

            # Interpretación IA
            texto_contexto = f"Valor presente del bono: ${pv_bono:,.2f}, Valor nominal: ${valor_nominal:,.2f}"
            st.info("Interpretación de la IA:")
            st.write(interpretar(texto_contexto))

            with st.expander("Desglose de Flujos de Caja"):
                st.dataframe(df_flujos.style.format({
                    "Flujo (Cupón)":"${:,.2f}",
                    "Flujo Descontado (PV)":"${:,.2f}"
                }))

        except Exception as e:
            st.error(f"Error en el cálculo: {e}")

# =========================
# Barra lateral: ayuda y exportación
# =========================
with st.sidebar:
    st.header("Ayuda y Exportación")
    st.info("Pase el cursor sobre los campos con un [?] para ver la explicación.")

    st.subheader("Exportar Reporte")

    if st.session_state.capital_final_A > 0:
        pdf_data = exportar_pdf.crear_reporte_jubilacion(
            df_crecimiento=st.session_state.df_crecimiento,
            capital_final=st.session_state.capital_final_A,
            total_aportado=st.session_state.aportes_totales_A,
            df_escenarios=st.session_state.df_escenarios
        )

        st.download_button(
            label="⬇️ Descargar Reporte de Jubilación (PDF)",
            data=pdf_data,
            file_name="Reporte_Jubilacion.pdf",
            mime="application/pdf"
        )
    else:
        st.write("⚠️ Complete el Módulo A para generar un reporte.")


