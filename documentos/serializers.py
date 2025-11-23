from rest_framework import serializers
from .models import TipoDocumento

class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = ['id', 'nombre', 'descripcion', 'activo']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Evitamos campos anidados, solo representamos el nombre del tipo de documento
        return representation

from .models import EtapaProcesal

class EtapaProcesalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtapaProcesal
        fields = ['id', 'nombre', 'descripcion', 'estado']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Evitamos campos anidados, solo representamos el nombre de la etapa procesal
        return representation

from .models import Documento

class DocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = ['id', 'carpeta', 'tipoDocumento', 'etapaProcesal', 'nombreDocumento', 'rutaDocumento', 'tamano', 'estado', 'palabraClave', 'fechaDoc', 'creadoEn', 'actualizadoEn']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Evitamos campos anidados, solo representamos la carpeta, tipo de documento y etapa procesal como texto
        representation['carpeta'] = instance.carpeta.nombre  # solo nombre de la carpeta
        representation['tipoDocumento'] = instance.tipoDocumento.nombre  # solo nombre del tipo de documento
        representation['etapaProcesal'] = instance.etapaProcesal.nombre if instance.etapaProcesal else None  # nombre de la etapa procesal
        return representation

from .models import VersionDocumento

class VersionDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VersionDocumento
        fields = ['id', 'documento', 'usuario', 'numeroVersion', 'rutaArchivo', 'fechaCambio', 'comentario']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Evitamos campos anidados, solo representamos el documento y el usuario como texto
        representation['documento'] = instance.documento.nombreDocumento  # nombre del documento
        representation['usuario'] = instance.usuario.username  # nombre de usuario
        return representation
