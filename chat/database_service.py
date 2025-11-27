"""
Servicio especializado para consultas inteligentes a la base de datos
"""
from django.db.models import Q, Count
from casos.models import Caso, Expediente, Carpeta
from documentos.models import Documento, TipoDocumento, EtapaProcesal
from actores.models import Actor, Abogado, Cliente, Asistente
from seguridad.models import Usuario, Rol, Permiso
from finanzas.models import Pago, Factura
from typing import List, Dict, Any
import re

class DatabaseQueryService:
    """
    Servicio para realizar consultas inteligentes a la base de datos
    """
    
    def __init__(self):
        pass
    
    def consultar_informacion(self, consulta: str, usuario=None) -> Dict[str, Any]:
        """
        Consulta inteligente que analiza la pregunta y busca información específica
        """
        consulta_lower = consulta.lower()
        resultados = {
            'casos': [],
            'documentos': [],
            'actores': [],
            'pagos': [],
            'estadisticas': {},
            'respuesta_directa': None
        }
        
        # Análisis de la consulta para determinar qué buscar
        if self._es_consulta_personal(consulta_lower):
            resultados.update(self._buscar_informacion_personal(consulta_lower, usuario))
        
        elif self._es_consulta_estadistica(consulta_lower):
            resultados['estadisticas'] = self._obtener_estadisticas(consulta_lower)
            resultados['respuesta_directa'] = self._generar_respuesta_estadistica(resultados['estadisticas'], consulta_lower)
        
        elif self._es_consulta_especifica(consulta_lower):
            resultados.update(self._buscar_informacion_especifica(consulta_lower))
        
        else:
            # Búsqueda general
            resultados['casos'] = self._buscar_casos_general(consulta_lower)
            resultados['documentos'] = self._buscar_documentos_general(consulta_lower)
            resultados['actores'] = self._buscar_actores_general(consulta_lower)
            # Búsqueda de pagos/facturas
            try:
                resultados['pagos'] = self._buscar_pagos_general(consulta_lower)
            except Exception:
                resultados['pagos'] = []
        
        return resultados
    
    def _buscar_informacion_personal(self, consulta: str, usuario) -> Dict[str, Any]:
        """Busca información personal del usuario"""
        resultados = {
            'casos': [],
            'documentos': [],
            'actores': [],
            'respuesta_directa': None
        }
        
        if not usuario:
            resultados['respuesta_directa'] = "⚠️ No se pudo identificar al usuario para realizar la búsqueda personal."
            return resultados
        
        # Buscar documentos creados por el usuario
        if any(palabra in consulta for palabra in ['documento', 'documentos', 'creado', 'creados']):
            documentos = self._buscar_documentos_personales(usuario, consulta)
            resultados['documentos'] = documentos
            if documentos:
                resultados['respuesta_directa'] = self._formatear_documentos_personales(documentos, usuario)
            else:
                resultados['respuesta_directa'] = f"📄 No se encontraron documentos creados por {usuario.username}."
        
        # Buscar casos asignados al usuario
        elif any(palabra in consulta for palabra in ['caso', 'casos', 'asignado', 'asignados']):
            casos = self._buscar_casos_personales(usuario, consulta)
            resultados['casos'] = casos
            if casos:
                resultados['respuesta_directa'] = self._formatear_casos_personales(casos, usuario)
            else:
                resultados['respuesta_directa'] = f"📁 No se encontraron casos asignados a {usuario.username}."
        
        # Buscar información del actor asociado al usuario
        elif any(palabra in consulta for palabra in ['actor', 'perfil', 'información', 'datos']):
            actor_info = self._buscar_informacion_actor_usuario(usuario)
            if actor_info:
                resultados['respuesta_directa'] = self._formatear_informacion_actor(actor_info, usuario)
            else:
                resultados['respuesta_directa'] = f"👤 No se encontró información del actor asociado a {usuario.username}."
        
        else:
            # Búsqueda general personal
            documentos = self._buscar_documentos_personales(usuario, consulta)
            casos = self._buscar_casos_personales(usuario, consulta)
            actor_info = self._buscar_informacion_actor_usuario(usuario)
            
            resultados['documentos'] = documentos
            resultados['casos'] = casos
            
            if documentos or casos or actor_info:
                respuesta = []
                if documentos:
                    respuesta.append(f"📄 **Documentos de {usuario.username}:** {len(documentos)} encontrados")
                if casos:
                    respuesta.append(f"📁 **Casos de {usuario.username}:** {len(casos)} encontrados")
                if actor_info:
                    respuesta.append(f"👤 **Información del actor:** {actor_info['nombres']} {actor_info['apellido_paterno']}")
                
                resultados['respuesta_directa'] = "\n".join(respuesta)
            else:
                resultados['respuesta_directa'] = f"🔍 No se encontró información personal para {usuario.username}."
        
        return resultados
    
    def _es_consulta_personal(self, consulta: str) -> bool:
        """Determina si la consulta es personal del usuario"""
        palabras_personales = [
            'mis', 'mi', 'he creado', 'he hecho', 'he enviado', 'he recibido',
            'me han asignado', 'me han dado', 'tengo', 'soy', 'estoy',
            'mi caso', 'mis casos', 'mi documento', 'mis documentos',
            'mi cliente', 'mis clientes', 'mi abogado', 'mis abogados',
            'asignado a mí', 'relacionado conmigo', 'que me pertenece'
        ]
        return any(palabra in consulta for palabra in palabras_personales)
    
    def _es_consulta_estadistica(self, consulta: str) -> bool:
        """Determina si la consulta es sobre estadísticas"""
        palabras_estadisticas = [
            'cuántos', 'cuanto', 'cantidad', 'total', 'número', 'numero',
            'cuántas', 'cuanta', 'estadística', 'estadistica', 'resumen',
            'listar', 'mostrar todos', 'todos los', 'todos las'
        ]
        return any(palabra in consulta for palabra in palabras_estadisticas)
    
    def _es_consulta_especifica(self, consulta: str) -> bool:
        """Determina si la consulta es sobre información específica"""
        palabras_especificas = [
            'cuál', 'cual', 'qué', 'que', 'dónde', 'donde', 'cuando',
            'especialidad', 'tipo', 'estado', 'fecha', 'nombre'
        ]
        return any(palabra in consulta for palabra in palabras_especificas)
    
    def _obtener_estadisticas(self, consulta: str) -> Dict[str, Any]:
        """Obtiene estadísticas de la base de datos"""
        stats = {}
        
        # Estadísticas de casos
        if any(palabra in consulta for palabra in ['caso', 'casos']):
            stats['casos'] = {
                'total': Caso.objects.count(),
                'por_tipo': list(Caso.objects.values('tipoCaso').annotate(count=Count('id'))),
                'por_estado': list(Caso.objects.values('estado').annotate(count=Count('id'))),
                'abiertos': Caso.objects.filter(estado='ABIERTO').count(),
                'cerrados': Caso.objects.filter(estado='CERRADO').count()
            }
        
        # Estadísticas de documentos
        if any(palabra in consulta for palabra in ['documento', 'documentos']):
            stats['documentos'] = {
                'total': Documento.objects.count(),
                'por_tipo': list(Documento.objects.values('tipoDocumento__nombre').annotate(count=Count('id'))),
                'con_palabras_clave': Documento.objects.exclude(palabraClave='').count(),
                'sin_palabras_clave': Documento.objects.filter(palabraClave='').count()
            }
        
        # Estadísticas de actores
        if any(palabra in consulta for palabra in ['actor', 'actores', 'abogado', 'cliente', 'asistente']):
            stats['actores'] = {
                'total': Actor.objects.count(),
                'abogados': Abogado.objects.count(),
                'clientes': Cliente.objects.count(),
                'asistentes': Asistente.objects.count(),
                'por_especialidad': list(Abogado.objects.values('especialidad').annotate(count=Count('actor_id'))),
                'por_tipo_cliente': list(Cliente.objects.values('tipoCliente').annotate(count=Count('actor_id')))
            }
        
        # Estadísticas de usuarios
        if any(palabra in consulta for palabra in ['usuario', 'usuarios', 'rol', 'roles']):
            stats['usuarios'] = {
                'total': Usuario.objects.count(),
                'activos': Usuario.objects.filter(is_active=True).count(),
                'inactivos': Usuario.objects.filter(is_active=False).count(),
                'por_rol': list(Usuario.objects.values('groups__name').annotate(count=Count('username')))
            }

        # Estadísticas de pagos
        if any(palabra in consulta for palabra in ['pago', 'pagos', 'factura', 'facturas']):
            stats['pagos'] = {
                'total': Pago.objects.count(),
                'completados': Pago.objects.filter(estado='COMPLETADO').count(),
                'pendientes': Pago.objects.filter(estado='PENDIENTE').count(),
                'fallidos': Pago.objects.filter(estado='FALLIDO').count(),
            }
        
        return stats
    
    def _generar_respuesta_estadistica(self, stats: Dict, consulta: str) -> str:
        """Genera una respuesta basada en las estadísticas"""
        respuesta = []
        
        if 'casos' in stats:
            casos_stats = stats['casos']
            respuesta.append(f"📊 **Estadísticas de Casos:**")
            respuesta.append(f"• Total de casos: **{casos_stats['total']}**")
            respuesta.append(f"• Casos abiertos: **{casos_stats['abiertos']}**")
            respuesta.append(f"• Casos cerrados: **{casos_stats['cerrados']}**")
            
            if casos_stats['por_tipo']:
                respuesta.append(f"• **Por tipo:**")
                for tipo in casos_stats['por_tipo'][:3]:
                    respuesta.append(f"  - {tipo['tipoCaso']}: {tipo['count']}")
        
        if 'documentos' in stats:
            docs_stats = stats['documentos']
            respuesta.append(f"\n📄 **Estadísticas de Documentos:**")
            respuesta.append(f"• Total de documentos: **{docs_stats['total']}**")
            respuesta.append(f"• Con palabras clave: **{docs_stats['con_palabras_clave']}**")
            respuesta.append(f"• Sin palabras clave: **{docs_stats['sin_palabras_clave']}**")
            
            if docs_stats['por_tipo']:
                respuesta.append(f"• **Por tipo:**")
                for tipo in docs_stats['por_tipo'][:3]:
                    respuesta.append(f"  - {tipo['tipoDocumento__nombre']}: {tipo['count']}")
        
        if 'actores' in stats:
            actores_stats = stats['actores']
            respuesta.append(f"\n👥 **Estadísticas de Actores:**")
            respuesta.append(f"• Total de actores: **{actores_stats['total']}**")
            respuesta.append(f"• Abogados: **{actores_stats['abogados']}**")
            respuesta.append(f"• Clientes: **{actores_stats['clientes']}**")
            respuesta.append(f"• Asistentes: **{actores_stats['asistentes']}**")
            
            if actores_stats['por_especialidad']:
                respuesta.append(f"• **Especialidades de abogados:**")
                for esp in actores_stats['por_especialidad'][:3]:
                    respuesta.append(f"  - {esp['especialidad']}: {esp['count']}")
        
        if 'usuarios' in stats:
            users_stats = stats['usuarios']
            respuesta.append(f"\n👤 **Estadísticas de Usuarios:**")
            respuesta.append(f"• Total de usuarios: **{users_stats['total']}**")
            respuesta.append(f"• Activos: **{users_stats['activos']}**")
            respuesta.append(f"• Inactivos: **{users_stats['inactivos']}**")

        if 'pagos' in stats:
            pagos_stats = stats['pagos']
            respuesta.append(f"\n💳 **Estadísticas de Pagos:**")
            respuesta.append(f"• Total de pagos: **{pagos_stats['total']}**")
            respuesta.append(f"• Completados: **{pagos_stats['completados']}**")
            respuesta.append(f"• Pendientes: **{pagos_stats['pendientes']}**")
            respuesta.append(f"• Fallidos: **{pagos_stats['fallidos']}**")
        
        return "\n".join(respuesta) if respuesta else "No se encontraron estadísticas relevantes."
    
    def _buscar_informacion_especifica(self, consulta: str) -> Dict[str, Any]:
        """Busca información específica basada en la consulta"""
        resultados = {
            'casos': [],
            'documentos': [],
            'actores': [],
            'respuesta_directa': None
        }
        
        # Buscar casos específicos
        if 'caso' in consulta:
            casos = self._buscar_casos_especificos(consulta)
            resultados['casos'] = casos
            if casos:
                resultados['respuesta_directa'] = self._formatear_casos(casos)
        
        # Buscar documentos específicos
        if 'documento' in consulta:
            documentos = self._buscar_documentos_especificos(consulta)
            resultados['documentos'] = documentos
            if documentos and not resultados['respuesta_directa']:
                resultados['respuesta_directa'] = self._formatear_documentos(documentos)

        # Buscar pagos/especificaciones financieras
        if any(pal in consulta for pal in ['pago', 'pagos', 'factura', 'facturas']):
            pagos = self._buscar_pagos_especificos(consulta)
            resultados['pagos'] = pagos
            if pagos and not resultados['respuesta_directa']:
                # Generar una respuesta directa simple
                primera = pagos[0]
                resultados['respuesta_directa'] = (
                    f"💳 Pago encontrado: monto {primera['monto']} - estado {primera['estado']} - "
                    f"caso {primera.get('caso') or 'N/A'}"
                )
        
        # Buscar actores específicos
        if any(palabra in consulta for palabra in ['abogado', 'cliente', 'asistente', 'actor']):
            actores = self._buscar_actores_especificos(consulta)
            resultados['actores'] = actores
            if actores and not resultados['respuesta_directa']:
                resultados['respuesta_directa'] = self._formatear_actores(actores)
        
        return resultados
    
    def _buscar_casos_especificos(self, consulta: str) -> List[Dict]:
        """Busca casos específicos"""
        casos = []
        
        # Si la consulta es sobre casos abiertos específicamente
        if 'abiertos' in consulta.lower() or 'abierto' in consulta.lower():
            casos_db = Caso.objects.filter(estado='ABIERTO').order_by('-fechaInicio')
        # Si la consulta es sobre casos cerrados específicamente
        elif 'cerrados' in consulta.lower() or 'cerrado' in consulta.lower():
            casos_db = Caso.objects.filter(estado='CERRADO').order_by('-fechaInicio')
        # Buscar por número de caso específico
        elif re.search(r'[a-z]+-\d{4}-\d+', consulta.lower()):
            numero_match = re.search(r'[a-z]+-\d{4}-\d+', consulta.lower())
            numero = numero_match.group()
            casos_db = Caso.objects.filter(nroCaso__icontains=numero)
        # Búsqueda por tipo de caso
        elif any(tipo in consulta.lower() for tipo in ['divorcio', 'robo', 'despido', 'sociedad', 'incumplimiento', 'pensión', 'horas', 'sucesión', 'daños', 'amparo']):
            # Mapear tipos de consulta a tipos reales
            tipo_mapping = {
                'divorcio': 'Divorcio',
                'robo': 'Robo',
                'despido': 'Despido Injustificado',
                'sociedad': 'Sociedad Comercial',
                'incumplimiento': 'Incumplimiento Contractual',
                'pensión': 'Pensión Alimenticia',
                'horas': 'Horas Extras',
                'sucesión': 'Sucesión',
                'daños': 'Daños y Perjuicios',
                'amparo': 'Recurso de Amparo'
            }
            
            casos_db = []
            for palabra, tipo_real in tipo_mapping.items():
                if palabra in consulta.lower():
                    casos_db = Caso.objects.filter(tipoCaso__icontains=tipo_real)
                    break
        else:
            # Búsqueda general limitada
            casos_db = Caso.objects.all().order_by('-fechaInicio')[:10]
        
        for caso in casos_db:
            # Contar documentos del caso
            documentos_count = 0
            expedientes = Expediente.objects.filter(caso=caso)
            for expediente in expedientes:
                carpetas = Carpeta.objects.filter(expediente=expediente)
                for carpeta in carpetas:
                    documentos_count += Documento.objects.filter(carpeta=carpeta).count()
            
            casos.append({
                'id': caso.id,
                'numero': caso.nroCaso,
                'tipo': caso.tipoCaso,
                'estado': caso.estado,
                'fecha_inicio': caso.fechaInicio,
                'descripcion': caso.descripcion,
                'documentos_count': documentos_count
            })
        
        return casos
    
    def _buscar_documentos_especificos(self, consulta: str) -> List[Dict]:
        """Busca documentos específicos"""
        documentos = []
        
        docs_db = Documento.objects.filter(
            Q(nombreDocumento__icontains=consulta) |
            Q(palabraClave__icontains=consulta)
        ).select_related('tipoDocumento', 'carpeta__expediente__caso')[:5]
        
        for doc in docs_db:
            caso_info = None
            if doc.carpeta and doc.carpeta.expediente:
                caso_info = doc.carpeta.expediente.caso.nroCaso
            
            documentos.append({
                'id': doc.id,
                'nombre': doc.nombreDocumento,
                'tipo': doc.tipoDocumento.nombre,
                'fecha': doc.fechaDoc,
                'palabras_clave': doc.palabraClave,
                'caso': caso_info
            })
        
        return documentos
    
    def _buscar_actores_especificos(self, consulta: str) -> List[Dict]:
        """Busca actores específicos"""
        actores = []
        
        # Buscar por nombre
        actores_db = Actor.objects.filter(
            Q(nombres__icontains=consulta) |
            Q(apellidoPaterno__icontains=consulta) |
            Q(apellidoMaterno__icontains=consulta) |
            Q(ci__icontains=consulta)
        )[:5]
        
        for actor in actores_db:
            info_adicional = {}
            
            # Obtener información específica según el tipo
            if actor.tipoActor == 'ABO':
                try:
                    abogado = actor.abogado
                    info_adicional = {
                        'especialidad': abogado.especialidad,
                        'numero_colegiado': abogado.numeroColegiado
                    }
                except:
                    pass
            elif actor.tipoActor == 'CLI':
                try:
                    cliente = actor.cliente
                    info_adicional = {
                        'tipo_cliente': cliente.tipoCliente
                    }
                except:
                    pass
            elif actor.tipoActor == 'ASI':
                try:
                    asistente = actor.asistente
                    info_adicional = {
                        'area': asistente.area
                    }
                except:
                    pass
            
            actores.append({
                'id': actor.id,
                'nombres': actor.nombres,
                'apellido_paterno': actor.apellidoPaterno,
                'apellido_materno': actor.apellidoMaterno,
                'ci': actor.ci,
                'tipo': actor.get_tipoActor_display(),
                'info_adicional': info_adicional
            })
        
        return actores

    def _buscar_pagos_especificos(self, consulta: str) -> List[Dict]:
        """Busca pagos o facturas específicos"""
        pagos = []

        # Buscar por transacción externa
        pagos_db = Pago.objects.none()
        if 'transaccion' in consulta or 'transacción' in consulta or 'transaccion_id' in consulta:
            # Buscar por transaccion_id_externo si aparece
            match = re.search(r'[A-Za-z0-9_-]{6,}', consulta)
            if match:
                pagos_db = Pago.objects.filter(transaccion_id_externo__icontains=match.group())

        # Buscar por número de caso
        if not pagos_db.exists() and re.search(r'[a-z]+-\d{4}-\d+', consulta.lower()):
            numero_match = re.search(r'[a-z]+-\d{4}-\d+', consulta.lower())
            if numero_match:
                pagos_db = Pago.objects.filter(caso__nroCaso__icontains=numero_match.group())

        # Buscar por usuario
        if not pagos_db.exists():
            pagos_db = Pago.objects.filter(
                Q(usuario__username__icontains=consulta) |
                Q(usuario__email__icontains=consulta)
            )[:10]

        for pago in pagos_db:
            pagos.append({
                'id': pago.id,
                'monto': float(pago.monto),
                'fecha': pago.fecha_pago,
                'metodo': pago.metodo_pago,
                'estado': pago.estado,
                'caso': pago.caso.nroCaso if pago.caso else None,
                'usuario': pago.usuario.username if pago.usuario else None
            })

        return pagos

    def _buscar_pagos_general(self, consulta: str) -> List[Dict]:
        """Búsqueda general de pagos (recientes o por palabras clave)"""
        pagos = []

        pagos_db = Pago.objects.all().order_by('-fecha_pago')[:10]
        for pago in pagos_db:
            pagos.append({
                'id': pago.id,
                'monto': float(pago.monto),
                'fecha': pago.fecha_pago,
                'metodo': pago.metodo_pago,
                'estado': pago.estado,
                'caso': pago.caso.nroCaso if pago.caso else None,
                'usuario': pago.usuario.username if pago.usuario else None
            })

        return pagos
    
    def _buscar_casos_general(self, consulta: str) -> List[Dict]:
        """Búsqueda general de casos"""
        return self._buscar_casos_especificos(consulta)
    
    def _buscar_documentos_general(self, consulta: str) -> List[Dict]:
        """Búsqueda general de documentos"""
        return self._buscar_documentos_especificos(consulta)
    
    def _buscar_actores_general(self, consulta: str) -> List[Dict]:
        """Búsqueda general de actores"""
        return self._buscar_actores_especificos(consulta)
    
    def _formatear_casos(self, casos: List[Dict]) -> str:
        """Formatea la información de casos para la respuesta"""
        if not casos:
            return "No se encontraron casos que coincidan con tu búsqueda."
        
        # Determinar el tipo de respuesta basado en la cantidad de casos
        if len(casos) >= 5:
            respuesta = [f"📁 **Se encontraron {len(casos)} casos:**\n"]
        else:
            respuesta = ["📁 **Casos encontrados:**\n"]
        
        for i, caso in enumerate(casos, 1):
            respuesta.append(f"{i}. **{caso['numero']}** - {caso['tipo']}")
            respuesta.append(f"   - Estado: {caso['estado']}")
            respuesta.append(f"   - Fecha: {caso['fecha_inicio'].strftime('%d/%m/%Y') if caso['fecha_inicio'] else 'N/A'}")
            respuesta.append(f"   - Documentos: {caso['documentos_count']}")
            if caso['descripcion']:
                respuesta.append(f"   - Descripción: {caso['descripcion'][:100]}...")
            respuesta.append("")
        
        return "\n".join(respuesta)
    
    def _formatear_documentos(self, documentos: List[Dict]) -> str:
        """Formatea la información de documentos para la respuesta"""
        if not documentos:
            return "No se encontraron documentos que coincidan con tu búsqueda."
        
        respuesta = ["📄 **Documentos encontrados:**\n"]
        
        for doc in documentos:
            respuesta.append(f"• **{doc['nombre']}**")
            respuesta.append(f"  - Tipo: {doc['tipo']}")
            respuesta.append(f"  - Fecha: {doc['fecha'].strftime('%d/%m/%Y') if doc['fecha'] else 'N/A'}")
            if doc['caso']:
                respuesta.append(f"  - Caso: {doc['caso']}")
            if doc['palabras_clave']:
                respuesta.append(f"  - Palabras clave: {doc['palabras_clave']}")
            respuesta.append("")
        
        return "\n".join(respuesta)
    
    def _formatear_actores(self, actores: List[Dict]) -> str:
        """Formatea la información de actores para la respuesta"""
        if not actores:
            return "No se encontraron actores que coincidan con tu búsqueda."
        
        respuesta = ["👥 **Actores encontrados:**\n"]
        
        for actor in actores:
            nombre_completo = f"{actor['nombres']} {actor['apellido_paterno']} {actor['apellido_materno']}"
            respuesta.append(f"• **{nombre_completo}**")
            respuesta.append(f"  - Tipo: {actor['tipo']}")
            respuesta.append(f"  - CI: {actor['ci']}")
            
            if actor['info_adicional']:
                for key, value in actor['info_adicional'].items():
                    respuesta.append(f"  - {key.replace('_', ' ').title()}: {value}")
            respuesta.append("")
        
        return "\n".join(respuesta)
    
    def _buscar_documentos_personales(self, usuario, consulta: str) -> List[Dict]:
        """Busca documentos relacionados con el usuario"""
        documentos = []
        
        # Buscar por usuario creador (si existe el campo)
        # Como no tenemos un campo de usuario creador directo, buscaremos por actor asociado
        try:
            actor_usuario = usuario.actor
            if actor_usuario:
                # Buscar documentos en casos donde el actor está involucrado
                casos_actor = Caso.objects.filter(
                    Q(expedientes__carpetas__documentos__isnull=False)
                ).distinct()
                
                for caso in casos_actor:
                    expedientes = Expediente.objects.filter(caso=caso)
                    for expediente in expedientes:
                        carpetas = Carpeta.objects.filter(expediente=expediente)
                        for carpeta in carpetas:
                            documentos = Documento.objects.filter(carpeta=carpeta)
                            for doc in documentos:
                                documentos.append({
                                    'id': doc.id,
                                    'nombre': doc.nombreDocumento,
                                    'tipo': doc.tipoDocumento.nombre,
                                    'fecha': doc.fechaDoc,
                                    'caso': caso.nroCaso,
                                    'palabras_clave': doc.palabraClave
                                })
        except:
            # Si no hay actor asociado, buscar documentos recientes
            docs_recientes = Documento.objects.all().order_by('-fechaDoc')[:5]
            for doc in docs_recientes:
                documentos.append({
                    'id': doc.id,
                    'nombre': doc.nombreDocumento,
                    'tipo': doc.tipoDocumento.nombre,
                    'fecha': doc.fechaDoc,
                    'caso': doc.carpeta.expediente.caso.nroCaso if doc.carpeta and doc.carpeta.expediente else None,
                    'palabras_clave': doc.palabraClave
                })
        
        return documentos[:10]  # Limitar a 10 documentos
    
    def _buscar_casos_personales(self, usuario, consulta: str) -> List[Dict]:
        """Busca casos relacionados con el usuario"""
        casos = []
        
        try:
            actor_usuario = usuario.actor
            if actor_usuario:
                # Buscar casos donde el actor está involucrado
                casos_db = Caso.objects.filter(
                    Q(expedientes__carpetas__documentos__isnull=False)
                ).distinct()
                
                for caso in casos_db:
                    documentos_count = 0
                    expedientes = Expediente.objects.filter(caso=caso)
                    for expediente in expedientes:
                        carpetas = Carpeta.objects.filter(expediente=expediente)
                        for carpeta in carpetas:
                            documentos_count += Documento.objects.filter(carpeta=carpeta).count()
                    
                    casos.append({
                        'id': caso.id,
                        'numero': caso.nroCaso,
                        'tipo': caso.tipoCaso,
                        'estado': caso.estado,
                        'fecha_inicio': caso.fechaInicio,
                        'descripcion': caso.descripcion,
                        'documentos_count': documentos_count
                    })
        except:
            # Si no hay actor asociado, buscar casos recientes
            casos_recientes = Caso.objects.all().order_by('-fechaInicio')[:5]
            for caso in casos_recientes:
                documentos_count = 0
                expedientes = Expediente.objects.filter(caso=caso)
                for expediente in expedientes:
                    carpetas = Carpeta.objects.filter(expediente=expediente)
                    for carpeta in carpetas:
                        documentos_count += Documento.objects.filter(carpeta=carpeta).count()
                
                casos.append({
                    'id': caso.id,
                    'numero': caso.nroCaso,
                    'tipo': caso.tipoCaso,
                    'estado': caso.estado,
                    'fecha_inicio': caso.fechaInicio,
                    'descripcion': caso.descripcion,
                    'documentos_count': documentos_count
                })
        
        return casos[:10]  # Limitar a 10 casos
    
    def _buscar_informacion_actor_usuario(self, usuario) -> Dict:
        """Busca información del actor asociado al usuario"""
        try:
            actor = usuario.actor
            if not actor:
                return None
            
            info_adicional = {}
            
            # Obtener información específica según el tipo de actor
            if actor.tipoActor == 'ABO':
                try:
                    abogado = actor.abogado
                    info_adicional = {
                        'especialidad': abogado.especialidad,
                        'numero_colegiado': abogado.numeroColegiado,
                        'estado_licencia': abogado.estadoLicencia
                    }
                except:
                    pass
            elif actor.tipoActor == 'CLI':
                try:
                    cliente = actor.cliente
                    info_adicional = {
                        'tipo_cliente': cliente.tipoCliente
                    }
                except:
                    pass
            elif actor.tipoActor == 'ASI':
                try:
                    asistente = actor.asistente
                    info_adicional = {
                        'area': asistente.area
                    }
                except:
                    pass
            
            return {
                'id': actor.id,
                'nombres': actor.nombres,
                'apellido_paterno': actor.apellidoPaterno,
                'apellido_materno': actor.apellidoMaterno,
                'ci': actor.ci,
                'tipo': actor.get_tipoActor_display(),
                'telefono': actor.telefono,
                'email': actor.email,
                'info_adicional': info_adicional
            }
        except:
            return None
    
    def _formatear_documentos_personales(self, documentos: List[Dict], usuario) -> str:
        """Formatea documentos personales para la respuesta"""
        if not documentos:
            return f"📄 No se encontraron documentos para {usuario.username}."
        
        respuesta = [f"📄 **Documentos relacionados con {usuario.username}:**\n"]
        
        for doc in documentos:
            respuesta.append(f"• **{doc['nombre']}**")
            respuesta.append(f"  - Tipo: {doc['tipo']}")
            respuesta.append(f"  - Fecha: {doc['fecha'].strftime('%d/%m/%Y') if doc['fecha'] else 'N/A'}")
            if doc['caso']:
                respuesta.append(f"  - Caso: {doc['caso']}")
            if doc['palabras_clave']:
                respuesta.append(f"  - Palabras clave: {doc['palabras_clave']}")
            respuesta.append("")
        
        return "\n".join(respuesta)
    
    def _formatear_casos_personales(self, casos: List[Dict], usuario) -> str:
        """Formatea casos personales para la respuesta"""
        if not casos:
            return f"📁 No se encontraron casos para {usuario.username}."
        
        respuesta = [f"📁 **Casos relacionados con {usuario.username}:**\n"]
        
        for caso in casos:
            respuesta.append(f"• **{caso['numero']}** - {caso['tipo']}")
            respuesta.append(f"  - Estado: {caso['estado']}")
            respuesta.append(f"  - Fecha: {caso['fecha_inicio'].strftime('%d/%m/%Y') if caso['fecha_inicio'] else 'N/A'}")
            respuesta.append(f"  - Documentos: {caso['documentos_count']}")
            if caso['descripcion']:
                respuesta.append(f"  - Descripción: {caso['descripcion'][:100]}...")
            respuesta.append("")
        
        return "\n".join(respuesta)
    
    def _formatear_informacion_actor(self, actor_info: Dict, usuario) -> str:
        """Formatea información del actor para la respuesta"""
        if not actor_info:
            return f"👤 No se encontró información del actor para {usuario.username}."
        
        respuesta = [f"👤 **Información de {usuario.username}:**\n"]
        respuesta.append(f"• **Nombre:** {actor_info['nombres']} {actor_info['apellido_paterno']} {actor_info['apellido_materno']}")
        respuesta.append(f"• **CI:** {actor_info['ci']}")
        respuesta.append(f"• **Tipo:** {actor_info['tipo']}")
        
        if actor_info['telefono']:
            respuesta.append(f"• **Teléfono:** {actor_info['telefono']}")
        if actor_info['email']:
            respuesta.append(f"• **Email:** {actor_info['email']}")
        
        if actor_info['info_adicional']:
            respuesta.append(f"• **Información adicional:**")
            for key, value in actor_info['info_adicional'].items():
                respuesta.append(f"  - {key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(respuesta)
