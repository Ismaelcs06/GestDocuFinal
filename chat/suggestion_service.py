from django.contrib.auth import get_user_model
from casos.models import Caso, Expediente, Carpeta
from documentos.models import Documento, TipoDocumento, EtapaProcesal
from actores.models import Actor, Abogado, Cliente, Asistente
from seguridad.models import Usuario
from datetime import datetime, timedelta
import random

User = get_user_model()

class SuggestionService:
    """
    Servicio para generar sugerencias inteligentes basadas en datos reales de la DB
    """
    
    def __init__(self):
        pass
    
    def get_smart_suggestions(self, user=None):
        """
        Genera sugerencias inteligentes basadas en los datos reales disponibles
        """
        suggestions = []
        
        # Obtener datos reales de la base de datos
        casos_data = self._get_casos_data()
        documentos_data = self._get_documentos_data()
        actores_data = self._get_actores_data()
        
        # Generar sugerencias basadas en datos reales
        suggestions.extend(self._generate_casos_suggestions(casos_data))
        suggestions.extend(self._generate_documentos_suggestions(documentos_data))
        suggestions.extend(self._generate_actores_suggestions(actores_data))
        suggestions.extend(self._generate_general_suggestions())
        
        # Mezclar y limitar sugerencias
        random.shuffle(suggestions)
        return suggestions[:8]  # Máximo 8 sugerencias
    
    def _get_casos_data(self):
        """Obtiene datos reales de casos"""
        casos = Caso.objects.all()
        return {
            'total': casos.count(),
            'tipos': list(casos.values_list('tipoCaso', flat=True).distinct()),
            'estados': list(casos.values_list('estado', flat=True).distinct()),
            'casos_recientes': list(casos.order_by('-fechaInicio')[:5].values_list('nroCaso', flat=True)),
            'casos_abiertos': casos.filter(estado='ABIERTO').count(),
            'casos_cerrados': casos.filter(estado='CERRADO').count(),
        }
    
    def _get_documentos_data(self):
        """Obtiene datos reales de documentos"""
        documentos = Documento.objects.all()
        tipos_doc = TipoDocumento.objects.all()
        return {
            'total': documentos.count(),
            'tipos': list(tipos_doc.values_list('nombre', flat=True)),
            'documentos_recientes': list(documentos.order_by('-fechaDoc')[:5].values_list('nombreDocumento', flat=True)),
            'con_palabras_clave': documentos.exclude(palabraClave='').count(),
        }
    
    def _get_actores_data(self):
        """Obtiene datos reales de actores"""
        actores = Actor.objects.all()
        abogados = Abogado.objects.all()
        clientes = Cliente.objects.all()
        asistentes = Asistente.objects.all()
        
        return {
            'total': actores.count(),
            'abogados': list(abogados.select_related('actor').values_list('actor__nombres', 'actor__apellidoPaterno', 'especialidad')),
            'clientes': list(clientes.select_related('actor').values_list('actor__nombres', 'actor__apellidoPaterno', 'tipoCliente')),
            'asistentes': list(asistentes.select_related('actor').values_list('actor__nombres', 'actor__apellidoPaterno', 'area')),
            'especialidades': list(abogados.values_list('especialidad', flat=True).distinct()),
        }
    
    def _generate_casos_suggestions(self, casos_data):
        """Genera sugerencias relacionadas con casos"""
        suggestions = []
        
        if casos_data['total'] > 0:
            # Sugerencias generales de casos
            suggestions.append({
                'text': f"¿Cuántos casos hay en total? (Actualmente hay {casos_data['total']})",
                'category': 'casos',
                'icon': '📊'
            })
            
            if casos_data['casos_abiertos'] > 0:
                suggestions.append({
                    'text': f"¿Cuántos casos están abiertos? (Actualmente {casos_data['casos_abiertos']})",
                    'category': 'casos',
                    'icon': '⚖️'
                })
            
            if casos_data['tipos']:
                tipo_ejemplo = casos_data['tipos'][0]
                suggestions.append({
                    'text': f"¿Cuántos casos de '{tipo_ejemplo}' hay?",
                    'category': 'casos',
                    'icon': '🔍'
                })
            
            if casos_data['casos_recientes']:
                caso_ejemplo = casos_data['casos_recientes'][0]
                suggestions.append({
                    'text': f"¿Qué documentos tiene el caso {caso_ejemplo}?",
                    'category': 'casos',
                    'icon': '📁'
                })
        
        return suggestions
    
    def _generate_documentos_suggestions(self, documentos_data):
        """Genera sugerencias relacionadas con documentos"""
        suggestions = []
        
        if documentos_data['total'] > 0:
            # Sugerencias generales de documentos
            suggestions.append({
                'text': f"¿Cuántos documentos hay en total? (Actualmente {documentos_data['total']})",
                'category': 'documentos',
                'icon': '📄'
            })
            
            if documentos_data['tipos']:
                tipo_ejemplo = documentos_data['tipos'][0]
                suggestions.append({
                    'text': f"¿Cuántos documentos de tipo '{tipo_ejemplo}' hay?",
                    'category': 'documentos',
                    'icon': '🔍'
                })
            
            if documentos_data['documentos_recientes']:
                doc_ejemplo = documentos_data['documentos_recientes'][0]
                suggestions.append({
                    'text': f"¿En qué caso está el documento '{doc_ejemplo}'?",
                    'category': 'documentos',
                    'icon': '🔗'
                })
        
        return suggestions
    
    def _generate_actores_suggestions(self, actores_data):
        """Genera sugerencias relacionadas con actores"""
        suggestions = []
        
        if actores_data['total'] > 0:
            # Sugerencias generales de actores
            suggestions.append({
                'text': f"¿Cuántos actores hay en total? (Actualmente {actores_data['total']})",
                'category': 'actores',
                'icon': '👥'
            })
            
            if actores_data['abogados']:
                abogado = actores_data['abogados'][0]
                nombre = f"{abogado[0]} {abogado[1]}"
                suggestions.append({
                    'text': f"¿Cuál es la especialidad del abogado {nombre}?",
                    'category': 'actores',
                    'icon': '⚖️'
                })
            
            if actores_data['especialidades']:
                especialidad = actores_data['especialidades'][0]
                suggestions.append({
                    'text': f"¿Qué abogados tienen especialidad en '{especialidad}'?",
                    'category': 'actores',
                    'icon': '🔍'
                })
            
            if actores_data['clientes']:
                cliente = actores_data['clientes'][0]
                nombre = f"{cliente[0]} {cliente[1]}"
                suggestions.append({
                    'text': f"¿Qué tipo de cliente es {nombre}?",
                    'category': 'actores',
                    'icon': '👤'
                })
        
        return suggestions
    
    def _generate_general_suggestions(self):
        """Genera sugerencias generales del sistema"""
        return [
            {
                'text': "¿Cuál es el caso con más documentos?",
                'category': 'analisis',
                'icon': '📈'
            },
            {
                'text': "¿Qué abogados están activos en el sistema?",
                'category': 'actores',
                'icon': '✅'
            },
            {
                'text': "¿Cuántos expedientes hay abiertos?",
                'category': 'casos',
                'icon': '📂'
            },
            {
                'text': "¿Qué tipos de documentos existen en el sistema?",
                'category': 'documentos',
                'icon': '📋'
            }
        ]
    
    def get_contextual_suggestions(self, user, current_conversation=None):
        """
        Genera sugerencias contextuales basadas en el usuario y conversación actual
        """
        suggestions = []
        
        # Si el usuario tiene un actor asociado
        try:
            actor = user.actor
            if actor.tipoActor == 'ABO':  # Abogado
                suggestions.extend([
                    {
                        'text': f"¿Cuáles son mis casos asignados?",
                        'category': 'personal',
                        'icon': '👨‍💼'
                    },
                    {
                        'text': f"¿Qué documentos he creado recientemente?",
                        'category': 'personal',
                        'icon': '📝'
                    }
                ])
            elif actor.tipoActor == 'CLI':  # Cliente
                suggestions.extend([
                    {
                        'text': f"¿Cuáles son mis casos?",
                        'category': 'personal',
                        'icon': '👤'
                    },
                    {
                        'text': f"¿Qué documentos están relacionados conmigo?",
                        'category': 'personal',
                        'icon': '📄'
                    }
                ])
        except:
            pass
        
        # Agregar sugerencias generales
        suggestions.extend(self.get_smart_suggestions(user))
        
        return suggestions[:6]  # Máximo 6 sugerencias contextuales
