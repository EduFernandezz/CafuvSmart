from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.http import require_POST
urlpatterns = [
    path('login/', LoginView.as_view(redirect_authenticated_user = True), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('change/', views.change, name='change'),
    path('usuarios/logged/', views.get_logged_user, name='logged'),
    path('descargar/<int:pk>', views.descargar_archivo, name='descargar'),
    path('activate/<str:uidb64>/<str:token>/<str:grupo>/', views.activate_account, name='activate'),


    path('', views.index_view, name='home'),
    path('eventos/api/', views.ApiEventos),
    path('eventos/<int:pk>', views.EventosFormView.as_view(), name="eventos_form"),



    path('usuarios/', views.usuarios_view, name="usuarios_view"),
    path('usuarios/api/', views.ApiUsuarios),
    path('usuarios/<str:pk>', views.UsuariosFormView.as_view(), name='usuarios_form'),
    


    path('insumos/', views.insumos_view, name="insumos_view"),
    path('insumos/api/', views.ApiInsumos),
    path('entrada-salida/insumos/<int:pk>', views.entrada_salida_insumos, name="entrada_salida"),
    path('insumos/<int:pk>', views.InsumosFormView.as_view(), name='insumos_form'),
    


    path('archivos/', views.archivos_view, name='archivos_view'),
    path('archivos/api/', views.ApiArchivos),
    path('archivos/compartir/<int:pk>/', views.compartir_archivo, name='compartir_archivo'),
    path('archivos/eliminar/<int:pk>/', views.eliminar_archivo, name='eliminar_archivo'),
    
    path('pacientes/', views.pacientes_view, name="pacientes_view"),
    path('pacientes/api/', views.ApiPaciente),
    path('pacientes/form/<str:pk>/', views.PacientesFormView.as_view(), name="pacientes_form"),
    

    path('pacientes/api/<str:pk>/', views.ApiSolicitud),  
    path('solicitud/<str:pk>/<str:pk_paciente>/', views.solicitud_view, name="solicitudes_form"),
    path('atencion/<str:pk>/', views.atencion_view, name="atencion_form"),
    path('atencion/usuarios/<str:pk>/', views.usuarios_solicitud_view, name="usuarios_solicitud_form"),
    path('desvincular/fono/<int:pk>', views.desvincular_fono, name="desvincular_fono"),
    path('sesion/form/<str:pk>/<str:pk_solicitud>/', views.sesion_view, name="sesion_form"),
    path('sesion/api/<str:pk>/', views.ApiSesion),
    path('sesion/eliminar/<str:pk>/', views.eliminar_sesion, name="eliminar_sesion"),
    path('upload/', views.archivo_form, name='file-upload'),
    path('listaespera/api/', views.ApiListaEspera),
    path('perfil/usuario/', views.perfil_usuario, name='perfil_usuario'),
    path('subir/imagen/', views.subir_imagen, name='subir_imagen'),
    path('change/password/', views.change_password, name='change_password'),
    path('bloquear/usuario/<str:pk>/', views.bloquear_usuario, name='bloquear_usuario'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
