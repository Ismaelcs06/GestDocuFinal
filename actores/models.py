from django.db import models
from django.conf import settings
# Create your models here.

# ==========================
# ACTOR (1–a–1 con Usuario)
# ==========================
class Actor(models.Model):
    TIPO_CHOICES = (
        ("ABO", "Abogado"),
        ("CLI", "Cliente"),
        ("ASI", "Asistente"),
    )

    ESTADOS = (
        ("ACTIVO", "Activo"),
        ("INACTIVO", "Inactivo"),
    )

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,      # no perder integridad si intentan borrar el usuario
        related_name="actor"
    )

    tipoActor = models.CharField(max_length=5, choices=TIPO_CHOICES)
    nombres = models.CharField(max_length=120)
    apellidoPaterno = models.CharField(max_length=80)
    apellidoMaterno = models.CharField(max_length=80, blank=True)
    ci = models.CharField(max_length=30, unique=True)
    telefono = models.CharField(max_length=30, blank=True)
    direccion = models.TextField(blank=True)
    estadoActor = models.CharField(max_length=20, choices=ESTADOS, default="ACTIVO")

    #  Auditoría
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="actor_creados",
        null=True, blank=True
    )
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="actor_modificados",
        null=True, blank=True
    )

    creadoEn = models.DateTimeField(auto_now_add=True)
    actualizadoEn = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["tipoActor"]),
            models.Index(fields=["estadoActor"]),
        ]
        # db_table = "actor"

    def __str__(self):
        return f"{self.nombres} {self.apellidoPaterno} ({self.get_tipoActor_display()})"


# ===================================
# SUBTIPOS (PK = FK a Actor.id)
# ===================================

class Abogado(models.Model):
    actor = models.OneToOneField(
        Actor,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="abogado"
    )
    nroCredencial = models.CharField(max_length=50)
    especialidad = models.CharField(max_length=100, blank=True)
    estadoLicencia = models.CharField(max_length=50, default="VIGENTE")

    #  Auditoría
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="abogado_creados",
        null=True, blank=True
    )
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="abogado_modificados",
        null=True, blank=True
    )

    class Meta:
        indexes = [models.Index(fields=["estadoLicencia"])]

    def __str__(self):
        return f"Abg. {self.actor.nombres} {self.actor.apellidoPaterno}"


class Cliente(models.Model):
    actor = models.OneToOneField(
        Actor,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="cliente"
    )
    TIPO_CHOICES = (("NATURAL", "Natural"), ("JURIDICO", "Jurídico"))
    tipoCliente = models.CharField(max_length=10, choices=TIPO_CHOICES)
    observaciones = models.TextField(blank=True)

    #  Auditoría
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="cliente_creados",
        null=True, blank=True
    )
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="cliente_modificados",
        null=True, blank=True
    )

    class Meta:
        indexes = [models.Index(fields=["tipoCliente"])]

    def __str__(self):
        return f"Cliente {self.actor.nombres} {self.actor.apellidoPaterno}"


class Asistente(models.Model):
    actor = models.OneToOneField(
        Actor,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="asistente"
    )
    area = models.CharField(max_length=100, blank=True)
    cargo = models.CharField(max_length=100, blank=True)

    #  Auditoría
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="asistente_creados",
        null=True, blank=True
    )
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="asistente_modificados",
        null=True, blank=True
    )

    class Meta:
        indexes = [models.Index(fields=["area", "cargo"])]

    def __str__(self):
        return f"Asistente {self.actor.nombres} {self.actor.apellidoPaterno}"