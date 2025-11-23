from django.core.management.base import BaseCommand
from casos.models import Caso, EquipoCaso, ParteProcesal, Expediente, Carpeta
from actores.models import Actor, Cliente
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Seed data for casos app'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando seed de datos de casos...')
        
        # Verificar que existan actores
        actores = Actor.objects.all()
        clientes = Cliente.objects.all()
        
        if not actores.exists():
            self.stdout.write(
                self.style.ERROR('No hay actores en el sistema. Ejecuta primero seed_actores.')
            )
            return
        
        if not clientes.exists():
            self.stdout.write(
                self.style.ERROR('No hay clientes en el sistema. Ejecuta primero seed_actores.')
            )
            return
        
        # Crear casos
        casos_data = [
            {
                'nroCaso': 'CIV-2024-001',
                'tipoCaso': 'Divorcio',
                'descripcion': 'Proceso de divorcio por mutuo acuerdo',
                'estado': 'ABIERTO',
                'prioridad': 'MEDIA',
                'fechaInicio': datetime.now().date() - timedelta(days=30)
            },
            {
                'nroCaso': 'PEN-2024-002',
                'tipoCaso': 'Robo',
                'descripcion': 'Defensa en caso de robo agravado',
                'estado': 'ABIERTO',
                'prioridad': 'ALTA',
                'fechaInicio': datetime.now().date() - timedelta(days=15)
            },
            {
                'nroCaso': 'LAB-2024-003',
                'tipoCaso': 'Despido Injustificado',
                'descripcion': 'Demanda por despido injustificado',
                'estado': 'ABIERTO',
                'prioridad': 'ALTA',
                'fechaInicio': datetime.now().date() - timedelta(days=45)
            },
            {
                'nroCaso': 'COM-2024-004',
                'tipoCaso': 'Incumplimiento Contractual',
                'descripcion': 'Demanda por incumplimiento de contrato de construcción',
                'estado': 'ABIERTO',
                'prioridad': 'MEDIA',
                'fechaInicio': datetime.now().date() - timedelta(days=20)
            },
            {
                'nroCaso': 'CIV-2024-005',
                'tipoCaso': 'Sucesión',
                'descripcion': 'Proceso de sucesión intestada',
                'estado': 'CERRADO',
                'prioridad': 'BAJA',
                'fechaInicio': datetime.now().date() - timedelta(days=90),
                'fechaFin': datetime.now().date() - timedelta(days=5)
            },
            {
                'nroCaso': 'FAM-2024-006',
                'tipoCaso': 'Pensión Alimenticia',
                'descripcion': 'Demanda de pensión alimenticia',
                'estado': 'ABIERTO',
                'prioridad': 'ALTA',
                'fechaInicio': datetime.now().date() - timedelta(days=10)
            },
            {
                'nroCaso': 'ADM-2024-007',
                'tipoCaso': 'Recurso de Amparo',
                'descripcion': 'Recurso de amparo constitucional',
                'estado': 'ABIERTO',
                'prioridad': 'MEDIA',
                'fechaInicio': datetime.now().date() - timedelta(days=25)
            },
            {
                'nroCaso': 'COM-2024-008',
                'tipoCaso': 'Sociedad Comercial',
                'descripcion': 'Constitución de sociedad comercial',
                'estado': 'ABIERTO',
                'prioridad': 'BAJA',
                'fechaInicio': datetime.now().date() - timedelta(days=5)
            },
            {
                'nroCaso': 'CIV-2024-009',
                'tipoCaso': 'Daños y Perjuicios',
                'descripcion': 'Demanda por daños y perjuicios en accidente de tránsito',
                'estado': 'ABIERTO',
                'prioridad': 'MEDIA',
                'fechaInicio': datetime.now().date() - timedelta(days=35)
            },
            {
                'nroCaso': 'LAB-2024-010',
                'tipoCaso': 'Horas Extras',
                'descripcion': 'Demanda por pago de horas extras',
                'estado': 'ABIERTO',
                'prioridad': 'BAJA',
                'fechaInicio': datetime.now().date() - timedelta(days=12)
            }
        ]
        
        casos_creados = []
        for caso_data in casos_data:
            caso, created = Caso.objects.get_or_create(
                nroCaso=caso_data['nroCaso'],
                defaults=caso_data
            )
            if created:
                self.stdout.write(f'Creado caso: {caso.nroCaso}')
            casos_creados.append(caso)
        
        # Crear expedientes para cada caso
        for i, caso in enumerate(casos_creados):
            expediente, created = Expediente.objects.get_or_create(
                caso=caso,
                defaults={
                    'nroExpediente': f'EXP-{caso.nroCaso}',
                    'estado': 'ABIERTO' if caso.estado == 'ABIERTO' else 'CERRADO',
                    'fechaCreacion': caso.fechaInicio
                }
            )
            if created:
                self.stdout.write(f'Creado expediente: {expediente.nroExpediente}')
        
        # Crear carpetas para cada expediente
        carpetas_por_expediente = [
            ['Documentos Iniciales', 'Pruebas', 'Escritos', 'Resoluciones'],
            ['Denuncia', 'Pruebas', 'Testimonios', 'Peritajes'],
            ['Contrato', 'Pruebas', 'Testimonios', 'Resoluciones'],
            ['Contrato Original', 'Comunicaciones', 'Pruebas', 'Resoluciones'],
            ['Testamento', 'Pruebas', 'Inventario', 'Resoluciones'],
            ['Demanda', 'Pruebas', 'Testimonios', 'Resoluciones'],
            ['Recurso', 'Pruebas', 'Fundamentos', 'Resoluciones'],
            ['Estatutos', 'Documentos Societarios', 'Pruebas', 'Resoluciones'],
            ['Denuncia', 'Pruebas', 'Peritajes', 'Resoluciones'],
            ['Contrato Laboral', 'Pruebas', 'Testimonios', 'Resoluciones']
        ]
        
        expedientes = Expediente.objects.all()
        for i, expediente in enumerate(expedientes):
            if i < len(carpetas_por_expediente):
                for nombre_carpeta in carpetas_por_expediente[i]:
                    carpeta, created = Carpeta.objects.get_or_create(
                        expediente=expediente,
                        nombre=nombre_carpeta,
                        defaults={
                            'estado': 'ACTIVO'
                        }
                    )
                    if created:
                        self.stdout.write(f'Creada carpeta: {carpeta.nombre} en {expediente.nroExpediente}')
        
        # Crear equipos de caso (asignar actores a casos)
        abogados = Actor.objects.filter(tipoActor='ABO')
        asistentes = Actor.objects.filter(tipoActor='ASI')
        
        for caso in casos_creados[:8]:  # Solo para los primeros 8 casos
            # Asignar abogado responsable
            if abogados.exists():
                abogado = random.choice(abogados)
                equipo, created = EquipoCaso.objects.get_or_create(
                    actor=abogado,
                    caso=caso,
                    defaults={
                        'rolEnEquipo': 'RESPONSABLE',
                        'observaciones': f'Abogado responsable del caso {caso.nroCaso}',
                        'fechaAsignacion': caso.fechaInicio
                    }
                )
                if created:
                    self.stdout.write(f'Asignado abogado {abogado} como responsable en {caso.nroCaso}')
            
            # Asignar asistente si existe
            if asistentes.exists() and random.choice([True, False]):
                asistente = random.choice(asistentes)
                equipo, created = EquipoCaso.objects.get_or_create(
                    actor=asistente,
                    caso=caso,
                    defaults={
                        'rolEnEquipo': 'ASISTENTE',
                        'observaciones': f'Asistente legal del caso {caso.nroCaso}',
                        'fechaAsignacion': caso.fechaInicio
                    }
                )
                if created:
                    self.stdout.write(f'Asignado asistente {asistente} en {caso.nroCaso}')
        
        # Crear partes procesales (asignar clientes a casos)
        roles_procesales = ['DEMANDANTE', 'DEMANDADO', 'TERCERO']
        
        for i, caso in enumerate(casos_creados[:6]):  # Solo para los primeros 6 casos
            if i < len(clientes):
                cliente = clientes[i]
                rol = random.choice(roles_procesales)
                
                parte, created = ParteProcesal.objects.get_or_create(
                    cliente=cliente,
                    caso=caso,
                    defaults={
                        'rolProcesal': rol,
                        'estado': 'ACTIVO',
                        'fechaInicio': caso.fechaInicio
                    }
                )
                if created:
                    self.stdout.write(f'Asignado cliente {cliente} como {rol} en {caso.nroCaso}')
        
        self.stdout.write(
            self.style.SUCCESS('Seed de casos completado exitosamente!')
        )
