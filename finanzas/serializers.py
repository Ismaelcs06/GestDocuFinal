from rest_framework import serializers
from .models import Pago, Factura, ConceptoPago

class ConceptoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConceptoPago
        fields = '__all__'

class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura
        fields = '__all__'

class PagoSerializer(serializers.ModelSerializer):
    # Mostramos la factura anidada si existe
    factura = FacturaSerializer(read_only=True)
    
    # Campos de solo lectura para mostrar nombres
    nombre_concepto = serializers.CharField(source='concepto.nombre', read_only=True)
    nombre_usuario = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = Pago
        fields = '__all__'
        # AQUÍ ESTÁ LA SOLUCIÓN: Agregamos 'usuario' a read_only_fields
        read_only_fields = ('fecha_pago', 'estado', 'usuario')