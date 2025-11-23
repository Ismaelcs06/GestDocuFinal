from .models import EventoExpediente

def registrar_evento_exp(usuario, expediente, tipo, descripcion):
    """
    Crea un registro en el timeline del expediente
    """
    if expediente and usuario:
        EventoExpediente.objects.create(
            usuario=usuario,
            expediente=expediente,
            tipo=tipo,
            descripcion=descripcion
        )
