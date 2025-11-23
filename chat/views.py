from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.db import transaction
import json
import time
from datetime import datetime

from .models import Conversacion, Mensaje, ConsultaDocumento, ConfiguracionIA
from .services import AsistenteIAService
from .suggestion_service import SuggestionService


class ChatView(LoginRequiredMixin, TemplateView):
    """
    Vista principal del chat
    """
    template_name = 'chat/chat.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener conversaciones del usuario
        conversaciones = Conversacion.objects.filter(
            usuario=self.request.user,
            activa=True
        ).order_by('-fecha_actualizacion')[:10]
        
        context['conversaciones'] = conversaciones
        
        # Obtener la conversación activa si se especifica
        conversacion_id = self.request.GET.get('conversacion_id')
        if conversacion_id:
            try:
                conversacion = get_object_or_404(
                    Conversacion,
                    id=conversacion_id,
                    usuario=self.request.user
                )
                context['conversacion_activa'] = conversacion
                context['mensajes'] = conversacion.mensajes.all().order_by('fecha_envio')
            except:
                pass
        
        return context


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def enviar_mensaje(request):
    """
    API endpoint para enviar mensajes al chat
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    
    try:
        data = json.loads(request.body)
        mensaje_usuario = data.get('mensaje', '').strip()
        conversacion_id = data.get('conversacion_id')
        
        if not mensaje_usuario:
            return JsonResponse({'error': 'Mensaje vacío'}, status=400)
        
        # Obtener o crear conversación
        if conversacion_id:
            conversacion = get_object_or_404(
                Conversacion,
                id=conversacion_id,
                usuario=request.user
            )
        else:
            # Crear nueva conversación
            conversacion = Conversacion.objects.create(
                usuario=request.user,
                titulo=mensaje_usuario[:50] + "..." if len(mensaje_usuario) > 50 else mensaje_usuario
            )
        
        # Guardar mensaje del usuario
        mensaje_usuario_obj = Mensaje.objects.create(
            conversacion=conversacion,
            tipo='usuario',
            contenido=mensaje_usuario
        )
        
        # Procesar con IA
        inicio_tiempo = time.time()
        respuesta_ia = procesar_consulta_ia(request.user, mensaje_usuario, conversacion)
        tiempo_respuesta = time.time() - inicio_tiempo
        
        # Guardar respuesta de la IA
        mensaje_ia_obj = Mensaje.objects.create(
            conversacion=conversacion,
            tipo='asistente',
            contenido=respuesta_ia['respuesta'],
            tiempo_respuesta=tiempo_respuesta,
            documentos_consultados=respuesta_ia.get('documentos_consultados', []),
            entidades_extraidas=respuesta_ia.get('entidades_extraidas', [])
        )
        
        # Actualizar fecha de conversación
        conversacion.fecha_actualizacion = datetime.now()
        conversacion.save()
        
        return JsonResponse({
            'success': True,
            'mensaje_usuario': {
                'id': mensaje_usuario_obj.id,
                'contenido': mensaje_usuario_obj.contenido,
                'fecha': mensaje_usuario_obj.fecha_envio.isoformat(),
                'tipo': mensaje_usuario_obj.tipo
            },
            'mensaje_ia': {
                'id': mensaje_ia_obj.id,
                'contenido': mensaje_ia_obj.contenido,
                'fecha': mensaje_ia_obj.fecha_envio.isoformat(),
                'tipo': mensaje_ia_obj.tipo,
                'tiempo_respuesta': mensaje_ia_obj.tiempo_respuesta,
                'documentos_consultados': mensaje_ia_obj.documentos_consultados
            },
            'conversacion_id': conversacion.id
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)


def procesar_consulta_ia(usuario, consulta, conversacion):
    """
    Procesa la consulta del usuario usando IA
    """
    try:
        # Inicializar servicio de IA
        servicio_ia = AsistenteIAService()
        
        # Analizar la consulta
        analisis = servicio_ia.analizar_consulta(consulta)
        
        # Buscar información relevante
        contexto = []
        documentos_consultados = []
        
        if analisis['tipo'] == 'documento':
            resultados = servicio_ia.buscar_documentos(consulta, usuario)
            contexto.extend(resultados)
            documentos_consultados = [r['objeto'].id for r in resultados if r['tipo'] == 'documento']
        
        elif analisis['tipo'] == 'actor':
            resultados = servicio_ia.buscar_actores(consulta)
            contexto.extend(resultados)
        
        elif analisis['tipo'] == 'caso':
            resultados = servicio_ia.buscar_casos(consulta)
            contexto.extend(resultados)
        
        else:
            # Búsqueda general
            resultados_docs = servicio_ia.buscar_documentos(consulta, usuario)
            resultados_actores = servicio_ia.buscar_actores(consulta)
            resultados_casos = servicio_ia.buscar_casos(consulta)
            
            contexto.extend(resultados_docs[:3])
            contexto.extend(resultados_actores[:2])
            contexto.extend(resultados_casos[:2])
            
            documentos_consultados = [r['objeto'].id for r in resultados_docs if r['tipo'] == 'documento']
        
        # Obtener historial de conversación
        mensajes_anteriores = conversacion.mensajes.all().order_by('-fecha_envio')[:6]
        historial = []
        for msg in reversed(mensajes_anteriores):
            if msg.tipo in ['usuario', 'asistente']:
                historial.append(msg.contenido)
        
        # Generar respuesta con IA
        respuesta = servicio_ia.generar_respuesta_ia(consulta, contexto, historial, usuario)
        
        return {
            'respuesta': respuesta,
            'documentos_consultados': documentos_consultados,
            'entidades_extraidas': analisis['entidades'],
            'tipo_consulta': analisis['tipo']
        }
        
    except Exception as e:
        return {
            'respuesta': f"Lo siento, hubo un error al procesar tu consulta: {str(e)}",
            'documentos_consultados': [],
            'entidades_extraidas': [],
            'tipo_consulta': 'error'
        }


@login_required
@require_http_methods(["GET"])
def obtener_conversacion(request, conversacion_id):
    """
    Obtiene los mensajes de una conversación específica
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    
    try:
        conversacion = get_object_or_404(
            Conversacion,
            id=conversacion_id,
            usuario=request.user
        )
        
        mensajes = conversacion.mensajes.all().order_by('fecha_envio')
        
        mensajes_data = []
        for mensaje in mensajes:
            mensajes_data.append({
                'id': mensaje.id,
                'contenido': mensaje.contenido,
                'tipo': mensaje.tipo,
                'fecha': mensaje.fecha_envio.isoformat(),
                'tiempo_respuesta': mensaje.tiempo_respuesta,
                'documentos_consultados': mensaje.documentos_consultados
            })
        
        return JsonResponse({
            'success': True,
            'conversacion': {
                'id': conversacion.id,
                'titulo': conversacion.titulo,
                'fecha_creacion': conversacion.fecha_creacion.isoformat(),
                'fecha_actualizacion': conversacion.fecha_actualizacion.isoformat()
            },
            'mensajes': mensajes_data
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)


@login_required
@require_http_methods(["POST"])
def crear_conversacion(request):
    """
    Crea una nueva conversación
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    
    try:
        conversacion = Conversacion.objects.create(
            usuario=request.user,
            titulo="Nueva conversación"
        )
        
        return JsonResponse({
            'success': True,
            'conversacion': {
                'id': conversacion.id,
                'titulo': conversacion.titulo,
                'fecha_creacion': conversacion.fecha_creacion.isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)


@login_required
@require_http_methods(["DELETE"])
def eliminar_conversacion(request, conversacion_id):
    """
    Elimina una conversación
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    
    try:
        conversacion = get_object_or_404(
            Conversacion,
            id=conversacion_id,
            usuario=request.user
        )
        
        conversacion.activa = False
        conversacion.save()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)


