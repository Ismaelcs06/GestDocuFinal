from django.db import models
from django.conf import settings
from casos.models import Carpeta
from seguridad.models import Usuario

# Create your models here.

# ==========================
# TIPO DE DOCUMENTO
# ==========================
class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


# ==========================
# ETAPA PROCESAL
# ==========================
class EtapaProcesal(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, default="ACTIVO")

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


# ==========================
# DOCUMENTO
# ==========================
class Documento(models.Model):
    carpeta = models.ForeignKey(
        Carpeta,
        on_delete=models.CASCADE,
        related_name="documentos",
        db_index=True,
    )
    tipoDocumento = models.ForeignKey(
        TipoDocumento,
        on_delete=models.PROTECT,
        related_name="documentos",
        db_index=True,
    )
    etapaProcesal = models.ForeignKey(
        EtapaProcesal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documentos",
        db_index=True,
    )

    nombreDocumento = models.CharField(max_length=200)
    rutaDocumento = models.FileField(
        upload_to="documentos/%Y/%m/%d/",
        blank=True,
        null=True,
        help_text="Archivo físico del documento"
    )
    estado = models.CharField(max_length=20, default="ACTIVO")
    palabraClave = models.CharField(max_length=150, blank=True)
    fechaDoc = models.DateField(help_text="Fecha del documento (emisión o recepción)")

    # 👇 Campos para auditoría
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='documentos_creados',
        null=True,
        blank=True
    )
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='documentos_modificados',
        null=True,
        blank=True
    )

    creadoEn = models.DateTimeField(auto_now_add=True)
    actualizadoEn = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["carpeta", "estado"]),
            models.Index(fields=["fechaDoc"]),
        ]

    def __str__(self):
        return self.nombreDocumento


# ==========================
# VERSIÓN DE DOCUMENTO
# ==========================
class VersionDocumento(models.Model):
    documento = models.ForeignKey(
        Documento,
        on_delete=models.CASCADE,
        related_name="versiones",
        db_index=True,
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="versiones_creadas",
        db_index=True,
    )

    numeroVersion = models.PositiveIntegerField()
    rutaArchivo = models.FileField(
        upload_to="versiones/%Y/%m/%d/",
        blank=True,
        null=True,
        help_text="Archivo físico de esta versión"
    )
    fechaCambio = models.DateTimeField(auto_now_add=True)
    comentario = models.TextField(blank=True)

    class Meta:
        unique_together = (("documento", "numeroVersion"),)
        ordering = ["-fechaCambio"]
        indexes = [
            models.Index(fields=["documento", "numeroVersion"]),
            models.Index(fields=["creado_por"]),
        ]

    def __str__(self):
        return f"{self.documento.nombreDocumento} v{self.numeroVersion}"