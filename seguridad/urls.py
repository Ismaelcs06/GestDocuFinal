from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MyTokenObtainPairView, UsuarioViewSet,LogoutView,RolViewSet, PermisoViewSet, UsuarioRolViewSet, RolPermisoViewSet, BitacoraViewSet, DetalleBitacoraViewSet
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = "seguridad"
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'roles', RolViewSet)
router.register(r'permisos', PermisoViewSet)
router.register(r'usuarios_roles', UsuarioRolViewSet)
router.register(r'roles_permisos', RolPermisoViewSet)
router.register(r'bitacoras', BitacoraViewSet)
router.register(r'detalles_bitacora', DetalleBitacoraViewSet)

urlpatterns = [
    path("bitacora/", views.bitacora_list, name="bitacora_list"),
    path("bitacora/<int:pk>/", views.bitacora_detalle, name="bitacora_detalle"),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
]
