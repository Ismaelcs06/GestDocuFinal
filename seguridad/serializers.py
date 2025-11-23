from rest_framework import serializers
from .models import Usuario
from actores.serializers import ActorSerializer
from rest_framework import serializers
#login
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
#end
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'estado', 'estadoCuenta', 'creadoEn', 'actualizadoEn']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Evitamos campos anidados, solo representamos el nombre de usuario
        return representation

from .models import Rol

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Evitamos campos anidados, solo representamos el nombre del rol
        return representation

from .models import Permiso

class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = ['id', 'descripcion', 'accion']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Evitamos campos anidados, solo representamos la descripción y la acción
        return representation

from .models import UsuarioRol

class UsuarioRolSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioRol
        fields = ['id', 'usuario', 'rol', 'fechaAsignacion']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Evitamos campos anidados, solo representamos el usuario y el rol como texto
        representation['usuario'] = instance.usuario.username  # Solo el nombre de usuario
        representation['rol'] = instance.rol.nombre  # Solo el nombre del rol
        return representation

from .models import RolPermiso

class RolPermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolPermiso
        fields = ['id', 'rol', 'permiso', 'estado']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Evitamos campos anidados, solo representamos el rol y el permiso como texto
        representation['rol'] = instance.rol.nombre  # Solo el nombre del rol
        representation['permiso'] = instance.permiso.accion  # Solo la acción del permiso
        return representation
from rest_framework import serializers
from .models import Bitacora

class BitacoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bitacora
        fields = ['id', 'login', 'ip', 'userAgent', 'fecha', 'login_at', 'logout_at', 'device', 'idUsuario']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Evitamos campos anidados, solo representamos el idUsuario como texto
        representation['idUsuario'] = instance.idUsuario.username  # Solo el nombre de usuario
        return representation
from rest_framework import serializers
from .models import DetalleBitacora

class DetalleBitacoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleBitacora
        fields = ['id', 'idBitacora', 'accion', 'fecha', 'tabla', 'detalle']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Evitamos campos anidados, solo representamos el idBitacora como texto
        representation['idBitacora'] = instance.idBitacora.id  # Solo el ID de la bitácora
        return representation
class MyTokenPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):#@
        username=attrs.get(self.username_field) or attrs.get('username')
        password=attrs.get('password')
        User=get_user_model()
        user=User.objects.filter(username=username).first()
        print(user)
        if not user:
            raise AuthenticationFailed('el usuario no existe')
        if not user.check_password(password):
            raise AuthenticationFailed('ingrese su contrase;a correctemetn')
        
            
        return super().validate(attrs)
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    def save(self, **kwargs):
        RefreshToken(self.token).blacklist()
class UsuarioMeSerializer(serializers.ModelSerializer):
    """
    Serializador exclusivo para el endpoint '/usuarios/me/'.
    """
    actor = ActorSerializer(read_only=True) 

    class Meta:
        model = Usuario
        fields = [
        'id',
            'actor',  # Incluye detalles del Actor
        ]