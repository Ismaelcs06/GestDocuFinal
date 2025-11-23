from django import forms
from .models import Documento, VersionDocumento, TipoDocumento, EtapaProcesal
from django.shortcuts import render, redirect

# ==========================
# FORMULARIO DE DOCUMENTOS
# ==========================
class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = [
            "carpeta", "tipoDocumento", "etapaProcesal",
            "nombreDocumento", "rutaDocumento",
            "estado", "palabraClave", "fechaDoc"
        ]
        widgets = {
            "carpeta": forms.Select(attrs={"class": "form-control"}),
            "tipoDocumento": forms.Select(attrs={"class": "form-control"}),
            "etapaProcesal": forms.Select(attrs={"class": "form-control"}),
            "nombreDocumento": forms.TextInput(attrs={"class": "form-control"}),
            "rutaDocumento": forms.ClearableFileInput(attrs={"class": "form-control"}), 
            "estado": forms.Select(choices=[
                ("ACTIVO", "Activo"),
                ("INACTIVO", "Inactivo"),
            ], attrs={"class": "form-control"}),
            "palabraClave": forms.TextInput(attrs={"class": "form-control"}),
            "fechaDoc": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }


# ==========================
# FORMULARIO DE VERSIONES
# ==========================
class VersionDocumentoForm(forms.ModelForm):
    class Meta:
        model = VersionDocumento
        fields = ["rutaArchivo", "comentario"]
        widgets = {
            "rutaArchivo": forms.ClearableFileInput(attrs={"class": "form-control"}),  
            "comentario": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


# ==========================
# FORMULARIOS DE CONFIGURACIÓN
# ==========================
class TipoDocumentoForm(forms.ModelForm):
    class Meta:
        model = TipoDocumento
        fields = ["nombre", "descripcion", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del tipo"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class EtapaProcesalForm(forms.ModelForm):
    class Meta:
        model = EtapaProcesal
        fields = ["nombre", "descripcion", "estado"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de la etapa"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "estado": forms.Select(
                choices=[("ACTIVO", "Activo"), ("INACTIVO", "Inactivo")],
                attrs={"class": "form-control"}
            ),
        }