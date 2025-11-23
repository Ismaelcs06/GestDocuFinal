# reportes/urls.py
from django.urls import path
from . import views

app_name = "reportes"

urlpatterns = [
    path("", views.report_builder, name="builder"),
    path("export/html/", views.report_export_html, name="export_html"),
    path("export/xlsx/", views.report_export_xlsx, name="export_xlsx"),
    path("export/pdf/", views.report_export_pdf, name="export_pdf"),
]
