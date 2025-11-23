from django.core.management.base import BaseCommand
from chat.models import ConfiguracionIA

class Command(BaseCommand):
    help = 'Seed data for chat app'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando seed de datos de chat...')
        
        # Crear configuración por defecto de IA
        configuracion, created = ConfiguracionIA.objects.get_or_create(
            nombre='Configuración Principal',
            defaults={
                'modelo_openai': 'gpt-3.5-turbo',
                'temperatura': 0.7,
                'max_tokens': 1000,
                'contexto_sistema': '''Eres un asistente legal especializado en gestión documental para el sistema GestDocSi2.

Tu función es ayudar a los usuarios a:
1. Buscar y encontrar documentos específicos
2. Analizar información de casos legales
3. Proporcionar información sobre actores del sistema (abogados, clientes, asistentes)
4. Responder preguntas sobre el estado de casos y expedientes

INSTRUCCIONES:
- Siempre responde en español
- Sé profesional y preciso
- Si encuentras información relevante en el contexto, úsala para dar una respuesta completa
- Si no encuentras información específica, indícalo claramente
- Estructura tu respuesta de manera clara y organizada
- Incluye referencias específicas a documentos, casos o actores cuando sea relevante

FORMATO DE RESPUESTA:
- Usa viñetas para organizar información
- Incluye números de caso, nombres de documentos y fechas cuando estén disponibles
- Proporciona enlaces o referencias específicas cuando sea posible

EJEMPLOS DE RESPUESTAS:
- Para búsqueda de documentos: "Encontré 3 documentos relacionados con 'contrato': [lista de documentos]"
- Para información de casos: "El caso CIV-2024-001 es de tipo 'Divorcio' y está en estado 'ABIERTO'"
- Para actores: "El abogado Carlos Mendoza tiene especialidad en 'Derecho Civil' y está activo"''',
                'activo': True
            }
        )
        
        if created:
            self.stdout.write('Creada configuración de IA: Configuración Principal')
        else:
            self.stdout.write('Configuración de IA ya existe: Configuración Principal')
        
        self.stdout.write(
            self.style.SUCCESS('Seed de chat completado exitosamente!')
        )
