# reportes/views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from django.utils.http import urlencode
from casos.models import Caso
from documentos.models import Documento
from .forms import ReportBuilderForm
from .utils import queryset_to_xlsx, render_pdf_from_html
from django.template.loader import render_to_string

# =====================================================================
#  FUNCIÓN AUXILIAR: Construir el queryset según modelo y filtros
# =====================================================================
def _build_queryset(modelo, filtros, extra):
    """
    Devuelve un queryset filtrado dinámicamente según el modelo y criterios extra.
    """
    if modelo == "caso":
        qs = Caso.objects.all()
        if filtros:
            qs = qs.filter(
                Q(nroCaso__icontains=filtros)
                | Q(tipoCaso__icontains=filtros)
                | Q(descripcion__icontains=filtros)
            )
        if extra.get("estado"):
            qs = qs.filter(estado=extra["estado"])
        if extra.get("prioridad"):
            qs = qs.filter(prioridad=extra["prioridad"])
        if extra.get("fecha_desde"):
            qs = qs.filter(fechaInicio__gte=extra["fecha_desde"])
        if extra.get("fecha_hasta"):
            qs = qs.filter(fechaInicio__lte=extra["fecha_hasta"])
        return qs

    elif modelo == "documento":
        qs = Documento.objects.select_related("tipoDocumento", "carpeta", "carpeta__expediente")
        if filtros:
            qs = qs.filter(
                Q(nombreDocumento__icontains=filtros)
                | Q(tipoDocumento__nombre__icontains=filtros)
                | Q(palabraClave__icontains=filtros)
            )
        if extra.get("estado"):
            qs = qs.filter(estado=extra["estado"])
        if extra.get("tipo_doc"):
            qs = qs.filter(tipoDocumento=extra["tipo_doc"])
        if extra.get("fecha_desde"):
            qs = qs.filter(fechaDoc__gte=extra["fecha_desde"])
        if extra.get("fecha_hasta"):
            qs = qs.filter(fechaDoc__lte=extra["fecha_hasta"])
        return qs

    return None


# =====================================================================
#  VISTA PRINCIPAL: Construcción y vista previa del reporte
# =====================================================================
def report_builder(request):
    """
    Vista principal del generador de reportes dinámicos.
    """
    data = columns = modelo = None
    form = ReportBuilderForm(request.GET or None)

    if form.is_valid():
        modelo = form.cleaned_data["modelo"]
        columnas = form.cleaned_data["columnas"]
        filtros = form.cleaned_data.get("filtros", "")
        ordenar_por = form.cleaned_data.get("ordenar_por")
        orden = form.cleaned_data.get("orden", "asc")

        # 🔹 Nueva llamada con parámetros extra
        qs = _build_queryset(
            modelo,
            filtros,
            {
                "estado": form.cleaned_data.get("estado"),
                "prioridad": form.cleaned_data.get("prioridad"),
                "tipo_doc": form.cleaned_data.get("tipo_doc"),
                "fecha_desde": form.cleaned_data.get("fecha_desde"),
                "fecha_hasta": form.cleaned_data.get("fecha_hasta"),
            },
        )

        if qs is not None and columnas:
            if ordenar_por:
                orden_expr = ordenar_por if orden == "asc" else f"-{ordenar_por}"
                qs = qs.order_by(orden_expr)

            # Convertimos a lista de diccionarios (para tabla y exportaciones)
            data = list(qs.values(*columnas))
            columns = columnas

    # Mantener los filtros actuales para exportar con mismos criterios
    current_qs = urlencode(request.GET, doseq=True)

    return render(
        request,
        "reportes/report_builder.html",
        {
            "form": form,
            "data": data,
            "columns": columns or [],
            "modelo": modelo,
            "export_query": current_qs,
        },
    )


