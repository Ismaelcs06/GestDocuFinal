from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.utils import timezone
from django.apps import apps
import json

from .models import Bitacora, DetalleBitacora


# === FUNCIONES AUXILIARES ===

def get_client_ip(request):
    """Obtiene la IP real del cliente, incluso si está detrás de un proxy."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip


def registrar_detalle(usuario, accion, tabla, detalle):
    """
    Crea un registro de DetalleBitacora asociado al último evento del usuario.
    Si no existe una Bitacora base reciente, crea una genérica.
    """
    try:
        bitacora = Bitacora.objects.filter(idUsuario=usuario).order_by('-fecha').first()
        if not bitacora:
            bitacora = Bitacora.objects.create(
                idUsuario=usuario,
                login=f"Acción automática ({accion})",
                ip="127.0.0.1",
                userAgent="Sistema interno",
                fecha=timezone.now()
            )

        DetalleBitacora.objects.create(
            idBitacora=bitacora,
            accion=accion,
            tabla=tabla,
            detalle=detalle,
            fecha=timezone.now()
        )
    except Exception as e:
        print("⚠️ Error registrando detalle de bitácora:", e)


# === LOGIN / LOGOUT ===

@receiver(user_logged_in)
def registrar_login(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    agente = request.META.get('HTTP_USER_AGENT', '')
    Bitacora.objects.create(
        idUsuario=user,
        login="Inicio de sesión",
        ip=ip,
        userAgent=agente,
        fecha=timezone.now()
    )


@receiver(user_logged_out)
def registrar_logout(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    agente = request.META.get('HTTP_USER_AGENT', '')
    Bitacora.objects.create(
        idUsuario=user,
        login="Cierre de sesión",
        ip=ip,
        userAgent=agente,
        fecha=timezone.now()
    )


# === CREAR / EDITAR ===

@receiver(post_save)
def registrar_guardado(sender, instance, created, **kwargs):
    """
    Registra automáticamente la creación o modificación de registros.
    Ignora los modelos internos del sistema.
    """
    # Evita registrar la misma bitácora
    if sender.__name__ in ["Bitacora", "DetalleBitacora", "Session", "ContentType"]:
        return

    usuario = getattr(instance, "modificado_por", None) or getattr(instance, "creado_por", None)
    if not usuario:
        return

    accion = "Creación" if created else "Modificación"

    try:
        # Convertimos a JSON legible (sin campos internos)
        data = {k: str(v) for k, v in instance.__dict__.items() if not k.startswith('_')}
        detalle = json.dumps(data, ensure_ascii=False, indent=2)
    except Exception:
        detalle = f"{accion} de {sender.__name__} con ID {instance.pk}"

    registrar_detalle(usuario, accion, sender.__name__, detalle)


# === ELIMINAR ===

@receiver(post_delete)
def registrar_eliminacion(sender, instance, **kwargs):
    """
    Registra automáticamente la eliminación de registros.
    """
    if sender.__name__ in ["Bitacora", "DetalleBitacora", "Session", "ContentType"]:
        return

    usuario = getattr(instance, "modificado_por", None) or getattr(instance, "creado_por", None)
    if not usuario:
        return

    try:
        data = {k: str(v) for k, v in instance.__dict__.items() if not k.startswith('_')}
        detalle = json.dumps(data, ensure_ascii=False, indent=2)
    except Exception:
        detalle = f"Eliminación de {sender.__name__} con ID {instance.pk}"

    registrar_detalle(usuario, "Eliminación", sender.__name__, detalle)
