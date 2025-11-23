from rest_framework import serializers
from .models import Caso

class CasoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Caso
        fields = ['id', 'nroCaso', 'tipoCaso', 'descripcion', 'estado', 'prioridad', 'fechaInicio', 'fechaFin', 'creadoEn', 'actualizadoEn']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # No se anidan campos, solo se incluyen los campos relevantes
        return representation
from rest_framework import serializers
from .models import EquipoCaso

class EquipoCasoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipoCaso
        fields = ['id', 'actor', 'caso', 'rolEnEquipo', 'observaciones', 'fechaAsignacion', 'fechaSalida']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # No se anidan campos, solo representamos los valores como texto
        representation['actor'] = f"{instance.actor.nombres} {instance.actor.apellidoPaterno}"
        representation['caso'] = instance.caso.nroCaso
        return representation
from rest_framework import serializers
from .models import ParteProcesal

class ParteProcesalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParteProcesal
        fields = ['id', 'cliente', 'caso', 'rolProcesal', 'estado', 'fechaInicio', 'fechaFin']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # No se anidan campos, solo representamos los valores como texto
        representation['cliente'] = f"{instance.cliente.actor.nombres} {instance.cliente.actor.apellidoPaterno}"
        representation['caso'] = instance.caso.nroCaso
        return representation
from rest_framework import serializers
from .models import Expediente

class ExpedienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expediente
        fields = ['id', 'caso', 'nroExpediente', 'estado', 'fechaCreacion']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # No se anidan campos, solo representamos el número de caso como texto
        representation['caso'] = instance.caso.nroCaso
        return representation
from rest_framework import serializers
from .models import Carpeta

class CarpetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carpeta
        fields = ['id', 'expediente', 'nombre', 'estado', 'carpetaPadre', 'creadoEn', 'actualizadoEn']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # No se anidan campos, solo representamos el expediente como texto y la carpeta padre si existe
        representation['expediente'] = instance.expediente.nroExpediente
        if instance.carpetaPadre:
            representation['carpetaPadre'] = instance.carpetaPadre.nombre
        else:
            representation['carpetaPadre'] = None
        return representation
