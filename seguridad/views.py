from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Bitacora, DetalleBitacora

from rest_framework.permissions import IsAuthenticated

from rest_framework import viewsets
from .models import Usuario
from .serializers import UsuarioSerializer,LogoutSerializer,MyTokenPairSerializer,UsuarioMeSerializer
from  django.utils import timezone
from rest_framework.parsers import JSONParser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action,permission_classes
# Create your views here.

@login_required
def bitacora_list(request):
    # Permite filtrar por usuario, acción o fecha
    usuario = request.GET.get("usuario")
    accion = request.GET.get("accion")
    fecha = request.GET.get("fecha")

    bitacoras = Bitacora.objects.select_related("idUsuario").order_by("-fecha")

    if usuario:
        bitacoras = bitacoras.filter(idUsuario__username__icontains=usuario)
    if accion:
        bitacoras = bitacoras.filter(login__icontains=accion)
    if fecha:
        bitacoras = bitacoras.filter(fecha__date=fecha)

    return render(request, "seguridad/bitacora_list.html", {"bitacoras": bitacoras})


#DETALLE DE LAS BITACORAS

@login_required
def bitacora_detalle(request, pk):
    bitacora = Bitacora.objects.get(pk=pk)
    detalles = DetalleBitacora.objects.filter(idBitacora=bitacora).order_by("-fecha")
    return render(request, "seguridad/bitacora_detalle.html", {"bitacora": bitacora, "detalles": detalles})






class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    @action(
        detail=False,
        methods=['get'],
        url_path='me',
    )
    def me(self, request):
        """
        Endpoint exclusivo para el usuario autenticado.
        """
        # Usa el nuevo serializador específico para obtener los datos del usuario autenticado
        serializer = UsuarioMeSerializer(request.user)
        return Response(serializer.data)

from .models import Rol
from .serializers import RolSerializer

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer

from .models import Permiso
from .serializers import PermisoSerializer

class PermisoViewSet(viewsets.ModelViewSet):
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer

from .models import RolPermiso
from .serializers import RolPermisoSerializer

class RolPermisoViewSet(viewsets.ModelViewSet):
    queryset = RolPermiso.objects.all()
    serializer_class = RolPermisoSerializer

from .models import Bitacora
from .serializers import BitacoraSerializer

class BitacoraViewSet(viewsets.ModelViewSet):
    queryset = Bitacora.objects.all()
    serializer_class = BitacoraSerializer

from .models import DetalleBitacora
from .serializers import DetalleBitacoraSerializer

class DetalleBitacoraViewSet(viewsets.ModelViewSet):
    queryset = DetalleBitacora.objects.all()
    serializer_class = DetalleBitacoraSerializer

from .models import UsuarioRol
from .serializers import UsuarioRolSerializer

class UsuarioRolViewSet(viewsets.ModelViewSet):
    queryset = UsuarioRol.objects.all()
    serializer_class = UsuarioRolSerializer

from django.contrib.auth import authenticate, login
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect  
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class CSRFTokenView(APIView):
    """
    Vista para obtener el CSRF token.
    """
    def get(self, request):
        # Generar y devolver el token CSRF para proteger las solicitudes POST
        csrf_token = get_token(request)
        return JsonResponse({"csrf_token": csrf_token})





class LoginView(APIView):
    """
    Vista para autenticar a un usuario con username y password,
    y devolver un CSRF token.
    """
    @csrf_exempt  # Asegura que se protege la vista con CSRF si el login es exitoso
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Verificar las credenciales del usuario
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Iniciar la sesión del usuario
            csrf_token = get_token(request)  # Obtener el CSRF token
            return JsonResponse({"message": "Login exitoso", "csrf_token": csrf_token})
        else:
            return JsonResponse({"error": "Credenciales inválidas"}, status=status.HTTP_400_BAD_REQUEST)
class MyTokenObtainPairView(TokenObtainPairView): 
    serializer_class = MyTokenPairSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user  # ← ESTE es el usuario autenticado

        # IP (X-Forwarded-For si hay proxy; si no, REMOTE_ADDR)
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = (xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')) or None

        # User-Agent como "device" (o None si vacío)
        device = request.META.get('HTTP_USER_AGENT') or None

        # Registrar login en bitácora
        '''
        Bitacora.objects.create(
            idUsuario=user,
            login=timezone.now(),
            ip=ip,
            device=device
        )
        print('el usuario ingreso al perfil',)
        '''
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
class LogoutView(APIView):
    """
    Endpoint de **logout**.
    Requiere `{"refresh": "<jwt-refresh-token>"}` en el cuerpo (JSON).
    Blacklistea el refresh token mediante SimpleJWT y registra el logout en Bitacora si corresponde.
    Retorna 204 en caso de éxito.
    """
    parser_classes = [JSONParser]  # fuerza a intentar parsear JSON

    def post(self, request):
        # --- DEBUG: cuerpo crudo + datos parseados + headers ---
        raw = request.body.decode("utf-8", errors="replace")
        headers = {
            k: v for k, v in request.META.items()
            if k.startswith("HTTP_") or k in ("CONTENT_TYPE", "CONTENT_LENGTH")
        }

        #logger.info("=== RAW BODY === %s", raw)
        #logger.info("=== PARSED DATA === %s", request.data)
        #logger.info("=== HEADERS === %s", headers)
    
        # invalidamos el refresh token
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # ——————— Registro de logout ———————
        '''
        bit = Bitacora.objects.filter(
            idUsuario=request.user,
            logout_at__isnull=True
        ).last()
        if bit:
            print('no se esta cerrando seccion ')
            bit.logout = timezone.now()
            bit.save()
    '''
        return Response(status=status.HTTP_204_NO_CONTENT)