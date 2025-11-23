from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# ==========================
# USUARIO (CustomUser)
# ==========================
class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    estado = models.CharField(max_length=20, default="ACTIVO")
    estadoCuenta = models.CharField(max_length=20, default="HABILITADA")
    creadoEn = models.DateTimeField(auto_now_add=True)
    actualizadoEn = models.DateTimeField(auto_now=True)

    @property
    def nombreUser(self):
        return self.username

    @property
    def contrasena(self):
        return self.password

    def __str__(self):
        return f"{self.username} ({self.email})"


# ==========================
# ROLES / PERMISOS
# ==========================
class Rol(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    # 🧾 Auditoría
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="rol_creados",
        null=True, blank=True
    )
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="rol_modificados",
        null=True, blank=True
    )

    def __str__(self):
        return self.nombre


class Permiso(models.Model):
    descripcion = models.CharField(max_length=150)
    accion = models.CharField(max_length=100, unique=True)

    # 🧾 Auditoría
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="permiso_creados",
        null=True, blank=True
    )
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="permiso_modificados",
        null=True, blank=True
    )

    def __str__(self):
        return self.accion


class UsuarioRol(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, db_index=True)
    fechaAsignacion = models.DateField(auto_now_add=True)

    # 🧾 Auditoría
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="usuariorol_creados",
        null=True, blank=True
    )
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="usuariorol_modificados",
        null=True, blank=True
    )

    class Meta:
        unique_together = (("usuario", "rol"),)
        indexes = [
            models.Index(fields=["usuario", "rol"]),
        ]

    def __str__(self):
        return f"{self.usuario} -> {self.rol}"


class RolPermiso(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, db_index=True)
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE, db_index=True)
    estado = models.CharField(max_length=20, default="ACTIVO")

    # 🧾 Auditoría
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="rolpermiso_creados",
        null=True, blank=True
    )
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="rolpermiso_modificados",
        null=True, blank=True
    )

    class Meta:
        unique_together = (("rol", "permiso"),)
        indexes = [
            models.Index(fields=["rol", "permiso"]),
        ]

    def __str__(self):
        return f"{self.rol} -> {self.permiso}"


# ==========================
# BITÁCORA
# ==========================
class Bitacora(models.Model):
    login = models.CharField(max_length=100)
    ip = models.GenericIPAddressField(null=True, blank=True)
    userAgent = models.TextField(blank=True)
    fecha = models.DateTimeField()
    login_at = models.DateTimeField(null=True, blank=True)
    logout_at = models.DateTimeField(null=True, blank=True)
    device = models.CharField(max_length=255, null=True, blank=True)

    idUsuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="bitacoras",
        db_index=True
    )

    class Meta:
        db_table = "bitacora"
        indexes = [
            models.Index(fields=["idUsuario", "fecha"]),
            models.Index(fields=["login", "fecha"]),
        ]

    def __str__(self):
        return f"{self.login} - {self.idUsuario} @ {self.fecha:%Y-%m-%d %H:%M}"


class DetalleBitacora(models.Model):
    idBitacora = models.ForeignKey(
        Bitacora,
        on_delete=models.CASCADE,
        related_name="detalles"
    )
    accion = models.CharField(max_length=100)
    fecha = models.DateTimeField()
    tabla = models.CharField(max_length=100)
    detalle = models.TextField(blank=True)

    class Meta:
        db_table = "detallebitacora"
        indexes = [
            models.Index(fields=["tabla", "fecha"]),
            models.Index(fields=["accion", "fecha"]),
        ]

    def __str__(self):
        return f"{self.tabla} - {self.accion} ({self.fecha:%Y-%m-%d %H:%M})"
