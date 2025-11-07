import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import financiero # Nuestro módulo de cálculos
import graficos   # Nuestro módulo de gráficos
import exportar_pdf # Nuestro módulo de PDF
from perfil_inversor import PerfilInversor  # Nuestro nuevo módulo de IA

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Simulador Financiero Corporativo",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Simulador de Finanzas Corporativas y Jubilación")
st.caption("Desarrollado para el Examen Parcial de Finanzas Corporativas")

# --- Sección de Perfil de Inversor ---
with st.expander("🧩 Evaluación de Perfil de Inversor", expanded=True):
    st.write("Complete el siguiente cuestionario para obtener recomendaciones personalizadas de inversión:")
    
    # Pestañas para organizar el cuestionario
    tab_info, tab_riesgo, tab_objetivos = st.tabs(["📝 Información Básica", "🎯 Perfil de Riesgo", "🎯 Objetivos Financieros"])
    
    with tab_info:
        col1, col2 = st.columns(2)
        with col1:
            edad = st.slider("Edad", 18, 100, 30, 
                           help="Su edad actual en años")
            
            estado_civil = st.selectbox("Estado civil", 
                                      ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a", "Unión libre"],
                                      help="Su estado civil actual")
            
            hijos = st.number_input("Número de dependientes", 0, 10, 0,
                                  help="Personas que dependen económicamente de usted")
        
        with col2:
            ingresos = st.number_input("Ingresos mensuales netos (USD)", 
                                     min_value=100, max_value=100000, value=2000,
                                     help="Ingresos mensuales después de impuestos")
            
            gastos_mensuales = st.number_input("Gastos mensuales (USD)", 
                                             min_value=100, max_value=50000, value=1500,
                                             help="Gastos fijos mensuales")
            
            ahorro_porcentaje = st.slider("Porcentaje de ahorro mensual", 
                                        1, 90, 20,
                                        help="¿Qué porcentaje de sus ingresos ahorra o puede invertir?")
    
    with tab_riesgo:
        col1, col2 = st.columns(2)
        with col1:
            horizonte = st.slider("Horizonte de inversión (años)", 
                                1, 50, 20,
                                help="¿Por cuántos años planea mantener sus inversiones?")
            
            experiencia = st.slider("Años de experiencia en inversiones", 
                                 0, 50, 5,
                                 help="Años de experiencia en inversiones financieras")
            
            conocimiento_financiero = st.slider("Nivel de conocimiento financiero (1-5)", 
                                             1, 5, 3,
                                             help="1: Básico, 5: Avanzado")
        
        with col2:
            tolerancia = st.slider("Tolerancia al riesgo (1-5)", 
                                1, 5, 3,
                                help="1: Baja tolerancia, 5: Alta tolerancia")
            
            reaccion_mercado = st.selectbox("¿Cómo reaccionaría ante una caída del 20% en sus inversiones?",
                                         ["Vendería todo para evitar más pérdidas",
                                          "Vendería una parte para reducir exposición",
                                          "Mantendría la inversión esperando recuperación",
                                          "Aprovecharía para comprar más activos a menor precio"],
                                         index=2)
    
    with tab_objetivos:
        col1, col2 = st.columns(2)
        with col1:
            objetivo_principal = st.selectbox("Su principal objetivo financiero es:",
                                           ["Preservar mi capital",
                                            "Generar ingresos estables",
                                            "Crecimiento moderado de mi inversión",
                                            "Maximizar ganancias a largo plazo",
                                            "Acumular para un objetivo específico"])
            
            patrimonio_actual = st.number_input("Patrimonio actual (USD)",
                                             min_value=0, max_value=10000000, value=50000,
                                             help="Valor total de sus activos actuales")
        
        with col2:
            plazo_objetivo = st.slider("Plazo para alcanzar su objetivo (años)",
                                     1, 40, 10,
                                     help="En cuántos años espera alcanzar su objetivo financiero")
            
            aporte_adicional = st.number_input("¿Puede realizar aportes adicionales en caso necesario? (USD/mes)",
                                            min_value=0, max_value=10000, value=200,
                                            help="Monto que podría aportar adicionalmente en caso necesario")
    
    # Botón para analizar el perfil
    if st.button("🔍 Analizar mi perfil de inversor", type="primary", use_container_width=True):
        with st.spinner('Analizando su perfil...'):
            # Inicializar el clasificador
            clasificador = PerfilInversor()
            
            # Mapear la reacción al mercado a un valor numérico
            reaccion_valor = {
                "Vendería todo para evitar más pérdidas": 1,
                "Vendería una parte para reducir exposición": 2,
                "Mantendría la inversión esperando recuperación": 3,
                "Aprovecharía para comprar más activos a menor precio": 4
            }
            
            # Mapear el objetivo principal a un valor numérico
            objetivo_valor = {
                "Preservar mi capital": 1,
                "Generar ingresos estables": 2,
                "Crecimiento moderado de mi inversión": 3,
                "Maximizar ganancias a largo plazo": 5,
                "Acumular para un objetivo específico": 4
            }
            
            # Preparar datos del usuario
            datos_usuario = {
                'edad': edad,
                'horizonte': horizonte,
                'tolerancia': tolerancia,
                'ingresos': ingresos,
                'ahorro_porcentaje': ahorro_porcentaje,
                'experiencia': experiencia,
                'patrimonio_actual': patrimonio_actual,
                'nivel_educacion': conocimiento_financiero,
                'objetivos': objetivo_valor.get(objetivo_principal, 3),
                'conocimiento_financiero': conocimiento_financiero,
                'capacidad_endeudamiento': ingresos * 0.3  # Capacidad de endeudamiento estimada
            }
            
            # Predecir perfil
            resultado = clasificador.predecir_perfil(datos_usuario)
            
            # Guardar resultados en la sesión
            st.session_state.perfil_inversor = resultado
            st.session_state.perfil_calculado = True
    
    # Mostrar resultados si están disponibles
    if 'perfil_calculado' in st.session_state and st.session_state.perfil_calculado:
        resultado = st.session_state.perfil_inversor
        
        # Debug: Verificar que el resultado tenga datos válidos
        if not resultado or not isinstance(resultado, dict):
            st.error("Error: No se pudo obtener el resultado del perfil. Por favor, intente nuevamente.")
            st.stop()
        
        # Mostrar tarjeta de resultados
        with st.container():
            st.markdown("---")
            st.markdown("## 🔍 Resultado de tu perfil de inversor")
            
            # Encabezado con el perfil
            col1, col2 = st.columns([1, 2])
            with col1:
                # Mostrar perfil con color según el tipo
                if resultado['perfil'] == 'conservador':
                    st.markdown("### 🛡️ Perfil Conservador")
                    st.metric("Nivel de riesgo", "Bajo", "1/5")
                elif resultado['perfil'] == 'moderado':
                    st.markdown("### ⚖️ Perfil Moderado")
                    st.metric("Nivel de riesgo", "Medio", "3/5")
                else:
                    st.markdown("### 🚀 Perfil Agresivo")
                    st.metric("Nivel de riesgo", "Alto", "5/5")
                
                # Mostrar confianza con mejor formato
                confianza = resultado.get('confianza', 0)
                st.markdown("### 🔍 Nivel de confianza del análisis")
                col_conf1, col_conf2 = st.columns([1, 3])
                with col_conf1:
                    st.metric("Confianza", f"{confianza:.1f}%")
                with col_conf2:
                    st.progress(min(100, int(confianza)) / 100, 
                              text=f"Nivel de confianza del análisis")
                
                # Tasa de retorno sugerida con mejor formato
                st.markdown("### 📈 Retorno esperado")
                tasas = resultado.get('tasa_sugerida', {})
                if isinstance(tasas, dict) and all(k in tasas for k in ['min', 'max', 'media']):
                    st.metric("Rango de retorno anual esperado", 
                            f"{tasas['min']}% - {tasas['max']}%",
                            f"Media: {tasas['media']}%")
                else:
                    tasa_valor = tasas if isinstance(tasas, (int, float)) else 5.0
                    st.metric("Retorno anual esperado", f"{tasa_valor}%")
            
            with col2:
                # Descripción del perfil
                st.markdown(PerfilInversor.get_descripcion_perfil(resultado['perfil']))
            
            # Sección de distribución de activos recomendada
            st.markdown("---")
            st.markdown("## 📊 Distribución de activos recomendada")
            
            distribucion = resultado.get('distribucion_activos', {})
            if not distribucion:
                st.error("⚠️ Error: No se pudo obtener la distribución de activos. El resultado del análisis puede estar incompleto.")
                st.info("💡 Sugerencia: Intente presionar el botón 'Analizar mi perfil de inversor' nuevamente.")
                activos = []  # Definir valores por defecto
                valores = []
            else:
                activos = [k for k in distribucion.keys() if k != 'Descripción']
                valores = [v for k, v in distribucion.items() if k != 'Descripción']
            
            # Gráfico de torta mejorado
            if activos and any(valores):
                # Asegurarse de que los valores sumen 100
                total = sum(valores)
                if total > 0:
                    valores = [v/total*100 for v in valores]  # Normalizar a porcentajes
                
                # Crear el gráfico de torta con colores atractivos
                colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                         '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
                
                fig = go.Figure(data=[go.Pie(
                    labels=activos,
                    values=valores,
                    hole=0.3,
                    textinfo='percent+label',
                    insidetextorientation='radial',
                    marker=dict(colors=colors, line=dict(color='#FFFFFF', width=1)),
                    textfont=dict(size=14)
                )])
                
                fig.update_layout(
                    showlegend=False,
                    margin=dict(l=10, r=10, t=20, b=10),
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
                # Mostrar tabla con los porcentajes
                df_distribucion = pd.DataFrame({
                    'Activo': activos,
                    'Porcentaje': [f"{v:.1f}%" for v in valores]
                })
                st.dataframe(
                    df_distribucion,
                    column_config={
                        "Activo": "Activo",
                        "Porcentaje": st.column_config.ProgressColumn(
                            "Porcentaje",
                            format="%f",
                            min_value=0,
                            max_value=100,
                        ),
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                if 'Descripción' in distribucion:
                    st.info(distribucion['Descripción'])
            else:
                st.warning("No hay datos de distribución disponibles para mostrar.")
            
            # Sección de proyecciones mejorada
            st.markdown("---")
            st.markdown("## 📈 Proyecciones a largo plazo")
            
            proyecciones = resultado.get('proyecciones', {})
            if not proyecciones or not any(proyecciones.values()):
                st.error("⚠️ Error: No se pudieron generar las proyecciones.")
                st.info("💡 Sugerencia: Verifique que haya ingresado su patrimonio actual e ingresos mensuales correctamente.")
                if st.button("🔄 Volver a analizar perfil"):
                    del st.session_state.perfil_calculado
                    st.rerun()
            else:
                # Crear figura con estilo mejorado
                fig = go.Figure()
                
                # Definir colores para cada perfil
                colores = {
                    'conservador': '#2ecc71',  # Verde
                    'moderado': '#f39c12',     # Naranja
                    'agresivo': '#e74c3c'      # Rojo
                }
                
                for perfil, datos in proyecciones.items():
                    if not datos or 'años' not in datos or 'saldos' not in datos:
                        continue
                        
                    es_perfil_actual = (perfil == resultado.get('perfil', ''))
                    color = colores.get(perfil, '#3498db')
                    
                    # Formatear los valores en formato de moneda
                    valores_formateados = [f"${v:,.0f}" for v in datos['saldos']]
                    
                    fig.add_trace(go.Scatter(
                        x=datos['años'],
                        y=datos['saldos'],
                        mode='lines+markers+text',
                        name=f"{perfil.capitalize()}",
                        text=valores_formateados if es_perfil_actual else None,
                        textposition="top center",
                        line=dict(
                            width=4 if es_perfil_actual else 2,
                            dash='solid' if es_perfil_actual else 'dot',
                            color=color
                        ),
                        marker=dict(
                            size=10 if es_perfil_actual else 6,
                            color=color
                        ),
                        hovertemplate=
                            f"<b>{perfil.capitalize()}</b><br>" +
                            "Año: %{x}<br>" +
                            "Patrimonio: $%{{y:,.0f}}<br>" +
                            f"Tasa: {datos.get('rango', 'N/A')}<extra></extra>",
                        showlegend=True
                    ))
                
                # Mejorar el diseño del gráfico
                fig.update_layout(
                    xaxis=dict(
                        title="Edad",
                        showgrid=True,
                        gridwidth=1,
                        gridcolor='rgba(0,0,0,0.05)',
                        tickmode='array',
                        tickvals=datos['años'],
                        ticktext=[str(int(a)) for a in datos['años']]
                    ),
                    yaxis=dict(
                        title="Patrimonio (USD)",
                        showgrid=True,
                        gridwidth=1,
                        gridcolor='rgba(0,0,0,0.05)',
                        tickprefix="$",
                        tickformat=",.0f"
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5,
                        bgcolor='rgba(255,255,255,0.8)'
                    ),
                    hovermode="x unified",
                    height=500,
                    margin=dict(l=50, r=50, t=50, b=50),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=14,
                        font_family="Arial"
                    )
                )
                
                # Añadir anotación para el perfil actual
                if resultado.get('perfil') in proyecciones:
                    perfil_actual = resultado['perfil']
                    datos_actuales = proyecciones[perfil_actual]
                    if datos_actuales and 'saldos' in datos_actuales and 'años' in datos_actuales:
                        ultimo_año = datos_actuales['años'][-1]
                        ultimo_valor = datos_actuales['saldos'][-1]
                        
                        fig.add_annotation(
                            x=ultimo_año,
                            y=ultimo_valor,
                            text=f"Tu perfil: {perfil_actual.capitalize()}",
                            showarrow=True,
                            arrowhead=2,
                            ax=0,
                            ay=-40,
                            font=dict(size=12, color=colores.get(perfil_actual, '#000000'))
                        )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
                
                # Añadir explicación
                st.markdown("""
                **Explicación de las proyecciones:**
                - **Línea continua**: Tu perfil de inversión actual
                - **Líneas punteadas**: Otros perfiles para comparación
                - **Valores**: Patrimonio proyectado en USD a diferentes edades
                - **Tasas**: Retorno anual esperado para cada perfil
                """)
                    
            # Mover las recomendaciones dentro del mismo contenedor
            st.markdown("---")
            st.markdown("## 💡 Recomendaciones personalizadas")
            
            recomendaciones = resultado.get('recomendaciones', [])
            if not recomendaciones:
                st.error("⚠️ Error: No hay recomendaciones disponibles.")
                st.info("💡 El análisis de perfil puede estar incompleto. Intente analizar nuevamente.")
            else:
                for i, rec in enumerate(recomendaciones):
                    with st.container():
                        st.markdown(f"### 📌 {rec.get('titulo', f'Recomendación {i+1}')}")
                        st.markdown(f"**{rec.get('contenido', '')}**")
                        st.markdown("**Acciones recomendadas:**")
                        for accion in rec.get('acciones', []):
                            st.markdown(f"- ✅ {accion}")
                        st.markdown("")
                
            # Factores clave
            st.markdown("---")
            st.markdown("## 🎯 Factores clave en tu perfil")
            
            # Ordenar características por importancia
            importancias = resultado.get('importancias', {})
            if not importancias:
                st.error("⚠️ Error: No se pudieron determinar los factores clave.")
                st.info("💡 El modelo de IA puede necesitar ser reentrenado. Intente analizar su perfil nuevamente.")
            else:
                caracteristicas_ordenadas = sorted(
                    importancias.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )
                
                # Mostrar las 5 características más importantes
                st.markdown("### 🎯 Factores clave en tu perfil")
                st.markdown("Estos son los factores que más influyeron en la determinación de tu perfil de inversor:")
                
                # Mostrar métricas
                cols = st.columns(5)
                for i, (caract, importancia) in enumerate(caracteristicas_ordenadas[:5]):
                    with cols[i % 5]:
                        st.metric(
                            label=caract.replace('_', ' ').title(),
                            value=f"{importancia*100:.1f}%"
                        )
                
                # Mostrar barras de progreso
                st.markdown("### Influencia de cada factor:")
                descripciones = {
                    'tolerancia': "Tu capacidad para asumir riesgos financieros. Una mayor tolerancia al riesgo puede permitirte considerar inversiones más volátiles con mayor potencial de retorno.",
                    'horizonte': "El tiempo que planeas mantener tus inversiones. Un horizonte más largo te permite asumir más riesgo, ya que tienes más tiempo para recuperarte de posibles pérdidas.",
                    'edad': "Tu edad actual afecta tu capacidad de asumir riesgos. Generalmente, los inversores más jóvenes pueden permitirse ser más agresivos en sus inversiones.",
                    'ingresos': "Tus ingresos mensuales o anuales. Unos ingresos más estables pueden permitirte asumir más riesgos en tus inversiones.",
                    'ahorro_porcentaje': "El porcentaje de tus ingresos que ahorras o inviertes. Un mayor porcentaje puede permitirte alcanzar tus metas financieras más rápidamente.",
                    'experiencia': "Tus años de experiencia en inversiones. Una mayor experiencia puede ayudarte a manejar mejor la volatilidad del mercado.",
                    'patrimonio_actual': "El valor total de tus activos actuales. Un patrimonio más grande puede permitirte diversificar más tus inversiones.",
                    'objetivos': "Tus metas financieras a corto, mediano y largo plazo. Objetivos más ambiciosos pueden requerir estrategias de inversión más agresivas.",
                    'conocimiento_financiero': "Tu nivel de comprensión sobre conceptos financieros e inversiones. Un mayor conocimiento puede ayudarte a tomar decisiones más informadas.",
                    'capacidad_endeudamiento': "Tu capacidad para asumir deudas de manera responsable. Una mayor capacidad puede ofrecer más opciones de inversión con apalancamiento."
                }
                
                for caracteristica, valor in caracteristicas_ordenadas[:5]:
                    nombre_bonito = caracteristica.replace('_', ' ').title()
                    st.markdown(f"**{nombre_bonito}**")
                    st.progress(min(100, int(valor * 100)) / 100, 
                              text=f"{valor*100:.1f}% de influencia")
                    # Mostrar descripción directamente
                    st.caption(f"ℹ️ {descripciones.get(caracteristica, 'Este factor influye en la determinación de tu perfil de inversor.')}")
                    st.markdown("")

# Inicializar tasa_predeterminada con un valor por defecto
tasa_predeterminada = 5.0  # Tasa predeterminada en caso de que no haya perfil

# Mostrar recomendaciones basadas en el perfil si ya se ha calculado
if 'perfil_inversor' in st.session_state:
    perfil = st.session_state.perfil_inversor
    # Asegurarnos de que perfil sea una cadena
    perfil_texto = perfil['perfil'] if isinstance(perfil, dict) and 'perfil' in perfil else str(perfil)
    st.sidebar.success(f"Perfil detectado: {perfil_texto.upper()}")
    
    # Manejar la tasa sugerida
    if isinstance(perfil, dict) and 'tasa_sugerida' in perfil:
        tasa = perfil['tasa_sugerida']
        if isinstance(tasa, dict):
            if 'media' in tasa:
                tasa_media = tasa['media']
                st.sidebar.info(f"Tasa de retorno sugerida: {tasa_media}%")
                tasa_predeterminada = tasa_media
            else:
                st.sidebar.warning("Formato de tasa no reconocido")
        elif isinstance(tasa, (int, float)):
            st.sidebar.info(f"Tasa de retorno sugerida: {tasa}%")
            tasa_predeterminada = tasa
        else:
            st.sidebar.warning("Tasa de retorno no disponible")
    else:
        st.sidebar.warning("No se pudo determinar la tasa de retorno")

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