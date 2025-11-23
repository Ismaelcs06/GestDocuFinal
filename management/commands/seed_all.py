from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Ejecuta todos los seeders en el orden correcto'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando proceso completo de seeders...')
        
        # Orden de ejecución de seeders
        seeders = [
            'seed_seguridad',
            'seed_actores', 
            'seed_casos',
            'seed_documentos',
            'seed_chat'
        ]
        
        for seeder in seeders:
            self.stdout.write(f'\n--- Ejecutando {seeder} ---')
            try:
                call_command(seeder)
                self.stdout.write(f'✓ {seeder} completado exitosamente')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error en {seeder}: {str(e)}')
                )
                return
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Todos los seeders ejecutados exitosamente!')
        )
        self.stdout.write('\nDatos de prueba creados:')
        self.stdout.write('• 5 usuarios con roles y permisos')
        self.stdout.write('• 10 actores (4 abogados, 4 clientes, 2 asistentes)')
        self.stdout.write('• 10 casos legales con expedientes y carpetas')
        self.stdout.write('• 10 documentos con versiones')
        self.stdout.write('• Bitácoras de auditoría')
        self.stdout.write('• Configuración de IA para el chat')
        self.stdout.write('\nPuedes acceder al sistema con:')
        self.stdout.write('• Usuario: admin / Contraseña: 123456')
        self.stdout.write('• Usuario: abogado1 / Contraseña: 123456')
        self.stdout.write('• Usuario: cliente1 / Contraseña: 123456')
        self.stdout.write('\n🤖 Chat con IA disponible en: /chat/')
        self.stdout.write('⚠️  Recuerda configurar OPENAI_API_KEY en el archivo .env')
