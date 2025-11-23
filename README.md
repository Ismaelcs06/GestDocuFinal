# GestDocSi2 - Sistema de Gestión Documental

Sistema de gestión documental para despachos de abogados desarrollado en Django 5.2.7.

## 📋 Descripción del Proyecto

GestDocSi2 es una aplicación web que permite gestionar de manera integral los documentos, casos legales, actores (abogados, clientes, asistentes) y expedientes de un despacho jurídico.

### 🏗️ Arquitectura del Sistema

El proyecto está estructurado en las siguientes aplicaciones Django:

- **`seguridad`**: Gestión de usuarios, roles, permisos y bitácora de auditoría
- **`actores`**: Gestión de actores del sistema (Abogados, Clientes, Asistentes)
- **`casos`**: Gestión de casos legales, expedientes y carpetas
- **`documentos`**: Gestión de documentos y versiones
- **`portal`**: Página de inicio y autenticación
- **`dashboard`**: Panel de control principal
- **`accounts`**: Gestión de cuentas de usuario
- **`chat`**: Chat inteligente con IA para búsqueda y análisis de documentos

## 🚀 Requisitos del Sistema

### Software Necesario
- **Python**: 3.8 o superior
- **PostgreSQL**: 12 o superior
- **Git**: Para clonar el repositorio

### Dependencias Python
- Django 5.2.7
- psycopg2 2.9.11 (driver PostgreSQL)
- django-environ 0.12.0 (gestión de variables de entorno)
- asgiref 3.10.0
- sqlparse 0.5.3
- tzdata 2025.2

## 📦 Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd GestDocu-Sprint2
```

### 2. Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos PostgreSQL

1. **Crear base de datos**:
```sql
CREATE DATABASE gestdocsi2;
CREATE USER defectdojo WITH PASSWORD '12345678';
GRANT ALL PRIVILEGES ON DATABASE gestdocsi2 TO defectdojo;
```

2. **Crear archivo `.env`** en la raíz del proyecto:
```env
# Configuración de Base de Datos
DB_NAME=gestdocsi2
DB_USER=defectdojo
DB_PASSWORD=12345678
DB_HOST=127.0.0.1
DB_PORT=5433

# Configuración de Django
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura-aqui
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Configuración Regional
LANGUAGE_CODE=es
TIME_ZONE=America/La_Paz

# Configuración de OpenAI (para el chat con IA)
OPENAI_API_KEY=tu-api-key-de-openai-aqui
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000
```

### 5. Ejecutar Migraciones

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate
```

### 6. Crear Superusuario

```bash
python manage.py createsuperuser
```

### 7. Recopilar Archivos Estáticos

```bash
python manage.py collectstatic
```

### 8. Ejecutar el Servidor

```bash
python manage.py runserver
```

El servidor estará disponible en: `http://127.0.0.1:8000`

## 🗄️ Estructura de la Base de Datos

### Modelos Principales

#### Seguridad
- **Usuario**: Usuario personalizado con campos adicionales
- **Rol**: Roles del sistema
- **Permiso**: Permisos específicos
- **UsuarioRol**: Asignación de roles a usuarios
- **RolPermiso**: Asignación de permisos a roles
- **Bitacora**: Registro de auditoría de accesos
- **DetalleBitacora**: Detalles de acciones realizadas

#### Actores
- **Actor**: Actor base (Abogado, Cliente, Asistente)
- **Abogado**: Información específica de abogados
- **Cliente**: Información específica de clientes
- **Asistente**: Información específica de asistentes

#### Casos
- **Caso**: Casos legales
- **EquipoCaso**: Asignación de actores a casos
- **ParteProcesal**: Clientes involucrados en casos
- **Expediente**: Expediente asociado a cada caso
- **Carpeta**: Carpetas dentro de expedientes

#### Documentos
- **TipoDocumento**: Tipos de documentos
- **EtapaProcesal**: Etapas del proceso legal
- **Documento**: Documentos del sistema
- **VersionDocumento**: Versiones de documentos

## 🔧 Comandos Útiles

### Desarrollo
```bash
# Ejecutar servidor de desarrollo
python manage.py runserver

# Ejecutar con puerto específico
python manage.py runserver 8080

# Acceder al shell de Django
python manage.py shell

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Verificar migraciones pendientes
python manage.py showmigrations
```

### Administración
```bash
# Crear superusuario
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic

# Limpiar archivos estáticos
python manage.py collectstatic --clear
```

### Base de Datos
```bash
# Hacer backup de la base de datos
pg_dump -h localhost -U defectdojo gestdocsi2 > backup.sql

# Restaurar backup
psql -h localhost -U defectdojo gestdocsi2 < backup.sql
```

### Seeders (Datos de Prueba)
```bash
# Ejecutar todos los seeders en orden
python manage.py seed_all

# Ejecutar seeders individuales
python manage.py seed_seguridad    # Usuarios, roles, permisos, bitácoras
python manage.py seed_actores      # Actores (abogados, clientes, asistentes)
python manage.py seed_casos        # Casos, expedientes, carpetas
python manage.py seed_documentos   # Documentos y versiones
python manage.py seed_chat         # Configuración de IA para el chat
```

