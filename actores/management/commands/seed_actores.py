from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from actores.models import Actor, Abogado, Cliente, Asistente
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed data for actores app'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando seed de datos de actores...')
        
        # Obtener usuarios existentes
        usuarios = User.objects.all()
        if not usuarios.exists():
            self.stdout.write(
                self.style.ERROR('No hay usuarios en el sistema. Ejecuta primero seed_seguridad.')
            )
            return
        
        # Datos de actores
        actores_data = [
            # Abogados
            {'tipo': 'ABO', 'nombres': 'Carlos', 'apellidoPaterno': 'Mendoza', 'apellidoMaterno': 'Rojas', 'ci': '12345678', 'telefono': '70123456', 'direccion': 'Av. 16 de Julio 1234, La Paz'},
            {'tipo': 'ABO', 'nombres': 'Ana', 'apellidoPaterno': 'García', 'apellidoMaterno': 'López', 'ci': '87654321', 'telefono': '70234567', 'direccion': 'Calle Potosí 567, La Paz'},
            {'tipo': 'ABO', 'nombres': 'Roberto', 'apellidoPaterno': 'Vargas', 'apellidoMaterno': 'Silva', 'ci': '11223344', 'telefono': '70345678', 'direccion': 'Av. Mariscal Santa Cruz 890, La Paz'},
            {'tipo': 'ABO', 'nombres': 'Patricia', 'apellidoPaterno': 'Fernández', 'apellidoMaterno': 'Morales', 'ci': '44332211', 'telefono': '70456789', 'direccion': 'Calle Comercio 234, La Paz'},
            
            # Clientes
            {'tipo': 'CLI', 'nombres': 'Juan', 'apellidoPaterno': 'Pérez', 'apellidoMaterno': 'González', 'ci': '55667788', 'telefono': '70567890', 'direccion': 'Zona Sur, Calle 5 123, La Paz'},
            {'tipo': 'CLI', 'nombres': 'María', 'apellidoPaterno': 'Rodríguez', 'apellidoMaterno': 'Herrera', 'ci': '99887766', 'telefono': '70678901', 'direccion': 'El Alto, Av. 6 de Marzo 456'},
            {'tipo': 'CLI', 'nombres': 'Luis', 'apellidoPaterno': 'Martínez', 'apellidoMaterno': 'Castro', 'ci': '33445566', 'telefono': '70789012', 'direccion': 'Zona Norte, Calle 10 789, La Paz'},
            {'tipo': 'CLI', 'nombres': 'Carmen', 'apellidoPaterno': 'Jiménez', 'apellidoMaterno': 'Vega', 'ci': '77889900', 'telefono': '70890123', 'direccion': 'Miraflores, Av. Busch 321, La Paz'},
            
            # Asistentes
            {'tipo': 'ASI', 'nombres': 'María', 'apellidoPaterno': 'López', 'apellidoMaterno': 'Torres', 'ci': '11223355', 'telefono': '70901234', 'direccion': 'San Pedro, Calle 15 654, La Paz'},
            {'tipo': 'ASI', 'nombres': 'Pedro', 'apellidoPaterno': 'Sánchez', 'apellidoMaterno': 'Ruiz', 'ci': '66778899', 'telefono': '70012345', 'direccion': 'Obrajes, Av. 20 de Octubre 987, La Paz'},
        ]
        
        # Crear actores
        actores_creados = []
        for i, actor_data in enumerate(actores_data):
            # Asignar usuario (usar los usuarios existentes o crear uno nuevo)
            if i < len(usuarios):
                usuario = usuarios[i]
            else:
                # Crear usuario adicional si es necesario
                username = f"{actor_data['nombres'].lower()}{actor_data['apellidoPaterno'].lower()}"
                email = f"{username}@email.com"
                usuario = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=actor_data['nombres'],
                    last_name=actor_data['apellidoPaterno'],
                    password='123456'
                )
            
            actor, created = Actor.objects.get_or_create(
                usuario=usuario,
                defaults={
                    'tipoActor': actor_data['tipo'],
                    'nombres': actor_data['nombres'],
                    'apellidoPaterno': actor_data['apellidoPaterno'],
                    'apellidoMaterno': actor_data['apellidoMaterno'],
                    'ci': actor_data['ci'],
                    'telefono': actor_data['telefono'],
                    'direccion': actor_data['direccion'],
                    'estadoActor': 'ACTIVO'
                }
            )
            
            if created:
                self.stdout.write(f'Creado actor: {actor.nombres} {actor.apellidoPaterno} ({actor.get_tipoActor_display()})')
            actores_creados.append(actor)
        
        # Crear abogados
        abogados_data = [
            {'nroCredencial': 'ABG-001-2024', 'especialidad': 'Derecho Civil'},
            {'nroCredencial': 'ABG-002-2024', 'especialidad': 'Derecho Penal'},
            {'nroCredencial': 'ABG-003-2024', 'especialidad': 'Derecho Laboral'},
            {'nroCredencial': 'ABG-004-2024', 'especialidad': 'Derecho Comercial'},
        ]
        
        abogados_actores = [actor for actor in actores_creados if actor.tipoActor == 'ABO']
        for i, abogado_data in enumerate(abogados_data):
            if i < len(abogados_actores):
                abogado, created = Abogado.objects.get_or_create(
                    actor=abogados_actores[i],
                    defaults={
                        'nroCredencial': abogado_data['nroCredencial'],
                        'especialidad': abogado_data['especialidad'],
                        'estadoLicencia': 'VIGENTE'
                    }
                )
                if created:
                    self.stdout.write(f'Creado abogado: {abogado}')
        
        # Crear clientes
        clientes_data = [
            {'tipoCliente': 'NATURAL', 'observaciones': 'Cliente particular'},
            {'tipoCliente': 'NATURAL', 'observaciones': 'Cliente particular'},
            {'tipoCliente': 'JURIDICO', 'observaciones': 'Empresa constructora'},
            {'tipoCliente': 'NATURAL', 'observaciones': 'Cliente particular'},
        ]
        
        clientes_actores = [actor for actor in actores_creados if actor.tipoActor == 'CLI']
        for i, cliente_data in enumerate(clientes_data):
            if i < len(clientes_actores):
                cliente, created = Cliente.objects.get_or_create(
                    actor=clientes_actores[i],
                    defaults={
                        'tipoCliente': cliente_data['tipoCliente'],
                        'observaciones': cliente_data['observaciones']
                    }
                )
                if created:
                    self.stdout.write(f'Creado cliente: {cliente}')
        
        # Crear asistentes
        asistentes_data = [
            {'area': 'Administración Legal', 'cargo': 'Asistente Senior'},
            {'area': 'Gestión Documental', 'cargo': 'Asistente Junior'},
        ]
        
        asistentes_actores = [actor for actor in actores_creados if actor.tipoActor == 'ASI']
        for i, asistente_data in enumerate(asistentes_data):
            if i < len(asistentes_actores):
                asistente, created = Asistente.objects.get_or_create(
                    actor=asistentes_actores[i],
                    defaults={
                        'area': asistente_data['area'],
                        'cargo': asistente_data['cargo']
                    }
                )
                if created:
                    self.stdout.write(f'Creado asistente: {asistente}')
        
        self.stdout.write(
            self.style.SUCCESS('Seed de actores completado exitosamente!')
        )