# =====================================================================
#  EXPORTACIÓN HTML
# =====================================================================
def report_export_html(request):
    """
    Exporta el reporte actual en formato HTML limpio.
    """
    form = ReportBuilderForm(request.GET or None)
    if not form.is_valid():
        return HttpResponse("Parámetros inválidos", status=400)

    modelo = form.cleaned_data["modelo"]
    columnas = form.cleaned_data["columnas"]
    filtros = form.cleaned_data.get("filtros", "")
    ordenar_por = form.cleaned_data.get("ordenar_por")
    orden = form.cleaned_data.get("orden", "asc")

    qs = _build_queryset(
        modelo,
        filtros,
        {
            "estado": form.cleaned_data.get("estado"),
            "prioridad": form.cleaned_data.get("prioridad"),
            "tipo_doc": form.cleaned_data.get("tipo_doc"),
            "fecha_desde": form.cleaned_data.get("fecha_desde"),
            "fecha_hasta": form.cleaned_data.get("fecha_hasta"),
        },
    )

    if ordenar_por:
        qs = qs.order_by(ordenar_por if orden == "asc" else f"-{ordenar_por}")

    data = list(qs.values(*columnas))

    return render(
        request,
        "reportes/report_result.html",
        {
            "columns": columnas,
            "data": data,
            "titulo": f"Reporte de {modelo.capitalize()}",
        },
    )


# =====================================================================
#  EXPORTACIÓN EXCEL
# =====================================================================
def report_export_xlsx(request):
    """
    Exporta el reporte actual en formato Excel (.xlsx).
    """
    form = ReportBuilderForm(request.GET or None)
    if not form.is_valid():
        return HttpResponse("Parámetros inválidos", status=400)

    modelo = form.cleaned_data["modelo"]
    columnas = form.cleaned_data["columnas"]
    filtros = form.cleaned_data.get("filtros", "")
    ordenar_por = form.cleaned_data.get("ordenar_por")
    orden = form.cleaned_data.get("orden", "asc")

    qs = _build_queryset(
        modelo,
        filtros,
        {
            "estado": form.cleaned_data.get("estado"),
            "prioridad": form.cleaned_data.get("prioridad"),
            "tipo_doc": form.cleaned_data.get("tipo_doc"),
            "fecha_desde": form.cleaned_data.get("fecha_desde"),
            "fecha_hasta": form.cleaned_data.get("fecha_hasta"),
        },
    )

    if ordenar_por:
        qs = qs.order_by(ordenar_por if orden == "asc" else f"-{ordenar_por}")

    data = list(qs.values(*columnas))
    xlsx_bytes, filename = queryset_to_xlsx(data, columnas, filename_prefix=f"reporte_{modelo}")

    response = HttpResponse(
        xlsx_bytes,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


# =====================================================================
#  EXPORTACIÓN PDF
# =====================================================================
def report_export_pdf(request):
    form = ReportBuilderForm(request.GET or None)
    if not form.is_valid():
        return HttpResponse("Parámetros inválidos", status=400)

    modelo = form.cleaned_data["modelo"]
    columnas = form.cleaned_data["columnas"]
    filtros = form.cleaned_data.get("filtros")

    ordenar_por = form.cleaned_data.get("ordenar_por")
    orden = form.cleaned_data.get("orden")

    extras = {
        "estado": form.cleaned_data.get("estado"),
        "prioridad": form.cleaned_data.get("prioridad"),
        "tipo_doc": form.cleaned_data.get("tipo_doc"),
        "fecha_desde": form.cleaned_data.get("fecha_desde"),
        "fecha_hasta": form.cleaned_data.get("fecha_hasta"),
    }

    qs = _build_queryset(modelo, filtros, extras)
    if ordenar_por:
        qs = qs.order_by(ordenar_por if orden == "asc" else f"-{ordenar_por}")
    data = list(qs.values(*columnas))

    # Render HTML del reporte (aunque no lo uses visualmente)
    from django.template.loader import render_to_string
    html = render_to_string("reportes/report_pdf.html", {
        "columns": columnas,
        "data": data,
        "titulo": f"Reporte de {modelo.capitalize()}",
    })

    # 🔹 Usar la versión de ReportLab simple
    pdf_bytes, filename = render_pdf_from_html(
        html,
        filename_prefix=f"reporte_{modelo}",
        columns=columnas,
         data=data
)


    # Si algo falla, mostrar el HTML
    if pdf_bytes is None:
        return render(request, "reportes/report_result.html", {
            "columns": columnas,
            "data": data,
            "titulo": f"Reporte de {modelo.capitalize()} (Imprime como PDF desde tu navegador)",
        })

    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp
