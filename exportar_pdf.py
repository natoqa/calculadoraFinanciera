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

def crear_reporte_jubilacion(df_crecimiento, capital_final, total_aportado):
    """Crea un PDF con los resultados del Módulo A."""
    
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
    
    # (Aquí se podría agregar la lógica para incluir la gráfica como imagen)
    
    # 3. Tabla de Crecimiento (simplificada)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Detalle del Crecimiento (Anual)', 0, 1)
    
    # (En un reporte real, probablemente resumirías la tabla por años)
    # Por simplicidad, aquí solo mostramos algunas filas
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(25, 8, 'Periodo', 1)
    pdf.cell(50, 8, 'Saldo Inicial', 1)
    pdf.cell(40, 8, 'Aporte', 1)
    pdf.cell(40, 8, 'Interés', 1)
    pdf.cell(40, 8, 'Saldo Final', 1, 1)
    
    pdf.set_font('Arial', '', 9)
    for i, row in df_crecimiento.head(20).iterrows(): # Solo las primeras 20 filas para el ejemplo
        pdf.cell(25, 6, str(row['Periodo']), 1)
        pdf.cell(50, 6, f"${row['Saldo Inicial']:,.2f}", 1)
        pdf.cell(40, 6, f"${row['Aporte']:,.2f}", 1)
        pdf.cell(40, 6, f"${row['Interés Ganado']:,.2f}", 1)
        pdf.cell(40, 6, f"${row['Saldo Final']:,.2f}", 1, 1)

    # Retorna el PDF como bytes
    return bytes(pdf.output(dest='S'))