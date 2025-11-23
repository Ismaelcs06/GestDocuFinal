# reportes/forms.py
from django import forms
from documentos.models import TipoDocumento

COLUMNAS_MODELOS = {
    "caso": [
        ("nroCaso", "Nro de Caso"),
        ("tipoCaso", "Tipo de Caso"),
        ("estado", "Estado"),
        ("prioridad", "Prioridad"),
        ("fechaInicio", "Fecha de Inicio"),
        ("fechaFin", "Fecha de Fin"),
    ],
    "documento": [
        ("nombreDocumento", "Nombre del Documento"),
        ("tipoDocumento__nombre", "Tipo de Documento"),
        ("estado", "Estado"),
        ("fechaDoc", "Fecha del Documento"),
        ("carpeta__nombre", "Carpeta"),
        ("carpeta__expediente__nroExpediente", "Nro Expediente"),
    ],
}


class ReportBuilderForm(forms.Form):
    MODELOS = [
        ("caso", "Casos"),
        ("documento", "Documentos"),
    ]

    modelo = forms.ChoiceField(choices=MODELOS, label="Tipo de reporte")
    filtros = forms.CharField(required=False, label="Buscar (texto libre)")
    columnas = forms.MultipleChoiceField(
        choices=[], widget=forms.CheckboxSelectMultiple, label="Columnas a mostrar"
    )

    # 🔹 Filtros adicionales
    estado = forms.ChoiceField(
        required=False,
        label="Estado",
        choices=[
            ("", "Todos"),
            ("ABIERTO", "Abierto"),
            ("CERRADO", "Cerrado"),
            ("ACTIVO", "Activo"),
            ("INACTIVO", "Inactivo"),
        ],
    )
    prioridad = forms.ChoiceField(
        required=False,
        label="Prioridad",
        choices=[
            ("", "Todas"),
            ("ALTA", "Alta"),
            ("MEDIA", "Media"),
            ("BAJA", "Baja"),
        ],
    )
    tipo_doc = forms.ModelChoiceField(
        required=False,
        queryset=TipoDocumento.objects.filter(activo=True),
        label="Tipo de Documento",
    )
    fecha_desde = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    fecha_hasta = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        modelo = self.data.get("modelo") or self.initial.get("modelo") or "caso"

        # Cambiar columnas dinámicamente
        if modelo in COLUMNAS_MODELOS:
            self.fields["columnas"].choices = COLUMNAS_MODELOS[modelo]

        # Esconder o mostrar campos dependiendo del modelo
        if modelo == "caso":
            self.fields["tipo_doc"].widget = forms.HiddenInput()
        elif modelo == "documento":
            self.fields["prioridad"].widget = forms.HiddenInput()
