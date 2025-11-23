from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from seguridad.models import Rol, Permiso, UsuarioRol, RolPermiso, Bitacora, DetalleBitacora
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed data for seguridad app'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando seed de datos de seguridad...')
        
        # Crear roles
        roles_data = [
            {'nombre': 'Administrador', 'descripcion': 'Acceso completo al sistema'},
            {'nombre': 'Abogado Senior', 'descripcion': 'Abogado con permisos amplios'},
            {'nombre': 'Abogado Junior', 'descripcion': 'Abogado con permisos limitados'},
            {'nombre': 'Asistente Legal', 'descripcion': 'Asistente con permisos de consulta'},
            {'nombre': 'Cliente', 'descripcion': 'Cliente con acceso limitado'},
        ]
        
        roles = []
        for role_data in roles_data:
            rol, created = Rol.objects.get_or_create(
                nombre=role_data['nombre'],
                defaults={'descripcion': role_data['descripcion']}
            )
            roles.append(rol)
            if created:
                self.stdout.write(f'Creado rol: {rol.nombre}')
        
        # Crear permisos
        permisos_data = [
            {'descripcion': 'Crear casos', 'accion': 'crear_caso'},
            {'descripcion': 'Editar casos', 'accion': 'editar_caso'},
            {'descripcion': 'Eliminar casos', 'accion': 'eliminar_caso'},
            {'descripcion': 'Ver casos', 'accion': 'ver_caso'},
            {'descripcion': 'Crear documentos', 'accion': 'crear_documento'},
            {'descripcion': 'Editar documentos', 'accion': 'editar_documento'},
            {'descripcion': 'Eliminar documentos', 'accion': 'eliminar_documento'},
            {'descripcion': 'Ver documentos', 'accion': 'ver_documento'},
            {'descripcion': 'Gestionar usuarios', 'accion': 'gestionar_usuarios'},
            {'descripcion': 'Ver reportes', 'accion': 'ver_reportes'},
        ]
        
        permisos = []
        for perm_data in permisos_data:
            permiso, created = Permiso.objects.get_or_create(
                accion=perm_data['accion'],
                defaults={'descripcion': perm_data['descripcion']}
            )
            permisos.append(permiso)
            if created:
                self.stdout.write(f'Creado permiso: {permiso.accion}')
        
        # Crear usuarios de prueba
        usuarios_data = [
            {'username': 'admin', 'email': 'admin@despacho.com', 'first_name': 'Admin', 'last_name': 'Sistema'},
            {'username': 'abogado1', 'email': 'abogado1@despacho.com', 'first_name': 'Carlos', 'last_name': 'Mendoza'},
            {'username': 'abogado2', 'email': 'abogado2@despacho.com', 'first_name': 'Ana', 'last_name': 'García'},
            {'username': 'asistente1', 'email': 'asistente1@despacho.com', 'first_name': 'María', 'last_name': 'López'},
            {'username': 'cliente1', 'email': 'cliente1@email.com', 'first_name': 'Juan', 'last_name': 'Pérez'},
        ]
        
        usuarios = []
        for user_data in usuarios_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_staff': True if user_data['username'] == 'admin' else False,
                    'is_superuser': True if user_data['username'] == 'admin' else False,
                }
            )
            if created:
                user.set_password('123456')  # Contraseña por defecto
                user.save()
                self.stdout.write(f'Creado usuario: {user.username}')
            usuarios.append(user)
        
        # Asignar roles a usuarios
        asignaciones_roles = [
            (usuarios[0], roles[0]),  # admin -> Administrador
            (usuarios[1], roles[1]),  # abogado1 -> Abogado Senior
            (usuarios[2], roles[2]),  # abogado2 -> Abogado Junior
            (usuarios[3], roles[3]),  # asistente1 -> Asistente Legal
            (usuarios[4], roles[4]),  # cliente1 -> Cliente
        ]
        
        for usuario, rol in asignaciones_roles:
            usuario_rol, created = UsuarioRol.objects.get_or_create(
                usuario=usuario,
                rol=rol
            )
            if created:
                self.stdout.write(f'Asignado rol {rol.nombre} a {usuario.username}')
        
        # Asignar permisos a roles
        asignaciones_permisos = [
            # Administrador - todos los permisos
            (roles[0], permisos[0]), (roles[0], permisos[1]), (roles[0], permisos[2]), (roles[0], permisos[3]),
            (roles[0], permisos[4]), (roles[0], permisos[5]), (roles[0], permisos[6]), (roles[0], permisos[7]),
            (roles[0], permisos[8]), (roles[0], permisos[9]),
            # Abogado Senior - casi todos
            (roles[1], permisos[0]), (roles[1], permisos[1]), (roles[1], permisos[3]),
            (roles[1], permisos[4]), (roles[1], permisos[5]), (roles[1], permisos[7]), (roles[1], permisos[9]),
            # Abogado Junior - limitados
            (roles[2], permisos[3]), (roles[2], permisos[4]), (roles[2], permisos[7]),
            # Asistente Legal - solo consulta
            (roles[3], permisos[3]), (roles[3], permisos[7]),
            # Cliente - solo ver sus documentos
            (roles[4], permisos[7]),
        ]
        
        for rol, permiso in asignaciones_permisos:
            rol_permiso, created = RolPermiso.objects.get_or_create(
                rol=rol,
                permiso=permiso
            )
            if created:
                self.stdout.write(f'Asignado permiso {permiso.accion} a rol {rol.nombre}')
        
        # Crear bitácoras de ejemplo
        for i in range(10):
            usuario = random.choice(usuarios)
            fecha = datetime.now() - timedelta(days=random.randint(1, 30))
            login_at = fecha
            logout_at = fecha + timedelta(hours=random.randint(1, 8))
            
            bitacora = Bitacora.objects.create(
                login=usuario.username,
                ip=f'192.168.1.{random.randint(1, 254)}',
                userAgent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                fecha=fecha,
                login_at=login_at,
                logout_at=logout_at,
                device='Desktop',
                idUsuario=usuario
            )
            
            # Crear detalles de bitácora
            acciones = ['LOGIN', 'LOGOUT', 'CREAR_CASO', 'EDITAR_DOCUMENTO', 'VER_REPORTE']
            tablas = ['usuario', 'caso', 'documento', 'expediente']
            
            for j in range(random.randint(1, 5)):
                DetalleBitacora.objects.create(
                    idBitacora=bitacora,
                    accion=random.choice(acciones),
                    fecha=fecha + timedelta(minutes=random.randint(1, 480)),
                    tabla=random.choice(tablas),
                    detalle=f'Acción realizada por {usuario.username}'
                )
        
        self.stdout.write(
            self.style.SUCCESS('Seed de seguridad completado exitosamente!')
        )
