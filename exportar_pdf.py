from fpdf import FPDF
import pandas as pd

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Reporte de Simulación de Jubilación', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

        

def crear_reporte_jubilacion(df_crecimiento, capital_final, total_aportado, df_escenarios: pd.DataFrame = None):
    """Crea un PDF con los resultados del Módulo A y comparaciones de escenarios (opcional)."""
    
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    
    # 1. Resumen
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Resumen de la Proyección', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f'Capital Final Acumulado: ${capital_final:,.2f}', 0, 1)
    pdf.cell(0, 8, f'Total Aportado: ${total_aportado:,.2f}', 0, 1)
    pdf.cell(0, 8, f'Ganancia (Intereses): ${(capital_final - total_aportado):,.2f}', 0, 1)
    
    pdf.ln(10) # Salto de línea
    
    # 2. Tabla de Crecimiento
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Detalle del Crecimiento Por Periodos', 0, 1)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(25, 8, 'Periodo', 1)
    pdf.cell(50, 8, 'Saldo Inicial', 1)
    pdf.cell(40, 8, 'Aporte', 1)
    pdf.cell(40, 8, 'Interés', 1)
    pdf.cell(40, 8, 'Saldo Final', 1, 1)
    
    pdf.set_font('Arial', '', 9)
    for i, row in df_crecimiento.iterrows():  # Solo primeras 20 filas
        pdf.cell(25, 6, str(row['Periodo']), 1)
        pdf.cell(50, 6, f"${row['Saldo Inicial']:,.2f}", 1)
        pdf.cell(40, 6, f"${row['Aporte']:,.2f}", 1)
        pdf.cell(40, 6, f"${row['Interés Ganado']:,.2f}", 1)
        pdf.cell(40, 6, f"${row['Saldo Final']:,.2f}", 1, 1)
    
    # 3. Escenarios de Jubilación (opcional)
    if df_escenarios is not None and not df_escenarios.empty:
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Comparación de Escenarios de Jubilación', 0, 1)
        
        pdf.set_font('Arial', 'B', 10)
        col_widths = [50, 50, 50]
        headers = ["Tasa TEA Retiro (%)", "Años de Pensión", "Pensión Mensual (USD)"]
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 7, h, 1, 0, 'C')
        pdf.ln()
        
        pdf.set_font('Arial', '', 9)
        for _, row in df_escenarios.iterrows():
            pdf.cell(col_widths[0], 6, f"{row['Tasa TEA Retiro (%)']:.2f}", 1)
            pdf.cell(col_widths[1], 6, str(int(row['Años de Pensión'])), 1)
            pdf.cell(col_widths[2], 6, f"${row['Pensión Mensual (USD)']:,.2f}", 1)
            pdf.ln()
    
    return bytes(pdf.output(dest='S'))


