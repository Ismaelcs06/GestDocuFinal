from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import uuid
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.shortcuts import get_object_or_404
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Importaciones de modelos locales
from .models import Pago, ConceptoPago, Factura
from .serializers import PagoSerializer, ConceptoPagoSerializer, FacturaSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY

# Importaciones de otras apps para rellenar los Selects del HTML
# (Asegúrate de que 'casos' sea el nombre correcto de tu app)
try:
    from casos.models import Caso
except ImportError:
    Caso = None  # Manejo de error si la app no está lista aún

# =================================================
#  SECCIÓN 1: API REST (Para App Móvil y JS)
# =================================================

class ConceptoPagoViewSet(viewsets.ModelViewSet):
    queryset = ConceptoPago.objects.filter(activo=True)
    serializer_class = ConceptoPagoSerializer

class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all().order_by('-fecha_pago')
    serializer_class = PagoSerializer

    def perform_create(self, serializer):
        # 1. Obtener la instancia del Caso que se está pagando
        caso = serializer.validated_data['caso']
        
        # 2. Buscar al Cliente Principal (Demandante) asociado a este caso
        # Navegamos: Caso -> ParteProcesal -> Cliente -> Actor -> Usuario
        parte_demandante = caso.parteprocesal_set.filter(rolProcesal='DEMANDANTE').select_related('cliente__actor__usuario').first()
        
        # Por defecto, si no encontramos cliente, asignamos el pago al usuario que está logueado (Admin/Abogado)
        usuario_asignado = self.request.user
        
        # Datos para la factura
        nit_cliente = "0"
        nombre_cliente = "Sin Nombre"

        if parte_demandante:
            actor = parte_demandante.cliente.actor
            # Datos reales para la factura
            nit_cliente = actor.ci
            nombre_cliente = f"{actor.nombres} {actor.apellidoPaterno}"
            
            # Intentamos asignar el usuario del cliente si tiene cuenta en el sistema
            if hasattr(actor, 'usuario') and actor.usuario:
                usuario_asignado = actor.usuario

        # 3. Guardamos el Pago con el usuario correcto y estado COMPLETADO
        pago = serializer.save(usuario=usuario_asignado, estado='COMPLETADO')
        
        # 4. Generamos la Factura automáticamente con los datos obtenidos
        if not hasattr(pago, 'factura'):
            Factura.objects.create(
                pago=pago,
                nro_factura=f"F-{uuid.uuid4().hex[:8].upper()}",
                nit_ci=nit_cliente,
                razon_social=nombre_cliente
            )

class FacturaViewSet(viewsets.ReadOnlyModelViewSet):
    # Solo lectura por API, la generación se hace en el backend
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer

# =================================================
#  SECCIÓN 2: VISTAS HTML (Para el Navegador Web)
# =================================================

@login_required
def registrar_pago_view(request):
    """
    Renderiza el formulario HTML para registrar un pago manualmente (HU22).
    Envía los casos y conceptos al template para llenar los <select>.
    """
    conceptos = ConceptoPago.objects.filter(activo=True)
    
    # Filtramos casos que no estén archivados/cerrados para el combo
    if Caso:
        casos = Caso.objects.exclude(estado='Archivado')
    else:
        casos = []

    context = {
        'conceptos': conceptos,
        'casos': casos,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'finanzas/registrar_pago.html', context)

@login_required
def historial_pagos_view(request):
    """
    Renderiza la tabla con el historial de todos los pagos y facturas.
    """
    pagos = Pago.objects.all().select_related('usuario', 'caso', 'factura').order_by('-fecha_pago')
    
    context = {
        'pagos': pagos
    }
    return render(request, 'finanzas/historial.html', context)


@login_required
def conceptos_list_view(request):
    """
    Renderiza la pantalla de gestión de Conceptos de Pago.
    """
    conceptos = ConceptoPago.objects.all().order_by('-activo', 'nombre')
    context = {
        'conceptos': conceptos
    }
    return render(request, 'finanzas/conceptos.html', context)


@login_required
def generar_pdf_view(request, pago_id):
    # 1. Obtener datos
    pago = get_object_or_404(Pago, id=pago_id)
    # Intentamos acceder a la factura, si no existe (casos viejos) manejamos error o creamos una
    try:
        factura = pago.factura
    except Factura.DoesNotExist:
        return HttpResponse("Error: Este pago no tiene factura generada.", status=404)

    # 2. Renderizar HTML con datos
    template_path = 'finanzas/factura_pdf.html'
    context = {'pago': pago, 'factura': factura}
    response = HttpResponse(content_type='application/pdf')
    
    # Esto hace que se descargue con nombre bonito
    filename = f"Factura_{factura.nro_factura}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # 3. Convertir a PDF
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Hubo un error al generar el PDF', status=500)
    return response


@login_required
def crear_intento_pago(request):
    """
    Crea un PaymentIntent en Stripe y devuelve el client_secret al frontend.
    Esto se llama cuando el usuario elige pagar con tarjeta.
    """
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        try:
            monto = float(data.get('monto', 0))
            # Stripe trabaja en centavos (100 Bs = 10000 centavos)
            monto_centavos = int(monto * 100)

            intent = stripe.PaymentIntent.create(
                amount=monto_centavos,
                currency='bob', # O 'usd' si Stripe no te deja usar bolivianos en modo test
                metadata={'usuario_id': request.user.id}
            )
            
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': "Método no permitido"}, status=405)