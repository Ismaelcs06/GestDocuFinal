from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class Conversacion(models.Model):
    """
    Modelo para almacenar conversaciones del chat
    """
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversaciones'
    )
    titulo = models.CharField(max_length=200, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-fecha_actualizacion']
        verbose_name = 'Conversación'
        verbose_name_plural = 'Conversaciones'
    
    def __str__(self):
        return f"Conversación {self.id} - {self.usuario.username}"


class Mensaje(models.Model):
    """
    Modelo para almacenar mensajes del chat
    """
    TIPO_CHOICES = [
        ('usuario', 'Usuario'),
        ('asistente', 'Asistente IA'),
        ('sistema', 'Sistema'),
    ]
    
    conversacion = models.ForeignKey(
        Conversacion,
        on_delete=models.CASCADE,
        related_name='mensajes'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    
    # Metadatos para análisis
    tokens_usados = models.IntegerField(null=True, blank=True)
    tiempo_respuesta = models.FloatField(null=True, blank=True)  # en segundos
    documentos_consultados = models.JSONField(default=list, blank=True)
    entidades_extraidas = models.JSONField(default=list, blank=True)
    
    class Meta:
        ordering = ['fecha_envio']
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.contenido[:50]}..."


class ConsultaDocumento(models.Model):
    """
    Modelo para registrar consultas específicas a documentos
    """
    mensaje = models.ForeignKey(
        Mensaje,
        on_delete=models.CASCADE,
        related_name='consultas_documentos'
    )
    documento = models.ForeignKey(
        'documentos.Documento',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    caso = models.ForeignKey(
        'casos.Caso',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    # Relación opcional con pagos/facturas (finanzas)
    pago = models.ForeignKey(
        'finanzas.Pago',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    factura = models.ForeignKey(
        'finanzas.Factura',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    actor = models.ForeignKey(
        'actores.Actor',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    tipo_consulta = models.CharField(max_length=50)  # 'buscar', 'analizar', 'resumir'
    resultado = models.TextField(blank=True)
    relevancia = models.FloatField(default=0.0)  # 0-1
    
    class Meta:
        verbose_name = 'Consulta a Documento'
        verbose_name_plural = 'Consultas a Documentos'
    
    def __str__(self):
        return f"Consulta {self.tipo_consulta} - {self.mensaje.contenido[:30]}..."


class ConfiguracionIA(models.Model):
    """
    Modelo para configuraciones del asistente IA
    """
    nombre = models.CharField(max_length=100, unique=True)
    modelo_openai = models.CharField(max_length=50, default='gpt-3.5-turbo')
    temperatura = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=1000)
    contexto_sistema = models.TextField(
        default="Eres un asistente legal especializado en gestión documental. "
                "Ayudas a los usuarios a encontrar y analizar documentos, casos y actores del sistema. "
                "Siempre responde en español y de manera profesional."
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Configuración IA'
        verbose_name_plural = 'Configuraciones IA'
    
    def __str__(self):
        return f"Configuración: {self.nombre}"