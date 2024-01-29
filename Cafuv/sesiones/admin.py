from django.contrib import admin
from .models import Usuario, Insumo, Paciente, Evento, Archivo, Comuna, Cargo, EntradaSalidaInsumo, Solicitud, Sesion, Atencion, UsuarioSolicitud



#Cambiar nombre
admin.site.site_header = "Administración de CAFUV"
admin.site.site_title = "Administración de CAFUV"


admin.site.register(Usuario)
admin.site.register(Insumo)
admin.site.register(Paciente)
admin.site.register(Evento)
admin.site.register(Archivo)
admin.site.register(Comuna)
admin.site.register(Cargo)
admin.site.register(EntradaSalidaInsumo)
admin.site.register(Solicitud)
admin.site.register(Sesion)
admin.site.register(Atencion)
admin.site.register(UsuarioSolicitud)