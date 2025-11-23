# reportes/utils.py
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def queryset_to_xlsx(rows, columns, filename_prefix="reporte"):
    try:
        import pandas as pd
    except ImportError:
        import csv
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in columns})
        csv_bytes = output.getvalue().encode("utf-8-sig")
        return csv_bytes, f"{filename_prefix}_{datetime.now():%Y%m%d_%H%M%S}.csv"

    df = pd.DataFrame(rows, columns=columns)
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Reporte", index=False)
    bio.seek(0)
    return bio.getvalue(), f"{filename_prefix}_{datetime.now():%Y%m%d_%H%M%S}.xlsx"


def render_pdf_from_html(html, filename_prefix="reporte", columns=None, data=None):
    """
    Genera un PDF con tabla de datos (simple, sin WeasyPrint).
    columns: lista de nombres de columnas
    data: lista de diccionarios con los datos
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    story = []

    # Título
    story.append(Paragraph(f"{filename_prefix.capitalize()} - Exportación PDF", styles["Title"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Este reporte fue generado automáticamente desde GestDocu.", styles["Normal"]))
    story.append(Spacer(1, 15))

    # Si hay datos estructurados, dibujar tabla
    if columns and data:
        # Encabezado + filas
        table_data = [columns]
        for row in data:
            table_data.append([str(row.get(col, "")) for col in columns])

        # Tabla
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
        ]))
        story.append(table)
    else:
        # Si no hay datos estructurados, mostrar texto plano
        story.append(Paragraph("No hay datos disponibles o no se definieron columnas.", styles["Italic"]))

    doc.build(story)
    pdf_value = buffer.getvalue()
    buffer.close()

    filename = f"{filename_prefix}_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    return pdf_value, filename