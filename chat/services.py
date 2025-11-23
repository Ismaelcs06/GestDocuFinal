import openai
import os
import json
import time
from typing import List, Dict, Any, Optional
from django.conf import settings
from django.db.models import Q
from casos.models import Caso, Expediente, Carpeta
from documentos.models import Documento, TipoDocumento, EtapaProcesal
from actores.models import Actor, Abogado, Cliente, Asistente
from seguridad.models import Usuario
from .database_service import DatabaseQueryService


class AsistenteIAService:
    """
    Servicio para manejar la integración con OpenAI y búsquedas inteligentes
    """
    
class AsistenteIAService:
    def __init__(self):
        # Usa settings para la API key
        self.client = openai.OpenAI(
            api_key=getattr(settings, "OPENAI_API_KEY", None)
        )
        self.modelo = getattr(settings, "OPENAI_MODEL", "gpt-3.5-turbo")
        self.temperatura = float(getattr(settings, "OPENAI_TEMPERATURE", 0.7))
        self.max_tokens = int(getattr(settings, "OPENAI_MAX_TOKENS", 1000))
        self.db_service = DatabaseQueryService()
    
    def buscar_documentos(self, consulta: str, usuario: Usuario) -> List[Dict[str, Any]]:
        """
        Busca documentos relevantes basándose en la consulta del usuario
        """
        resultados = []
        
        # Búsqueda por nombre de documento
        documentos_nombre = Documento.objects.filter(
            Q(nombreDocumento__icontains=consulta) |
            Q(palabraClave__icontains=consulta)
        ).select_related('carpeta__expediente__caso', 'tipoDocumento', 'etapaProcesal')
        
        for doc in documentos_nombre:
            resultados.append({
                'tipo': 'documento',
                'objeto': doc,
                'relevancia': 0.9,
                'razon': f"Documento encontrado por nombre: {doc.nombreDocumento}"
            })
        
        # Búsqueda por tipo de documento
        tipos_doc = TipoDocumento.objects.filter(
            nombre__icontains=consulta
        )
        for tipo in tipos_doc:
            docs_tipo = Documento.objects.filter(tipoDocumento=tipo)
            for doc in docs_tipo:
                resultados.append({
                    'tipo': 'documento',
                    'objeto': doc,
                    'relevancia': 0.7,
                    'razon': f"Documento de tipo: {tipo.nombre}"
                })
        
        # Búsqueda por casos
        casos = Caso.objects.filter(
            Q(nroCaso__icontains=consulta) |
            Q(tipoCaso__icontains=consulta) |
            Q(descripcion__icontains=consulta)
        )
        
        for caso in casos:
            # Buscar documentos del caso
            expedientes = Expediente.objects.filter(caso=caso)
            for exp in expedientes:
                carpetas = Carpeta.objects.filter(expediente=exp)
                for carpeta in carpetas:
                    docs = Documento.objects.filter(carpeta=carpeta)
                    for doc in docs:
                        resultados.append({
                            'tipo': 'documento',
                            'objeto': doc,
                            'relevancia': 0.8,
                            'razon': f"Documento del caso {caso.nroCaso}: {caso.tipoCaso}"
                        })
        
        # Eliminar duplicados y ordenar por relevancia
        resultados_unicos = {}
        for resultado in resultados:
            doc_id = resultado['objeto'].id
            if doc_id not in resultados_unicos or resultados_unicos[doc_id]['relevancia'] < resultado['relevancia']:
                resultados_unicos[doc_id] = resultado
        
        return sorted(resultados_unicos.values(), key=lambda x: x['relevancia'], reverse=True)[:10]
    
    def buscar_actores(self, consulta: str) -> List[Dict[str, Any]]:
        """
        Busca actores relevantes basándose en la consulta
        """
        resultados = []
        
        # Búsqueda por nombre
        actores = Actor.objects.filter(
            Q(nombres__icontains=consulta) |
            Q(apellidoPaterno__icontains=consulta) |
            Q(apellidoMaterno__icontains=consulta) |
            Q(ci__icontains=consulta)
        ).select_related('usuario')
        
        for actor in actores:
            resultados.append({
                'tipo': 'actor',
                'objeto': actor,
                'relevancia': 0.9,
                'razon': f"Actor encontrado: {actor.nombres} {actor.apellidoPaterno}"
            })
        
        # Búsqueda por tipo de actor
        if 'abogado' in consulta.lower():
            abogados = Abogado.objects.select_related('actor').all()
            for abogado in abogados:
                resultados.append({
                    'tipo': 'actor',
                    'objeto': abogado.actor,
                    'relevancia': 0.8,
                    'razon': f"Abogado: {abogado.actor.nombres} {abogado.actor.apellidoPaterno}"
                })
        
        if 'cliente' in consulta.lower():
            clientes = Cliente.objects.select_related('actor').all()
            for cliente in clientes:
                resultados.append({
                    'tipo': 'actor',
                    'objeto': cliente.actor,
                    'relevancia': 0.8,
                    'razon': f"Cliente: {cliente.actor.nombres} {cliente.actor.apellidoPaterno}"
                })
        
        return sorted(resultados, key=lambda x: x['relevancia'], reverse=True)[:5]
    
    def buscar_casos(self, consulta: str) -> List[Dict[str, Any]]:
        """
        Busca casos relevantes basándose en la consulta
        """
        resultados = []
        
        casos = Caso.objects.filter(
            Q(nroCaso__icontains=consulta) |
            Q(tipoCaso__icontains=consulta) |
            Q(descripcion__icontains=consulta)
        )
        
        for caso in casos:
            resultados.append({
                'tipo': 'caso',
                'objeto': caso,
                'relevancia': 0.9,
                'razon': f"Caso encontrado: {caso.nroCaso} - {caso.tipoCaso}"
            })
        
        return sorted(resultados, key=lambda x: x['relevancia'], reverse=True)[:5]
    
    def generar_respuesta_ia(self, consulta: str, contexto: List[Dict[str, Any]], conversacion_historial: List[str] = None, usuario=None) -> str:
        """
        Genera una respuesta usando OpenAI basándose en la consulta y el contexto encontrado
        """
        try:
            # Usar el nuevo servicio de base de datos para obtener información específica
            db_resultados = self.db_service.consultar_informacion(consulta, usuario)
            
            # Si hay una respuesta directa de la base de datos, usarla
            if db_resultados.get('respuesta_directa'):
                return db_resultados['respuesta_directa']
            
            # Construir el contexto del sistema
            contexto_sistema = self._construir_contexto_sistema()
            
            # Construir el contexto de la consulta con los resultados de la DB
            contexto_consulta = self._construir_contexto_mejorado(db_resultados)
            
            # Construir el historial de conversación
            historial = self._construir_historial(conversacion_historial) if conversacion_historial else []
            
            # Preparar mensajes para OpenAI
            mensajes = [
                {"role": "system", "content": contexto_sistema}
            ] + historial + [
                {"role": "user", "content": f"{consulta}\n\nInformación encontrada en la base de datos:\n{contexto_consulta}"}
            ]
            
            # Llamar a OpenAI
            response = self.client.chat.completions.create(
                model=self.modelo,
                messages=mensajes,
                temperature=self.temperatura,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = str(e)
            
            # Mensajes de error más específicos
            if "API key" in error_msg or "authentication" in error_msg:
                return "⚠️ Error de configuración: No se ha configurado la API key de OpenAI. Por favor, revisa el archivo .env y agrega OPENAI_API_KEY=tu-api-key-aqui"
            elif "quota" in error_msg or "billing" in error_msg:
                return "⚠️ Error de crédito: Tu cuenta de OpenAI no tiene crédito suficiente. Ve a https://platform.openai.com/account/billing para agregar crédito."
            elif "rate limit" in error_msg:
                return "⚠️ Límite de velocidad: Has excedido el límite de solicitudes. Espera unos momentos antes de intentar nuevamente."
            else:
                return f"⚠️ Error al procesar tu consulta: {error_msg}"
    
    def _construir_contexto_sistema(self) -> str:
        """
        Construye el contexto del sistema para el asistente IA
        """
        return """Eres un asistente legal especializado en gestión documental para el sistema GestDocSi2.

REGLAS CRÍTICAS:
- NUNCA inventes información que no esté en el contexto proporcionado
- SIEMPRE usa únicamente los datos reales de la base de datos que se te proporcionan
- Si no hay información suficiente en el contexto, di claramente "No se encontró información específica"
- NO generes nombres, fechas, números de caso o información que no esté en los datos reales

Tu función es ayudar a los usuarios a:
1. Buscar y encontrar documentos específicos
2. Analizar información de casos legales
3. Proporcionar información sobre actores del sistema (abogados, clientes, asistentes)
4. Responder preguntas sobre el estado de casos y expedientes

INSTRUCCIONES:
- Siempre responde en español
- Sé profesional y preciso
- Usa ÚNICAMENTE la información que se te proporciona en el contexto
- Si encuentras información relevante en el contexto, úsala para dar una respuesta completa
- Si no encuentras información específica, indícalo claramente
- Estructura tu respuesta de manera clara y organizada
- Incluye referencias específicas a documentos, casos o actores cuando estén disponibles en el contexto

FORMATO DE RESPUESTA:
- Usa viñetas para organizar información
- Incluye números de caso, nombres de documentos y fechas SOLO cuando estén en el contexto
- Proporciona referencias específicas SOLO cuando estén disponibles en los datos reales"""
    
    def _construir_contexto_consulta(self, contexto: List[Dict[str, Any]]) -> str:
        """
        Construye el contexto de la consulta basándose en los resultados encontrados
        """
        if not contexto:
            return "No se encontró información relevante en la base de datos."
        
        contexto_texto = "Información encontrada:\n\n"
        
        for item in contexto:
            if item['tipo'] == 'documento':
                doc = item['objeto']
                contexto_texto += f"📄 DOCUMENTO: {doc.nombreDocumento}\n"
                contexto_texto += f"   - Tipo: {doc.tipoDocumento.nombre}\n"
                contexto_texto += f"   - Caso: {doc.carpeta.expediente.caso.nroCaso}\n"
                contexto_texto += f"   - Fecha: {doc.fechaDoc}\n"
                contexto_texto += f"   - Estado: {doc.estado}\n"
                if doc.palabraClave:
                    contexto_texto += f"   - Palabras clave: {doc.palabraClave}\n"
                contexto_texto += "\n"
            
            elif item['tipo'] == 'actor':
                actor = item['objeto']
                contexto_texto += f"👤 ACTOR: {actor.nombres} {actor.apellidoPaterno}\n"
                contexto_texto += f"   - Tipo: {actor.get_tipoActor_display()}\n"
                contexto_texto += f"   - CI: {actor.ci}\n"
                contexto_texto += f"   - Estado: {actor.estadoActor}\n"
                if actor.telefono:
                    contexto_texto += f"   - Teléfono: {actor.telefono}\n"
                contexto_texto += "\n"
            
            elif item['tipo'] == 'caso':
                caso = item['objeto']
                contexto_texto += f"⚖️ CASO: {caso.nroCaso}\n"
                contexto_texto += f"   - Tipo: {caso.tipoCaso}\n"
                contexto_texto += f"   - Estado: {caso.estado}\n"
                contexto_texto += f"   - Prioridad: {caso.prioridad}\n"
                contexto_texto += f"   - Fecha inicio: {caso.fechaInicio}\n"
                if caso.descripcion:
                    contexto_texto += f"   - Descripción: {caso.descripcion}\n"
                contexto_texto += "\n"
        
        return contexto_texto
    
    def _construir_contexto_mejorado(self, db_resultados: Dict[str, Any]) -> str:
        """
        Construye el contexto mejorado con los resultados de la base de datos
        """
        # Si hay una respuesta directa de la base de datos, usarla como contexto principal
        if db_resultados.get('respuesta_directa'):
            return f"**Información encontrada en la base de datos:**\n{db_resultados['respuesta_directa']}"
        
        contexto_texto = ""
        
        # Agregar estadísticas si existen
        if db_resultados.get('estadisticas'):
            stats = db_resultados['estadisticas']
            contexto_texto += "📊 ESTADÍSTICAS DEL SISTEMA:\n"
            
            if 'casos' in stats:
                casos_stats = stats['casos']
                contexto_texto += f"• Total de casos: {casos_stats['total']}\n"
                contexto_texto += f"• Casos abiertos: {casos_stats['abiertos']}\n"
                contexto_texto += f"• Casos cerrados: {casos_stats['cerrados']}\n"
            
            if 'documentos' in stats:
                docs_stats = stats['documentos']
                contexto_texto += f"• Total de documentos: {docs_stats['total']}\n"
                contexto_texto += f"• Con palabras clave: {docs_stats['con_palabras_clave']}\n"
            
            if 'actores' in stats:
                actores_stats = stats['actores']
                contexto_texto += f"• Total de actores: {actores_stats['total']}\n"
                contexto_texto += f"• Abogados: {actores_stats['abogados']}\n"
                contexto_texto += f"• Clientes: {actores_stats['clientes']}\n"
                contexto_texto += f"• Asistentes: {actores_stats['asistentes']}\n"
            
            contexto_texto += "\n"
        
        # Agregar casos encontrados
        if db_resultados.get('casos'):
            contexto_texto += "📁 CASOS ENCONTRADOS:\n"
            for caso in db_resultados['casos']:
                contexto_texto += f"• {caso['numero']} - {caso['tipo']}\n"
                contexto_texto += f"  - Estado: {caso['estado']}\n"
                contexto_texto += f"  - Fecha: {caso['fecha_inicio'].strftime('%d/%m/%Y') if caso['fecha_inicio'] else 'N/A'}\n"
                contexto_texto += f"  - Documentos: {caso['documentos_count']}\n"
            contexto_texto += "\n"
        
        # Agregar documentos encontrados
        if db_resultados.get('documentos'):
            contexto_texto += "📄 DOCUMENTOS ENCONTRADOS:\n"
            for doc in db_resultados['documentos']:
                contexto_texto += f"• {doc['nombre']}\n"
                contexto_texto += f"  - Tipo: {doc['tipo']}\n"
                contexto_texto += f"  - Fecha: {doc['fecha'].strftime('%d/%m/%Y') if doc['fecha'] else 'N/A'}\n"
                if doc['caso']:
                    contexto_texto += f"  - Caso: {doc['caso']}\n"
            contexto_texto += "\n"
        
        # Agregar actores encontrados
        if db_resultados.get('actores'):
            contexto_texto += "👥 ACTORES ENCONTRADOS:\n"
            for actor in db_resultados['actores']:
                nombre_completo = f"{actor['nombres']} {actor['apellido_paterno']} {actor['apellido_materno']}"
                contexto_texto += f"• {nombre_completo}\n"
                contexto_texto += f"  - Tipo: {actor['tipo']}\n"
                contexto_texto += f"  - CI: {actor['ci']}\n"
                if actor['info_adicional']:
                    for key, value in actor['info_adicional'].items():
                        contexto_texto += f"  - {key.replace('_', ' ').title()}: {value}\n"
            contexto_texto += "\n"
        
        return contexto_texto
    
    def _construir_historial(self, historial: List[str]) -> List[Dict[str, str]]:
        """
        Construye el historial de conversación para OpenAI
        """
        mensajes = []
        for i, mensaje in enumerate(historial):
            role = "user" if i % 2 == 0 else "assistant"
            mensajes.append({"role": role, "content": mensaje})
        return mensajes
    
    def analizar_consulta(self, consulta: str) -> Dict[str, Any]:
        """
        Analiza la consulta del usuario para determinar el tipo de búsqueda
        """
        consulta_lower = consulta.lower()
        
        # Detectar tipo de consulta
        if any(palabra in consulta_lower for palabra in ['documento', 'contrato', 'factura', 'escritura', 'certificado']):
            tipo = 'documento'
        elif any(palabra in consulta_lower for palabra in ['abogado', 'cliente', 'asistente', 'persona']):
            tipo = 'actor'
        elif any(palabra in consulta_lower for palabra in ['caso', 'expediente', 'proceso', 'demanda']):
            tipo = 'caso'
        else:
            tipo = 'general'
        
        # Extraer entidades
        entidades = []
        if 'contrato' in consulta_lower:
            entidades.append('contrato')
        if 'factura' in consulta_lower:
            entidades.append('factura')
        if 'abogado' in consulta_lower:
            entidades.append('abogado')
        if 'cliente' in consulta_lower:
            entidades.append('cliente')
        
        return {
            'tipo': tipo,
            'entidades': entidades,
            'consulta_original': consulta
        }
