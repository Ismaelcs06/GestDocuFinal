from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Importamos tanto los ViewSets (API) como las Vistas (HTML)
from .views import (
    PagoViewSet, 
    ConceptoPagoViewSet, 
    FacturaViewSet, 
    registrar_pago_view, 
    historial_pagos_view,
    conceptos_list_view,
    generar_pdf_view,
    crear_intento_pago,
)

app_name = 'finanzas'

# Configuración de rutas para la API (JSON)
router = DefaultRouter()
router.register(r'pagos', PagoViewSet, basename='pagos')
router.register(r'conceptos', ConceptoPagoViewSet, basename='conceptos')
router.register(r'facturas', FacturaViewSet, basename='facturas')

urlpatterns = [
    # 1. Rutas de la API (Para Móvil y JS)
    # Esto habilita: /api/finanzas/pagos/
    path('', include(router.urls)),

    # 2. Rutas de las Pantallas Web (HTML)
    # Esto habilita: /api/finanzas/registrar/
    path('registrar/', registrar_pago_view, name='registrar_pago'),
    
    # Esto habilita: /api/finanzas/historial/
    path('historial/', historial_pagos_view, name='historial_pagos'),
    
    path('catalogo/', conceptos_list_view, name='conceptos_list'),
    
    path('factura/<int:pago_id>/', generar_pdf_view, name='descargar_factura'),
    
    path('crear-intento-pago/', crear_intento_pago, name='crear_intento_pago'),
]