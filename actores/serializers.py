from rest_framework import serializers

from .models import Actor

class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['id', 'usuario', 'tipoActor', 'nombres', 'apellidoPaterno', 'apellidoMaterno', 'ci', 'telefono', 'direccion', 'estadoActor', 'creadoEn', 'actualizadoEn']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Aquí puedes personalizar la representación si es necesario
        # No estamos anidando campos, solo devolvemos la información directamente
        representation['usuario'] = instance.usuario.username  # Representar solo el nombre de usuario
        return representation

from .models import Abogado

class AbogadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Abogado
        fields = ['id', 'actor', 'nroCredencial', 'especialidad', 'estadoLicencia']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Evitamos campos anidados, solo representamos 'actor' con su nombre
        representation['actor'] = f"{instance.actor.nombres} {instance.actor.apellidoPaterno}"  # Representamos como texto
        return representation

from .models import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'actor', 'tipoCliente', 'observaciones']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Evitamos campos anidados, solo representamos 'actor' con su nombre
        representation['actor'] = f"{instance.actor.nombres} {instance.actor.apellidoPaterno}"  # Representamos como texto
        return representation

from .models import Asistente

class AsistenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asistente
        fields = ['id', 'actor', 'area', 'cargo']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Evitamos campos anidados, solo representamos 'actor' con su nombre
        representation['actor'] = f"{instance.actor.nombres} {instance.actor.apellidoPaterno}"  # Representamos como texto
        return representation