@login_required
@require_http_methods(["GET"])
def obtener_conversaciones(request):
    """
    Obtiene las conversaciones del usuario
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    
    try:
        conversaciones = Conversacion.objects.filter(
            usuario=request.user,
            activa=True
        ).order_by('-fecha_actualizacion')
        
        conversaciones_data = []
        for conv in conversaciones:
            ultimo_mensaje = conv.mensajes.last()
            conversaciones_data.append({
                'id': conv.id,
                'titulo': conv.titulo,
                'fecha_creacion': conv.fecha_creacion.isoformat(),
                'fecha_actualizacion': conv.fecha_actualizacion.isoformat(),
                'ultimo_mensaje': ultimo_mensaje.contenido if ultimo_mensaje else None,
                'cantidad_mensajes': conv.mensajes.count()
            })
        
        return JsonResponse({
            'success': True,
            'conversaciones': conversaciones_data
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)


@login_required
@require_http_methods(["GET"])
def obtener_sugerencias(request):
    """
    Obtiene sugerencias inteligentes basadas en datos reales de la DB
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    
    try:
        suggestion_service = SuggestionService()
        conversacion_id = request.GET.get('conversacion_id')
        
        # Obtener sugerencias contextuales
        sugerencias = suggestion_service.get_contextual_suggestions(
            request.user, 
            conversacion_id
        )
        
        return JsonResponse({
            'success': True,
            'sugerencias': sugerencias
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)