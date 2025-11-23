from django import forms
from .models import Caso,EquipoCaso,ParteProcesal,Expediente,Carpeta

class CasoForm(forms.ModelForm):
    class Meta:
        model = Caso
        fields = ["nroCaso", "tipoCaso", "descripcion", "estado", "prioridad", "fechaInicio", "fechaFin"]
        widgets = {
            "nroCaso": forms.TextInput(attrs={"class": "form-control"}),
            "tipoCaso": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "estado": forms.Select(choices=[
                ("ABIERTO", "Abierto"),
                ("CERRADO", "Cerrado"),
            ], attrs={"class": "form-control"}),
            "prioridad": forms.Select(choices=[
                ("ALTA", "Alta"),
                ("MEDIA", "Media"),
                ("BAJA", "Baja"),
            ], attrs={"class": "form-control"}),
            "fechaInicio": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "fechaFin": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

class EquipoCasoForm(forms.ModelForm):
    class Meta:
        model = EquipoCaso
        fields = ["actor", "rolEnEquipo", "observaciones", "fechaAsignacion", "fechaSalida"]
        widgets = {
            "actor": forms.Select(attrs={"class": "form-control"}),
            "rolEnEquipo": forms.Select(attrs={"class": "form-control"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "fechaAsignacion": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "fechaSalida": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

class ParteProcesalForm(forms.ModelForm):
    class Meta:
        model = ParteProcesal
        fields = ["cliente", "rolProcesal", "estado", "fechaInicio", "fechaFin"]
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-control"}),
            "rolProcesal": forms.Select(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-control"}, choices=[
                ("ACTIVO", "Activo"),
                ("INACTIVO", "Inactivo"),
            ]),
            "fechaInicio": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "fechaFin": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }
        
# FORMULARIO PARA EXPEDIENTE

class ExpedienteForm(forms.ModelForm):
    class Meta:
        model = Expediente
        fields = ["nroExpediente", "estado", "fechaCreacion"]
        widgets = {
            "nroExpediente": forms.TextInput(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-control"}, choices=[
                ("ABIERTO", "Abierto"),
                ("CERRADO", "Cerrado"),
            ]),
            "fechaCreacion": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }


#FORMULARIO PARA EXPEDIENTES

class CarpetaForm(forms.ModelForm):
    class Meta:
        model = Carpeta
        fields = ["nombre", "estado", "carpetaPadre"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-control"}, choices=[
                ("ACTIVO", "Activo"),
                ("INACTIVO", "Inactivo"),
            ]),
            "carpetaPadre": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        expediente = kwargs.pop("expediente", None)
        super().__init__(*args, **kwargs)
        if expediente:
            self.fields["carpetaPadre"].queryset = Carpeta.objects.filter(expediente=expediente)
        else:
            self.fields["carpetaPadre"].queryset = Carpeta.objects.none()


