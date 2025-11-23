# accounts/forms.py
from django import forms
from seguridad.models import Usuario, Rol, UsuarioRol
from actores.models import Actor, Abogado, Cliente, Asistente


class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Contraseña"})
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirmar contraseña"})
    )

    class Meta:
        model = Usuario
        fields = ["username", "email", "estado", "estadoCuenta"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de usuario"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Correo electrónico"}),
            "estado": forms.TextInput(attrs={"class": "form-control"}),
            "estadoCuenta": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    
    
    # FORMULARIO PARA CREAR ROLES Y GESTIONARLOS
    
class RoleForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = ["nombre", "descripcion"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


class RoleAssignForm(forms.Form):
    roles = forms.ModelMultipleChoiceField(
        queryset=Rol.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop("usuario", None)
        super().__init__(*args, **kwargs)
        if usuario:
            actuales = Rol.objects.filter(usuariorol__usuario=usuario)
            self.fields["roles"].initial = actuales
            
            
    # FORMULARIOS PARA LA GESTION DE LOS ACTORES y CLASES CON GENERALIZACION 
    
class ActorForm(forms.ModelForm):
    class Meta:
        model = Actor
        fields = [
            "tipoActor", "nombres", "apellidoPaterno", "apellidoMaterno",
            "ci", "telefono", "direccion", "estadoActor"
        ]
        widgets = {
            "tipoActor": forms.Select(attrs={"class": "form-control"}),
            "nombres": forms.TextInput(attrs={"class": "form-control"}),
            "apellidoPaterno": forms.TextInput(attrs={"class": "form-control"}),
            "apellidoMaterno": forms.TextInput(attrs={"class": "form-control"}),
            "ci": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "estadoActor": forms.Select(attrs={"class": "form-control"}),
        }
        
class AbogadoForm(forms.ModelForm):
    class Meta:
        model = Abogado
        fields = ["nroCredencial", "especialidad", "estadoLicencia"]
        widgets = {
            "nroCredencial": forms.TextInput(attrs={"class": "form-control"}),
            "especialidad": forms.TextInput(attrs={"class": "form-control"}),
            "estadoLicencia": forms.TextInput(attrs={"class": "form-control"}),
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["tipoCliente", "observaciones"]
        widgets = {
            "tipoCliente": forms.Select(attrs={"class": "form-control"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

class AsistenteForm(forms.ModelForm):
    class Meta:
        model = Asistente
        fields = ["area", "cargo"]
        widgets = {
            "area": forms.TextInput(attrs={"class": "form-control"}),
            "cargo": forms.TextInput(attrs={"class": "form-control"}),
        }