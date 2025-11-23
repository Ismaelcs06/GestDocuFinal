from django.core.management.base import BaseCommand
from documentos.models import TipoDocumento, EtapaProcesal, Documento, VersionDocumento
from casos.models import Carpeta
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed data for documentos app'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando seed de datos de documentos...')
        
        # Verificar que existan carpetas
        carpetas = Carpeta.objects.all()
        usuarios = User.objects.all()
        
        if not carpetas.exists():
            self.stdout.write(
                self.style.ERROR('No hay carpetas en el sistema. Ejecuta primero seed_casos.')
            )
            return
        
        if not usuarios.exists():
            self.stdout.write(
                self.style.ERROR('No hay usuarios en el sistema. Ejecuta primero seed_seguridad.')
            )
            return
        
        # Crear tipos de documentos
        tipos_documentos_data = [
            {'nombre': 'Demanda', 'descripcion': 'Documento inicial de demanda'},
            {'nombre': 'Contestación', 'descripcion': 'Contestación a la demanda'},
            {'nombre': 'Escrito de Pruebas', 'descripcion': 'Escrito ofreciendo pruebas'},
            {'nombre': 'Testimonio', 'descripcion': 'Declaración testimonial'},
            {'nombre': 'Peritaje', 'descripcion': 'Informe pericial'},
            {'nombre': 'Resolución', 'descripcion': 'Resolución judicial'},
            {'nombre': 'Contrato', 'descripcion': 'Contrato legal'},
            {'nombre': 'Poder', 'descripcion': 'Poder notarial'},
            {'nombre': 'Escritura', 'descripcion': 'Escritura pública'},
            {'nombre': 'Certificado', 'descripcion': 'Certificado oficial'},
        ]
        
        tipos_documentos = []
        for tipo_data in tipos_documentos_data:
            tipo, created = TipoDocumento.objects.get_or_create(
                nombre=tipo_data['nombre'],
                defaults={'descripcion': tipo_data['descripcion']}
            )
            tipos_documentos.append(tipo)
            if created:
                self.stdout.write(f'Creado tipo de documento: {tipo.nombre}')
        
        # Crear etapas procesales
        etapas_data = [
            {'nombre': 'Demanda', 'descripcion': 'Etapa inicial del proceso'},
            {'nombre': 'Contestación', 'descripcion': 'Etapa de contestación'},
            {'nombre': 'Pruebas', 'descripcion': 'Etapa probatoria'},
            {'nombre': 'Alegatos', 'descripcion': 'Etapa de alegatos'},
            {'nombre': 'Sentencia', 'descripcion': 'Etapa de sentencia'},
            {'nombre': 'Ejecución', 'descripcion': 'Etapa de ejecución'},
            {'nombre': 'Apelación', 'descripcion': 'Etapa de apelación'},
            {'nombre': 'Recurso', 'descripcion': 'Etapa de recursos'},
            {'nombre': 'Conciliación', 'descripcion': 'Etapa de conciliación'},
            {'nombre': 'Mediación', 'descripcion': 'Etapa de mediación'},
        ]
        
        etapas = []
        for etapa_data in etapas_data:
            etapa, created = EtapaProcesal.objects.get_or_create(
                nombre=etapa_data['nombre'],
                defaults={'descripcion': etapa_data['descripcion']}
            )
            etapas.append(etapa)
            if created:
                self.stdout.write(f'Creada etapa procesal: {etapa.nombre}')
        
        # Crear documentos
        documentos_data = [
            {'nombre': 'Demanda Inicial - Divorcio', 'ruta': '/documentos/civ-2024-001/demanda_inicial.pdf', 'tamano': 2.5, 'palabraClave': 'divorcio mutuo acuerdo'},
            {'nombre': 'Contestación - Robo', 'ruta': '/documentos/pen-2024-002/contestacion.pdf', 'tamano': 1.8, 'palabraClave': 'robo defensa'},
            {'nombre': 'Escrito de Pruebas - Despido', 'ruta': '/documentos/lab-2024-003/escrito_pruebas.pdf', 'tamano': 3.2, 'palabraClave': 'despido pruebas'},
            {'nombre': 'Testimonio - Incumplimiento', 'ruta': '/documentos/com-2024-004/testimonio.pdf', 'tamano': 1.5, 'palabraClave': 'testimonio contrato'},
            {'nombre': 'Peritaje - Sucesión', 'ruta': '/documentos/civ-2024-005/peritaje.pdf', 'tamano': 4.1, 'palabraClave': 'peritaje sucesión'},
            {'nombre': 'Resolución - Pensión', 'ruta': '/documentos/fam-2024-006/resolucion.pdf', 'tamano': 2.8, 'palabraClave': 'pensión resolución'},
            {'nombre': 'Recurso de Amparo', 'ruta': '/documentos/adm-2024-007/recurso_amparo.pdf', 'tamano': 3.5, 'palabraClave': 'amparo constitucional'},
            {'nombre': 'Estatutos Sociedad', 'ruta': '/documentos/com-2024-008/estatutos.pdf', 'tamano': 5.2, 'palabraClave': 'sociedad estatutos'},
            {'nombre': 'Peritaje Tránsito', 'ruta': '/documentos/civ-2024-009/peritaje_transito.pdf', 'tamano': 2.9, 'palabraClave': 'tránsito peritaje'},
            {'nombre': 'Contrato Laboral', 'ruta': '/documentos/lab-2024-010/contrato_laboral.pdf', 'tamano': 1.7, 'palabraClave': 'contrato horas extras'},
        ]
        
        documentos_creados = []
        for i, doc_data in enumerate(documentos_data):
            if i < len(carpetas):
                carpeta = carpetas[i]
                tipo_doc = random.choice(tipos_documentos)
                etapa = random.choice(etapas) if random.choice([True, False]) else None
                
                documento, created = Documento.objects.get_or_create(
                    carpeta=carpeta,
                    nombreDocumento=doc_data['nombre'],
                    defaults={
                        'tipoDocumento': tipo_doc,
                        'etapaProcesal': etapa,
                        'rutaDocumento': doc_data['ruta'],
                        'tamano': doc_data['tamano'],
                        'estado': 'ACTIVO',
                        'palabraClave': doc_data['palabraClave'],
                        'fechaDoc': datetime.now().date() - timedelta(days=random.randint(1, 30))
                    }
                )
                if created:
                    self.stdout.write(f'Creado documento: {documento.nombreDocumento}')
                documentos_creados.append(documento)
        
        # Crear versiones de documentos
        for documento in documentos_creados:
            # Crear versión inicial
            version_inicial, created = VersionDocumento.objects.get_or_create(
                documento=documento,
                numeroVersion=1,
                defaults={
                    'usuario': random.choice(usuarios),
                    'rutaArchivo': documento.rutaDocumento,
                    'comentario': 'Versión inicial del documento'
                }
            )
            if created:
                self.stdout.write(f'Creada versión inicial para: {documento.nombreDocumento}')
            
            # Crear versiones adicionales (2-3 versiones por documento)
            num_versiones = random.randint(1, 3)
            for v in range(2, num_versiones + 2):
                version, created = VersionDocumento.objects.get_or_create(
                    documento=documento,
                    numeroVersion=v,
                    defaults={
                        'usuario': random.choice(usuarios),
                        'rutaArchivo': f"{documento.rutaDocumento.replace('.pdf', '')}_v{v}.pdf",
                        'comentario': f'Versión {v} - Modificaciones realizadas',
                        'fechaCambio': datetime.now() - timedelta(days=random.randint(1, 15))
                    }
                )
                if created:
                    self.stdout.write(f'Creada versión {v} para: {documento.nombreDocumento}')
        
        self.stdout.write(
            self.style.SUCCESS('Seed de documentos completado exitosamente!')
        )