**Datos de prueba incluidos:**
- 5 usuarios con roles y permisos configurados
- 10 actores (4 abogados, 4 clientes, 2 asistentes)
- 10 casos legales con expedientes y carpetas organizadas
- 10 documentos con versiones y control de cambios
- Bitácoras de auditoría con registros de actividad

**Usuarios de prueba:**
- `admin` / `123456` - Administrador del sistema
- `abogado1` / `123456` - Abogado Senior
- `abogado2` / `123456` - Abogado Junior
- `asistente1` / `123456` - Asistente Legal
- `cliente1` / `123456` - Cliente del sistema

## 🌐 URLs del Sistema

- **Inicio**: `/` - Página principal
- **Login**: `/login/` - Autenticación
- **Logout**: `/logout/` - Cerrar sesión
- **Panel**: `/panel/` - Dashboard principal
- **Admin**: `/admin/` - Panel de administración Django
- **Accounts**: `/accounts/` - Gestión de cuentas
- **Chat IA**: Widget flotante - Chat inteligente con asistente IA (esquina inferior derecha)

## 🤖 Chat Inteligente con IA

El sistema incluye un asistente IA integrado que permite:

### 🔍 Búsqueda Inteligente
- **Búsqueda por contenido**: "¿Dónde está el contrato con el proveedor X?"
- **Búsqueda por tipo**: "Muéstrame las facturas de septiembre"
- **Búsqueda por casos**: "¿Qué documentos tiene el caso CIV-2024-001?"
- **Búsqueda por actores**: "Busca información sobre el abogado Carlos Mendoza"

### 💬 Preguntas y Respuestas
- **Información de documentos**: "¿Cuál es la fecha de vencimiento del contrato con X?"
- **Estado de casos**: "¿En qué estado está el caso PEN-2024-002?"
- **Información de actores**: "¿Cuál es la especialidad del abogado Ana García?"

### 🧠 Características del Asistente
- **Widget flotante**: Aparece en la esquina inferior derecha de todas las páginas
- **Integración con OpenAI**: Utiliza GPT-3.5-turbo para respuestas inteligentes
- **Búsqueda contextual**: Analiza la base de datos antes de responder
- **Historial de conversaciones**: Mantiene el contexto de la conversación
- **Referencias específicas**: Incluye enlaces a documentos y casos relevantes
- **Respuestas en español**: Optimizado para el contexto legal boliviano
- **Interfaz moderna**: Animaciones suaves y diseño responsive

### 🔧 Configuración
El chat requiere una API key de OpenAI configurada en el archivo `.env`:
```env
OPENAI_API_KEY=tu-api-key-de-openai-aqui
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000
```

## 👥 Gestión de Usuarios

### Tipos de Actores

1. **Abogados**: Profesionales con credencial y especialidad
2. **Clientes**: Personas naturales o jurídicas
3. **Asistentes**: Personal de apoyo con área y cargo específico

### Roles y Permisos

El sistema utiliza un modelo de roles y permisos flexible que permite:
- Asignar múltiples roles a un usuario
- Definir permisos específicos por rol
- Auditoría completa de acciones

## 📁 Estructura de Archivos

```
GestDocu-Sprint2/
├── GestDocSi2/           # Configuración del proyecto
│   ├── settings.py       # Configuración principal
│   ├── urls.py          # URLs principales
│   └── wsgi.py          # Configuración WSGI
├── accounts/            # Gestión de cuentas
├── actores/            # Gestión de actores
├── casos/              # Gestión de casos
├── dashboard/          # Panel de control
├── documentos/         # Gestión de documentos
├── portal/             # Portal público
├── seguridad/          # Seguridad y auditoría
├── static/             # Archivos estáticos globales
├── templates/          # Plantillas globales
├── manage.py           # Script de gestión Django
├── requirements.txt    # Dependencias Python
└── .env               # Variables de entorno (crear)
```

## 🔒 Seguridad

- **Autenticación**: Sistema de login/logout integrado
- **Autorización**: Control de acceso basado en roles
- **Auditoría**: Bitácora completa de acciones
- **Variables de entorno**: Configuración sensible en `.env`
- **CSRF Protection**: Protección contra ataques CSRF

## 🐛 Solución de Problemas

### Error de Conexión a Base de Datos
```bash
# Verificar que PostgreSQL esté ejecutándose
sudo service postgresql status

# Verificar configuración en .env
cat .env
```

### Error de Migraciones
```bash
# Verificar migraciones pendientes
python manage.py showmigrations

# Aplicar migraciones específicas
python manage.py migrate seguridad
```

### Error de Archivos Estáticos
```bash
# Recopilar archivos estáticos
python manage.py collectstatic --noinput
```

## 📝 Notas de Desarrollo

- El proyecto utiliza **Django 5.2.7** con **PostgreSQL**
- Configuración regional para **Bolivia** (español, zona horaria La Paz)
- Modelo de usuario personalizado en la app `seguridad`
- Sistema de archivos estáticos configurado para producción
- Variables de entorno para configuración flexible

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto es privado y está destinado para uso interno del despacho jurídico.

---

**Desarrollado con ❤️ usando Django**
