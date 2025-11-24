from django.contrib import admin
from .models import ConceptoPago, Pago, Factura

@admin.register(ConceptoPago)
class ConceptoPagoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_sugerido', 'activo')
    search_fields = ('nombre',)

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'caso', 'monto', 'metodo_pago', 'estado', 'fecha_pago')
    list_filter = ('estado', 'metodo_pago', 'fecha_pago')
    search_fields = ('usuario__username', 'caso__nombre_caso') # Ajusta 'nombre_caso' según tu modelo real en 'casos'
    readonly_fields = ('fecha_pago',)

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('nro_factura', 'razon_social', 'nit_ci', 'fecha_emision', 'pago')
    search_fields = ('nro_factura', 'nit_ci', 'razon_social')