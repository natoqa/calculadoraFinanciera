import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import os
from typing import Dict, List, Tuple

class PerfilInversor:
    def __init__(self):
        self.model = None
        self.le = LabelEncoder()
        self.model_path = 'modelo_perfil_inversor.pkl'
        self.entrenar_modelo()
    
    def generar_datos_ejemplo(self):
        """Genera un conjunto de datos de ejemplo más robusto"""
        np.random.seed(42)
        n_samples = 5000  # Aumentamos el tamaño de la muestra para mayor precisión
        
        # Características principales
        edades = np.random.normal(45, 15, n_samples).clip(18, 80)
        horizontes = np.random.normal(20, 10, n_samples).clip(1, 40)
        tolerancias = np.random.normal(3, 1.5, n_samples).clip(1, 5)
        ingresos = np.random.lognormal(3.5, 0.6, n_samples).clip(10, 300)
        porcentaje_ahorro = np.random.normal(15, 8, n_samples).clip(1, 60)
        experiencia = np.random.normal(8, 7, n_samples).clip(0, 40)
        
        # Nuevas características
        patrimonio_actual = (ingresos * 12 * (edades - 20) * 0.3 * np.random.normal(1, 0.3, n_samples)).clip(0, 5000000)
        nivel_educacion = np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.1, 0.2, 0.4, 0.2, 0.1])
        objetivos = np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.15, 0.25, 0.3, 0.2, 0.1])
        conocimiento_financiero = np.random.normal(3, 1.2, n_samples).clip(1, 5)
        capacidad_endeudamiento = (ingresos * 0.3 - np.random.normal(500, 200, n_samples)).clip(0, 10000)
        
        # Generar perfiles con reglas más sofisticadas
        perfiles = []
        for i in range(n_samples):
            # Factores ponderados
            edad_score = 1 - (edades[i] - 18) / 62  # Menor puntuación para mayores
            horizonte_score = (horizontes[i] / 40) ** 0.5  # Raíz cuadrada para suavizar
            tolerancia_score = (tolerancias[i] - 1) / 4  # Normalizado 0-1
            ingreso_score = np.log10(ingresos[i] / 10) / 1.5  # Logarítmico
            ahorro_score = (porcentaje_ahorro[i] / 60) ** 0.7
            experiencia_score = (experiencia[i] / 40) ** 0.8
            educacion_score = (nivel_educacion[i] - 1) / 4
            objetivo_score = (objetivos[i] - 1) / 4
            conocimiento_score = (conocimiento_financiero[i] - 1) / 4
            
            # Ponderación de factores
            score = (
                edad_score * 0.15 +
                horizonte_score * 0.2 +
                tolerancia_score * 0.25 +
                ingreso_score * 0.1 +
                ahorro_score * 0.1 +
                experiencia_score * 0.05 +
                educacion_score * 0.05 +
                objetivo_score * 0.05 +
                conocimiento_score * 0.05
            )
            
            # Umbrales ajustados
            if score < 0.35:
                perfiles.append("conservador")
            elif score < 0.7:
                perfiles.append("moderado")
            else:
                perfiles.append("agresivo")
        
        # Crear DataFrame con todas las características
        data = pd.DataFrame({
            'edad': edades,
            'horizonte': horizontes,
            'tolerancia': tolerancias,
            'ingresos': ingresos,
            'ahorro_porcentaje': porcentaje_ahorro,
            'experiencia': experiencia,
            'patrimonio_actual': patrimonio_actual,
            'nivel_educacion': nivel_educacion,
            'objetivos': objetivos,
            'conocimiento_financiero': conocimiento_financiero,
            'capacidad_endeudamiento': capacidad_endeudamiento,
            'perfil': perfiles
        })
        
        return data
    
    def entrenar_modelo(self):
        """Entrena el modelo o lo carga si ya existe"""
        if os.path.exists(self.model_path):
            try:
                # Intentar cargar el modelo, scaler Y label encoder
                loaded = joblib.load(self.model_path)
                if isinstance(loaded, tuple) and len(loaded) == 3:
                    self.model, self.scaler, self.le = loaded
                elif isinstance(loaded, tuple) and len(loaded) == 2:
                    # Compatibilidad con versiones anteriores
                    self.model, self.scaler = loaded
                    # Crear y ajustar un nuevo LabelEncoder
                    data = self.generar_datos_ejemplo()
                    self.le.fit(data['perfil'])
                    # Guardar con el LabelEncoder incluido
                    joblib.dump((self.model, self.scaler, self.le), self.model_path)
                else:
                    # Si solo está el modelo, crear desde cero
                    self.crear_nuevo_modelo()
            except Exception as e:
                print(f"Error al cargar el modelo: {e}")
                self.crear_nuevo_modelo()
        else:
            self.crear_nuevo_modelo()
    
    def crear_nuevo_modelo(self):
        """Crea y entrena un nuevo modelo desde cero"""
        # Generar datos de ejemplo
        data = self.generar_datos_ejemplo()
        
        # IMPORTANTE: Primero ajustar el LabelEncoder con las clases
        self.le.fit(data['perfil'])
        
        # Codificar la variable objetivo
        y = self.le.transform(data['perfil'])
        X = data.drop('perfil', axis=1)
        
        # Normalizar características
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Entrenar el modelo (usamos RandomForest para mejor rendimiento)
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            random_state=42,
            class_weight='balanced'
        )
        self.model.fit(X_scaled, y)
        
        # Guardar el modelo, el scaler Y el label encoder
        joblib.dump((self.model, self.scaler, self.le), self.model_path)
        
        # Guardar las medias para imputación
        self.means_ = X.mean()
    
    def predecir_perfil(self, datos_usuario):
        """Predice el perfil del inversor con análisis detallado"""
        # Asegurarse de que todos los campos necesarios estén presentes
        campos_requeridos = [
            'edad', 'horizonte', 'tolerancia', 'ingresos', 'ahorro_porcentaje',
            'experiencia', 'patrimonio_actual', 'nivel_educacion', 'objetivos',
            'conocimiento_financiero', 'capacidad_endeudamiento'
        ]
        
        # Crear DataFrame con valores predeterminados si faltan
        datos_completos = {campo: datos_usuario.get(campo, 0) for campo in campos_requeridos}
        df_usuario = pd.DataFrame([datos_completos])
        
        try:
            # Normalizar los datos
            X_scaled = self.scaler.transform(df_usuario)
            
            # Predecir
            codigo_perfil = self.model.predict(X_scaled)[0]
            perfil = self.le.inverse_transform([codigo_perfil])[0]
            
            # Obtener probabilidades
            probabilidades = self.model.predict_proba(X_scaled)[0]
            confianza = max(probabilidades) * 100
            
            # Obtener importancia de características
            importancias = dict(zip(
                campos_requeridos,
                self.model.feature_importances_
            ))
            
            # Generar recomendaciones
            recomendaciones = self.generar_recomendaciones(perfil, datos_usuario)
            
            return {
                'perfil': perfil,
                'confianza': round(confianza, 1),
                'importancias': importancias,
                'tasa_sugerida': self.obtener_tasa_sugerida(perfil),
                'recomendaciones': recomendaciones,
                'distribucion_activos': self.obtener_distribucion_activos(perfil),
                'proyecciones': self.generar_proyecciones(perfil, datos_usuario)
            }
            
        except Exception as e:
            print(f"Error en la predicción: {e}")
            import traceback
            traceback.print_exc()
            # Retornar valores por defecto en caso de error
            return {
                'perfil': 'moderado',
                'confianza': 0,
                'importancias': {},
                'tasa_sugerida': {'min': 4.0, 'max': 9.0, 'media': 6.5},
                'recomendaciones': [],
                'distribucion_activos': {},
                'proyecciones': {}
            }
    
    @staticmethod
    def obtener_tasa_sugerida(perfil):
        """Devuelve la tasa de retorno sugerida según el perfil"""
        tasas = {
            'conservador': {
                'min': 2.0,
                'max': 5.0,
                'media': 3.5
            },
            'moderado': {
                'min': 4.0,
                'max': 9.0,
                'media': 6.5
            },
            'agresivo': {
                'min': 7.0,
                'max': 15.0,
                'media': 11.0
            }
        }
        return tasas.get(perfil.lower(), {
            'min': 3.0,
            'max': 8.0,
            'media': 5.5
        })

    @staticmethod
    def get_descripcion_perfil(perfil):
        """Devuelve una descripción detallada del perfil"""
        descripciones = {
            'conservador': {
                'descripcion': '''
                ## 🛡️ Perfil Conservador
                **Enfoque principal:** Preservación del capital y bajo riesgo
                **Horizonte típico:** Corto a mediano plazo (1-5 años)
                **Tolerancia al riesgo:** Baja
                **Objetivo:** Proteger el capital, con rendimientos que superen ligeramente la inflación
                ''',
                'caracteristicas': [
                    "Prefiere estabilidad sobre altos rendimientos",
                    "Inversiones principalmente en instrumentos de deuda gubernamental",
                    "Baja exposición a la volatilidad del mercado",
                    "Liquidez alta para emergencias",
                    "Pérdidas potenciales mínimas"
                ]
            },
            'moderado': {
                'descripcion': '''
                ## ⚖️ Perfil Moderado
                **Enfoque principal:** Equilibrio entre riesgo y rendimiento
                **Horizonte típico:** Mediano a largo plazo (5-15 años)
                **Tolerancia al riesgo:** Media
                **Objetivo:** Crecimiento constante del capital con riesgo controlado
                ''',
                'caracteristicas': [
                    "Busca equilibrio entre rentabilidad y seguridad",
                    "Cartera diversificada entre renta fija y variable",
                    "Tolera cierta volatilidad a cambio de mejores rendimientos",
                    "Objetivos financieros a mediano plazo",
                    "Exposición moderada a mercados internacionales"
                ]
            },
            'agresivo': {
                'descripcion': '''
                ## 🚀 Perfil Agresivo
                **Enfoque principal:** Máximo crecimiento del capital
                **Horizonte típico:** Largo plazo (15+ años)
                **Tolerancia al riesgo:** Alta
                **Objetivo:** Maximizar rendimientos asumiendo mayor volatilidad
                ''',
                'caracteristicas': [
                    "Enfocado en crecimiento a largo plazo",
                    "Alta exposición a renta variable y activos de riesgo",
                    "Tolera alta volatilidad",
                    "Objetivos financieros ambiciosos",
                    "Diversificación global y en diferentes clases de activos"
                ]
            }
        }
        
        perfil_data = descripciones.get(perfil.lower(), {
            'descripcion': 'Perfil no reconocido',
            'caracteristicas': []
        })
        
        # Formatear la salida
        output = perfil_data['descripcion'] + "\n**Características principales:**\n"
        for caracteristica in perfil_data['caracteristicas']:
            output += f"- {caracteristica}\n"
            
        return output
        
    @staticmethod
    def obtener_distribucion_activos(perfil):
        """Devuelve la distribución de activos recomendada según el perfil"""
        distribuciones = {
            'conservador': {
                'Bonos del Gobierno': 60,
                'Depósitos a Plazo': 20,
                'Acciones Blue Chips': 15,
                'Fondos de Inversión': 5,
                'Descripción': 'Distribución conservadora enfocada en preservar el capital con bajo riesgo.'
            },
            'moderado': {
                'Bonos Corporativos': 40,
                'Acciones Blue Chips': 35,
                'Fondos Indexados': 15,
                'Materias Primas': 5,
                'Efectivo': 5,
                'Descripción': 'Distribución equilibrada entre renta fija y variable para crecimiento moderado.'
            },
            'agresivo': {
                'Acciones de Crecimiento': 60,
                'ETFs Especulativos': 20,
                'Criptomonedas': 10,
                'Startups': 5,
                'Materias Primas': 5,
                'Descripción': 'Distribución agresiva enfocada en máximo crecimiento a largo plazo con alta volatilidad.'
            }
        }
        
        return distribuciones.get(perfil.lower(), {
            'Bonos': 40,
            'Acciones': 40,
            'Efectivo': 10,
            'Otros': 10,
            'Descripción': 'Distribución genérica para perfiles no identificados.'
        })
    
    def generar_recomendaciones(self, perfil, datos_usuario):
        """Genera recomendaciones personalizadas basadas en el perfil"""
        edad = datos_usuario.get('edad', 30)
        horizonte = datos_usuario.get('horizonte', 10)
        
        recomendaciones_base = {
            'conservador': [
                {
                    'titulo': 'Estrategia de Inversión',
                    'contenido': 'Enfoque en preservación de capital con bajo riesgo',
                    'acciones': [
                        'Mantén al menos el 60% en activos de renta fija',
                        'Considera bonos del gobierno y corporativos de alta calificación',
                        'Mantén un fondo de emergencia equivalente a 6-12 meses de gastos'
                    ]
                },
                {
                    'titulo': 'Gestión de Riesgo',
                    'contenido': 'Minimizar la exposición a la volatilidad del mercado',
                    'acciones': [
                        'Evita inversiones especulativas',
                        'Diversifica entre diferentes emisores de deuda',
                        'Considera seguros de inversión para proteger tu capital'
                    ]
                }
            ],
            'moderado': [
                {
                    'titulo': 'Estrategia de Inversión',
                    'contenido': 'Equilibrio entre crecimiento y estabilidad',
                    'acciones': [
                        'Mantén una mezcla equilibrada entre renta fija y variable',
                        'Considera fondos indexados para exposición diversificada',
                        'Revisa y rebalancea tu cartera cada 6-12 meses'
                    ]
                },
                {
                    'titulo': 'Crecimiento a Largo Plazo',
                    'contenido': 'Construir riqueza de manera constante',
                    'acciones': [
                        'Aprovecha el interés compuesto con contribuciones regulares',
                        'Considera planes de reinversión de dividendos',
                        'Explora mercados emergentes para mayor diversificación'
                    ]
                }
            ],
            'agresivo': [
                {
                    'titulo': 'Estrategia de Inversión',
                    'contenido': 'Máximo crecimiento con alta tolerancia al riesgo',
                    'acciones': [
                        'Enfócate en acciones de crecimiento y sectores innovadores',
                        'Considera pequeñas y medianas empresas con alto potencial',
                        'Mantén una porción pequeña en activos alternativos como criptomonedas'
                    ]
                },
                {
                    'titulo': 'Gestión de Riesgo',
                    'contenido': 'Manejo de la volatilidad en mercados agresivos',
                    'acciones': [
                        'Establece órdenes de stop-loss para limitar pérdidas',
                        'Mantén un horizonte de inversión a largo plazo (10+ años)',
                        'Considera estrategias de cobertura para protegerte de caídas del mercado'
                    ]
                }
            ]
        }
        
        # Añadir recomendaciones basadas en la edad
        recomendaciones_edad = []
        if edad < 30:
            recomendaciones_edad = [
                'Aprovecha el tiempo a tu favor con inversiones de mayor riesgo',
                'Considera destinar una porción a educación financiera continua'
            ]
        elif edad > 50:
            recomendaciones_edad = [
                'Considera reducir gradualmente la exposición a activos de mayor riesgo',
                'Evalúa opciones de ingresos pasivos para la jubilación'
            ]
            
        # Añadir recomendaciones basadas en el horizonte
        recomendaciones_horizonte = []
        if horizonte < 5:
            recomendaciones_horizonte = [
                'Enfoque en preservación de capital y liquidez',
                'Considera instrumentos de corto plazo como certificados de depósito'
            ]
        
        # Combinar todas las recomendaciones
        recomendaciones = recomendaciones_base.get(perfil.lower(), [])
        
        if recomendaciones_edad:
            recomendaciones.append({
                'titulo': 'Recomendaciones por Edad',
                'contenido': 'Ajustes sugeridos basados en tu etapa de vida',
                'acciones': recomendaciones_edad
            })
            
        if recomendaciones_horizonte:
            recomendaciones.append({
                'titulo': 'Consideraciones de Plazo',
                'contenido': 'Recomendaciones para tu horizonte de inversión',
                'acciones': recomendaciones_horizonte
            })
            
        return recomendaciones
    
    def generar_proyecciones(self, perfil, datos_usuario):
        """Genera proyecciones de patrimonio a largo plazo"""
        edad_actual = datos_usuario.get('edad', 30)
        horizonte = datos_usuario.get('horizonte', 20)
        patrimonio_actual = datos_usuario.get('patrimonio_actual', 0)
        ahorro_porcentaje = datos_usuario.get('ahorro_porcentaje', 20) / 100  # Convertir a decimal
        ahorro_mensual = (datos_usuario.get('ingresos', 0) * ahorro_porcentaje)
        
        # Tasas de retorno esperadas por perfil (anuales)
        tasas = {
            'conservador': 0.04,
            'moderado': 0.07,
            'agresivo': 0.10
        }
        
        # Generar proyecciones para diferentes perfiles
        proyecciones = {}
        for perfil_proy, tasa in tasas.items():
            años = list(range(0, min(horizonte, 40) + 1, 5))  # Cada 5 años, máximo 40
            if 0 not in años:
                años.insert(0, 0)  # Asegurar que empiece en 0
            
            saldos = []
            
            for año in años:
                # Calcular el saldo acumulado hasta ese año
                saldo = patrimonio_actual
                for a in range(año):
                    saldo = saldo * (1 + tasa) + (ahorro_mensual * 12)
                saldos.append(max(0, saldo))
            
            proyecciones[perfil_proy] = {
                'años': [edad_actual + a for a in años],
                'saldos': saldos,
                'rango': f"{tasa*100:.1f}% anual"
            }
        
        return proyecciones
