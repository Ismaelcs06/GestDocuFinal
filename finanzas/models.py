from django.db import models
from django.conf import settings  # Para referenciar al Usuario correctamente

# Si necesitas importar el modelo de Caso explícitamente:
# from casos.models import Caso 
# Pero usaremos 'string reference' para evitar errores de importación circular.

class ConceptoPago(models.Model):
    nombre = models.CharField(max_length=100)
    precio_sugerido = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Pago(models.Model):
    METODOS = [
        ('EFECTIVO', 'Efectivo'),
        ('QR', 'Pago QR'),
        ('TARJETA', 'Pasarela (Stripe)'),
    ]
    
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADO', 'Completado'),
        ('FALLIDO', 'Fallido'),
    ]

    # RELACIONES CON TU ESTRUCTURA ACTUAL
    # 1. Relación con CASOS (Tu app 'casos')
    caso = models.ForeignKey('casos.Caso', on_delete=models.PROTECT, related_name='pagos')
    
    # 2. Relación con USUARIO (Tu app 'accounts' o el User por defecto)
    # Usamos settings.AUTH_USER_MODEL es la mejor práctica en Django
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='pagos_realizados')
    
    concepto = models.ForeignKey(ConceptoPago, on_delete=models.SET_NULL, null=True)
    
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=20, choices=METODOS, default='EFECTIVO')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    
    # Para la HU23 (Pasarela)
    transaccion_id_externo = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Pago #{self.id} - {self.monto} Bs"

class Factura(models.Model):
    pago = models.OneToOneField(Pago, on_delete=models.PROTECT, related_name='factura')
    nro_factura = models.CharField(max_length=50, unique=True)
    nit_ci = models.CharField(max_length=20)
    razon_social = models.CharField(max_length=150)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    codigo_control = models.CharField(max_length=50, blank=True, null=True)
    
    # Guardaremos el PDF en la carpeta 'media/facturas'
    archivo_pdf = models.FileField(upload_to='facturas/', blank=True, null=True)

    def __str__(self):
        return f"Factura {self.nro_factura}"