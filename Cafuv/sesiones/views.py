from typing import Any, Dict
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from .forms import UsuarioForm, InsumoForm, EventoForm, PacienteForm, UsuarioChangeForm, ArchivoForm
from .models import Usuario, Insumo, Paciente, Evento, EntradaSalidaInsumo, Archivo, Solicitud, Atencion, Sesion, UsuarioSolicitud, Cargo
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.contrib import messages
from itertools import cycle
from django import forms
import uuid
import hashlib
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import Group
from datetime import datetime
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


def grupos_check(user, grupos_permitidos):
    return user.groups.filter(name__in=grupos_permitidos).exists()


def grupos_required(grupos_permitidos):
    def decorator(view_func):
        decorated_view_func = user_passes_test(
            lambda u: grupos_check(u, grupos_permitidos),
            login_url='home'
        )(view_func)
        return decorated_view_func
    return decorator


########################
### Vistas PACIENTES ###
########################
@login_required
@grupos_required(['Fonoaudiólogo', 'Administrador', 'Secretaria'])
def pacientes_view(request):
    return render(request, "pages/pacientes.html")


@login_required
@grupos_required(['Fonoaudiólogo', 'Administrador', 'Secretaria'])
def ApiPaciente(request):
    lista_pacientes = []
    pacientes = Paciente.objects.all()
    for x in pacientes:
        lista_pacientes.append([f"{x.rut}-{dv(x.rut)}", f"{x.nombre} {x.apellido}",
                               x.edad, f"+56{x.telefono}", x.email, x.id])
    return JsonResponse(lista_pacientes, safe=False)


@method_decorator(login_required, name='dispatch')
@method_decorator(grupos_required(['Fonoaudiólogo', 'Administrador', 'Secretaria']), name='dispatch')
class PacientesFormView(TemplateView):
    template_name = "forms/pacientes_form.html"
    allowed_groups = ["Administrador", "Secretaria", "Fonoaudiólogo"]

    def get(self, request, *args: Any, **kwargs: Dict[str, Any]):

        form = PacienteForm()

        context = {
            'form': form
        }

        if kwargs['pk'] != '0':
            paciente = get_object_or_404(Paciente, id=kwargs['pk'])
            form = PacienteForm(instance=paciente)
            form.fields['genero'].widget.attrs['disabled'] = True
            form.fields['comuna'].widget.attrs['disabled'] = True
            context["paciente"] = paciente
            context["form"] = form
            context["dv"] = dv(paciente.rut)
            return render(request, 'pages/perfil_paciente.html', context)

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        paciente = None

        if pk != '0':
            paciente = get_object_or_404(Paciente, id=pk)

        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            if pk != '0':
                messages.add_message(
                    request, messages.SUCCESS, "¡Paciente actualizado correctamente!")
                return redirect('pacientes_form', pk=pk)
            else:
                messages.add_message(
                    request, messages.SUCCESS, "¡Paciente agregado correctamente!")
                return redirect('pacientes_view')
        else:

            messages.add_message(request, messages.ERROR,
                                 "Ha ocurrido un error al agregar el paciente")
            if pk != '0':
                messages.add_message(
                    request, messages.ERROR, "¡Ha ocurrido un error al actualizar el paciente!")

        return redirect('pacientes_form', pk=pk)


@login_required
@grupos_required(['Fonoaudiólogo', 'Administrador', 'Secretaria'])
def solicitud_view(request, pk, pk_paciente):
    paciente = get_object_or_404(Paciente, id=pk_paciente)
    form = PacienteForm(instance=paciente)
    context = {
        'paciente': paciente,
        'form': form,
    }
    if request.method == 'POST':
        if pk != '0':
            solicitud = get_object_or_404(Solicitud, id=pk)
            solicitud.motivo = request.POST.get('motivo')
            solicitud.save()
            atencion = Atencion.objects.create(solicitud=solicitud)
            atencion.save()
            return redirect('solicitudes_form', pk=pk, pk_paciente=pk_paciente)
        motivo = request.POST.get('motivo')
        solicitud = Solicitud.objects.create(motivo=motivo, paciente=paciente)
        solicitud.save()
        return redirect('solicitudes_form', pk=pk, pk_paciente=pk_paciente)
    else:
        if pk != '0':
            context['solicitud'] = get_object_or_404(Solicitud, id=pk)

        return render(request, 'forms/solicitud.html', context)


@login_required
@grupos_required(['Fonoaudiólogo', 'Administrador', 'Secretaria'])
def ApiSolicitud(request, pk):
    lista_solicitudes = []
    solicitudes = Solicitud.objects.filter(paciente=pk)
    for x in solicitudes:
        try:
            fecha_atencion = x.atencion.fecha_format
            id_atencion = 'Ver Detalle'
        except:
            fecha_atencion = 'Sin atención'
            id_atencion = 'Agregar +'
        lista_solicitudes.append(
            [x.fecha_input, x.id, fecha_atencion, [id_atencion, x.id]])
    return JsonResponse(lista_solicitudes, safe=False)


@login_required
@grupos_required(['Fonoaudiólogo', 'Administrador', 'Secretaria'])
def atencion_view(request, pk):
    data = {}
    solicitud = get_object_or_404(Solicitud, id=pk)
    usuarios_solicitudes = UsuarioSolicitud.objects.filter(solicitud=solicitud)
    data["solicitud"] = solicitud
    data["fonos"] = usuarios_solicitudes
    try:
        atencion = Atencion.objects.get(solicitud=solicitud)
        data["atencion"] = atencion
    except:
        pass
    if request.method == "POST":
        if 'atencion' in data:
            atencion = data["atencion"]
            atencion.fecha = request.POST.get('fecha')
            atencion.diagnostico = request.POST.get('diagnostico')
            atencion.enfoque = request.POST.get('enfoque')
            atencion.objetivo_general = request.POST.get('objetivo_general')
            atencion.save()

        else:
            fecha_solicitud = solicitud.fecha
            fecha_atencion = request.POST.get('fecha')
            fecha_atencion = datetime.strptime(
                fecha_atencion, '%Y-%m-%dT%H:%M')
            fecha_atencion = timezone.make_aware(
                fecha_atencion, timezone.get_default_timezone())
            if fecha_solicitud > fecha_atencion:
                messages.add_message(
                    request, messages.ERROR, "¡La fecha de la atención no puede ser anterior a la fecha de la solicitud!")
                return redirect('atencion_form', pk=pk)

            atencion = Atencion.objects.create(
                solicitud=solicitud, fecha=request.POST.get('fecha'))
            atencion.save()

            return redirect('atencion_form', pk=pk)

        return redirect('atencion_form', pk=pk)

    return render(request, "forms/atencion.html", data)


@login_required
@grupos_required(['Fonoaudiólogo', 'Administrador', 'Secretaria'])
def usuarios_solicitud_view(request, pk):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, id=request.POST.get('usuario'))
        cargo = get_object_or_404(Cargo, id=request.POST.get('cargo'))
        solicitud = get_object_or_404(Solicitud, id=pk)
        usuario_solicitud = UsuarioSolicitud.objects.create(
            usuario=usuario, solicitud=solicitud, cargo=cargo)
        usuario_solicitud.save()
        return redirect('atencion_form', pk=pk)
    else:
        solicitud = get_object_or_404(Solicitud, id=pk)
        atencion = Atencion.objects.filter(solicitud=solicitud)
        usuarios_solicitudes = UsuarioSolicitud.objects.filter(
            solicitud=solicitud)
        usuarios = Usuario.objects.filter(groups__name__in=['Fonoaudiólogo']).exclude(
            id__in=usuarios_solicitudes.values_list('usuario', flat=True))
        cargos = Cargo.objects.all()

    fonos = UsuarioSolicitud.objects.filter(solicitud=solicitud)
    return render(request, "forms/fonoaudiologo.html", {'solicitud': solicitud, 'usuarios': usuarios, 'cargos': cargos, 'fonos': fonos})


def desvincular_fono(request, pk):
    try:
        usuario_solicitud = get_object_or_404(UsuarioSolicitud, id=pk)
        solicitud = usuario_solicitud.solicitud.id
        usuario_solicitud.delete()
        messages.add_message(request, messages.SUCCESS,
                             "¡Fonoaudiólogo desvinculado correctamente!")
    except:
        messages.add_message(
            request, messages.ERROR, "¡Ha ocurrido un error al desvincular el fonoaudiólogo!")
    return redirect('usuarios_solicitud_form', pk=solicitud)


@login_required
@grupos_required(['Fonoaudiólogo', 'Administrador', 'Secretaria'])
def sesion_view(request, pk, pk_solicitud):
    solicitud = get_object_or_404(Solicitud, id=pk_solicitud)
    atencion = Atencion.objects.get(solicitud=solicitud)
    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        numero = Sesion.objects.filter(atencion=solicitud.atencion).count()+1
        tiempo = request.POST.get('tiempo')
        area = request.POST.get('area')
        objetivo = request.POST.get('objetivo')
        material = request.POST.get('material')
        respuesta = request.POST.get('respuesta')
        fecha_sesion = datetime.strptime(fecha, '%Y-%m-%dT%H:%M')
        fecha_sesion = timezone.make_aware(
            fecha_sesion, timezone.get_default_timezone())
        print(type(fecha_sesion))
        print(type(atencion.fecha))
        if atencion.fecha > fecha_sesion:
            messages.add_message(
                request, messages.ERROR, "¡La fecha de la sesión no puede ser anterior a la fecha de la atención!")
            return redirect('atencion_form', pk=pk_solicitud)
        if pk != '0':
            sesion = get_object_or_404(Sesion, id=pk)
            sesion.fecha = fecha
            sesion.numero = numero
            sesion.tiempo = tiempo
            sesion.area = area
            sesion.objetivo = objetivo
            sesion.material = material
            sesion.respuesta = respuesta
            sesion.save()
            return redirect('atencion_form', pk=pk_solicitud)
        else:
            sesion = Sesion.objects.create(atencion=solicitud.atencion, fecha=fecha,
                                           numero=numero, tiempo=tiempo, area=area, objetivo=objetivo, material=material, respuesta=respuesta)

            sesion.save()
        return redirect('atencion_form', pk=pk_solicitud)
    else:
        if pk != '0':
            sesion = get_object_or_404(Sesion, id=pk)
            return render(request, 'forms/sesion.html', {'sesion': sesion, 'solicitud': solicitud, 'atencion': atencion})
        return render(request, 'forms/sesion.html', {'solicitud': solicitud, 'atencion': atencion})


def ApiSesion(request, pk):
    lista_sesiones = []
    solicitud = get_object_or_404(Solicitud, id=pk)
    try:
        sesiones = Sesion.objects.filter(atencion=solicitud.atencion)
        for x in sesiones:
            lista_sesiones.append(
                [x.fecha_format, x.numero, x.tiempo, x.area, x.objetivo, x.material, x.respuesta, x.id])
    except:
        pass
    return JsonResponse(lista_sesiones, safe=False)


def eliminar_sesion(request, pk):
    sesion = get_object_or_404(Sesion, id=pk)
    solicitud = sesion.atencion.solicitud.id
    sesion.delete()
    messages.add_message(request, messages.SUCCESS,
                         "¡Sesión eliminada correctamente!")
    return redirect('atencion_form', pk=solicitud)
#########################################################################################################


######################
### Vistas INSUMOS ###
######################
@login_required
@grupos_required(['Fonoaudiólogo', 'Administrador'])
def insumos_view(request):
    return render(request, "pages/insumos.html")


@login_required
@grupos_required(['Fonoaudiólogo', 'Administrador'])
def ApiInsumos(request):

    lista_insumos = []
    insumos = Insumo.objects.all()
    for x in insumos:
        lista_insumos.append([x.nombre.capitalize(
        ), x.descripcion.capitalize(), x.estado.capitalize(), x.cantidad, x.id])
    return JsonResponse(lista_insumos, safe=False)


@login_required
@grupos_required(['Fonoaudiólogo', 'Administrador'])
def entrada_salida_insumos(request, pk):
    insumo = get_object_or_404(Insumo, id=pk)

    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 0))
        accion = request.POST.get('accion')  # 'mas' o 'menos'
        if cantidad <= 1:
            messages.add_message(request, messages.ERROR,
                                 "La cantidad debe ser mayor a 1")
            return redirect('entrada_salida', pk=insumo.id)
        if accion == 'mas':
            tipo = "+"
            insumo.cantidad += cantidad
        elif accion == 'menos':
            tipo = "-"
            if insumo.cantidad >= cantidad:
                insumo.cantidad -= cantidad
            else:
                messages.add_message(request, messages.ERROR,
                                     "No hay insumos suficientes")

        # Guardar el insumo actualizado
        insumo.save()
        # Registrar la entrada/salida del insumo en la tabla EntradaSalidaInsumo
        entrada_salida = EntradaSalidaInsumo(
            usuario=request.user,  # Asegúrate de tener el usuario autenticado
            insumo=insumo,
            cantidad=cantidad,
            tipo=tipo
        )
        entrada_salida.save()
        print(entrada_salida.fecha)
        return redirect('entrada_salida', pk=insumo.id)
    else:
        objetos = EntradaSalidaInsumo.objects.filter(insumo=insumo)
        return render(request, 'forms/entrada_salida_form.html', {'objetos': objetos})


@method_decorator(login_required, name='dispatch')
@method_decorator(grupos_required(['Administrador', 'Fonoaudiólogo']), name='dispatch')
class InsumosFormView(TemplateView):
    template_name = 'forms/insumos_form.html'
    allowed_groups = ['Administrador', 'Fonoaudiólogo']

    def get(self, request, *args: Any, **kwargs: Dict[str, Any]):
        form = InsumoForm()
        context = {
            'form': form,
        }
        if kwargs['pk'] != 0:
            insumo = get_object_or_404(Insumo, id=kwargs['pk'])
            form = InsumoForm(instance=insumo)
            form.fields['cantidad'].widget = forms.HiddenInput()
            form.fields['cantidad'].label = ""
            context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args: Any, **kwargs: Dict[str, Any]):
        pk = kwargs.get('pk')
        insumo = None

        if pk != 0:
            insumo = get_object_or_404(Insumo, id=pk)

        form = InsumoForm(request.POST, instance=insumo)

        if Insumo.objects.filter(nombre=request.POST.get('nombre'), descripcion=request.POST.get('descripcion')).exists():
            messages.add_message(
                request, messages.ERROR, "¡Ya existe un insumo con el mismo nombre!")
            return redirect('insumos_form', pk=pk)

        if request.POST.get('descripcion') == "":
            if Insumo.objects.filter(nombre=request.POST.get('nombre'), descripcion=None).exists():
                messages.add_message(
                    request, messages.ERROR, "¡Ya existe un insumo con el mismo nombre!")
                return redirect('insumos_form', pk=pk)

        if form.is_valid():
            form.save()
            if pk != 0:
                messages.add_message(
                    request, messages.SUCCESS, "¡Insumo actualizado correctamente!")
                return redirect('insumos_form', pk=pk)
            else:
                messages.add_message(
                    request, messages.SUCCESS, "¡Insumo agregado correctamente!")
        else:
            print(form.errors)
            messages.add_message(request, messages.ERROR,
                                 "Ha ocurrido un error al agregar el insumo")
            if pk != 0:
                messages.add_message(
                    request, messages.ERROR, "¡Ha ocurrido un error al actualizar el insumo!")

        return redirect('insumos_view')
#########################################################################################################


######################
### Vistas EVENTOS ###
######################
@login_required
@grupos_required(['Fonoaudiólogo', 'Administrador', 'Secretaria'])
def index_view(request):
    cantidad_solicitudes_diciembre = Solicitud.objects.filter(
        fecha__month=12, fecha__year=2023).count()
    cantidad_atenciones_diciembre = Atencion.objects.filter(
        fecha__month=12, fecha__year=2023).count()
    return render(request, 'pages/index.html', {'solicitudes': cantidad_solicitudes_diciembre, 'atenciones': cantidad_atenciones_diciembre})


@login_required
@grupos_required(['Fonoaudiólogo', 'Administrador', 'Secretaria'])
def ApiEventos(request):
    lista_eventos = []
    eventos = Evento.objects.filter(usuarios=request.user)
    for x in eventos:
        if x.fecha_termino == None:
            diccionario_eventos = {
                'title': x.titulo, 'start': x.fecha_inicio, 'backgroundColor': f"#{x.prioridad}", 'id': x.id}
        else:
            diccionario_eventos = {'title': x.titulo, 'start': x.fecha_inicio, 'color': f"#{x.prioridad}",
                                   'end': x.fecha_termino, 'id': x.id}
        lista_eventos.append(diccionario_eventos)
    return JsonResponse(lista_eventos, safe=False)


@method_decorator(login_required, name='dispatch')
@method_decorator(grupos_required(['Fonoaudiólogo', 'Administrador', 'Secretaria']), name='dispatch')
class EventosFormView(TemplateView):
    template_name = 'forms/eventos_form.html'
    allowed_groups = ['Administrador']

    def get(self, request, *args: Any, **kwargs: Dict[str, Any]):
        form = EventoForm()
        context = {
            'form': form,
        }
        if request.user.groups.filter(name='Administrador').exists():
            context['usuarios'] = Usuario.objects.filter(
                is_active=True).exclude(id=request.user.id)
        else:
            context['usuarios'] = Usuario.objects.filter(
                is_active=True, groups__name__in=['Fonoaudiólogo']).exclude(id=request.user.id)

        if kwargs['pk'] != 0:
            evento = get_object_or_404(Evento, id=kwargs['pk'])
            if evento.creador == request.user:
                form = EventoForm(instance=evento)
                context['form'] = form

        return render(request, self.template_name, context)

    def post(self, request, *args: Any, **kwargs: Dict[str, Any]):
        pk = kwargs.get('pk')
        evento = None

        if pk != 0:
            evento = get_object_or_404(Evento, id=pk)

        form = EventoForm(request.POST, instance=evento)

        if form.is_valid():
            nuevo_evento = form.save(commit=False)
            try:
                titulo = nuevo_evento.titulo
                fecha_inicio = nuevo_evento.fecha_inicio
                fecha_termino = nuevo_evento.fecha_termino
                evento = Evento.objects.get(
                    titulo=titulo, fecha_inicio=fecha_inicio, fecha_termino=fecha_termino)
                if evento.creador == request.user:
                    messages.add_message(
                        request, messages.ERROR, "¡Ya existe un evento con los mismos datos!")
                    return redirect('eventos_form', pk=pk)
            except:
                pass

            nuevo_evento.save()
            nuevo_evento.usuarios.clear()
            nuevo_evento.usuarios.add(request.user)
            nuevo_evento.creador = request.user
            usuarios_seleccionados = form.cleaned_data.get('usuarios')
            if usuarios_seleccionados:
                for usuario in usuarios_seleccionados:
                    nuevo_evento.usuarios.add(usuario)

            nuevo_evento.save()

            if pk != 0:
                messages.add_message(
                    request, messages.SUCCESS, "¡Evento actualizado correctamente!")
                return redirect('eventos_form', pk=pk)
            else:
                messages.add_message(
                    request, messages.SUCCESS, "¡Evento agregado correctamente!")
        else:
            messages.add_message(request, messages.ERROR,
                                 "Ha ocurrido un error al agregar el evento")
            if pk != 0:
                messages.add_message(
                    request, messages.ERROR, "¡Ha ocurrido un error al actualizar el evento!")

        return redirect('home')
#########################################################################################################


#######################
### Vistas ARCHIVOS ###
#######################
@login_required
@grupos_required(['Fonoaudiólogo', 'Administrador', 'Secretaria'])
def archivos_view(request):
    archivos = Archivo.objects.all()
    form = ArchivoForm()
    context = {
        'archivos': archivos,
        'form': form
    }

    return render(request, 'pages/archivos.html', context)


def archivo_form(request):
    if request.method == 'POST':
        files = request.FILES
        for file in files:
            archivo = request.FILES[file]
            nombre = archivo.name
            extension = nombre.split('.')[-1]
            nuevo_archivo = Archivo.objects.create(
                nombre=nombre, extension=extension, archivo=archivo)
            request.user.archivos.add(nuevo_archivo)
        return JsonResponse({'message': 'Archivo cargado correctamente'})
    return redirect('archivos_view')


@login_required
@grupos_required(['Fonoaudiólogo', 'Administrador', 'Secretaria'])
def ApiArchivos(request):
    extensiones = {'docx': 'docx.png', 'pdf': 'pdf.png', 'xlsx': 'xlsx.png', 'pptx': 'pptx.png', 'jpg': 'jpg.png', 'png': 'png.png', 'mp3': 'mp3.png', 'mp4': 'mp4.png',
                   'zip': 'zip.png', 'rar': 'rar.png', 'txt': '<img width="24" height="24" src="https://img.icons8.com/color/48/txt.png" alt="txt"/>', 'default': 'default.png'}
    lista_archivos = []
    archivos = request.user.archivos.all()
    for x in archivos:
        html = f'<div class="archivo"><a href="{x.archivo.url}" target="_blank"><img src="/static/ico/extensiones/{extensiones[x.extension]}"><label>{x.nombre}</label></a></div>'
        buttons = f"<a class='btn bg-danger' href='/archivos/eliminar/{x.id}/'><i class='fa fa-trash'></i></a>"
        compartidos = x.usuarios.all().exclude(id=request.user.id).count()
        propietario = x.usuarios.last()
        propietario_name = f'{propietario.first_name} {propietario.last_name}'
        if propietario.username == request.user.username:
            propietario_name = 'Tú'
            buttons = f"""
            <a class='btn bg-secondary' href='/archivos/compartir/{x.id}/'>
                <i class="fa-solid fa-user-group"></i>
            </a>
"""+buttons

        lista_archivos.append(
            [html, x.fecha, propietario_name, f'{compartidos} Usuarios', buttons])
    return JsonResponse(lista_archivos, safe=False)


def descargar_archivo(request, pk):
    archivo = get_object_or_404(Archivo, id=pk)
    return redirect(archivo.archivo.url)


def eliminar_archivo(request, pk):
    try:
        request.user.archivos.remove(pk)
        messages.add_message(request, messages.SUCCESS,
                             "¡Archivo eliminado correctamente!")

    except:
        messages.add_message(request, messages.ERROR,
                             "¡Ha ocurrido un error al eliminar el archivo!")

    return redirect('archivos_view')


def compartir_archivo(request, pk):
    if request.method == 'POST':
        try:
            archivo = get_object_or_404(Archivo, id=pk)
            usuarios = request.POST.getlist('usuarios')
            for usuario in usuarios:
                usuario = get_object_or_404(Usuario, id=usuario)
                usuario.archivos.add(archivo)
            messages.add_message(request, messages.SUCCESS,
                                 "¡Archivo compartido correctamente!")
        except Exception as e:
            messages.add_message(request, messages.ERROR,
                                 f"Error al compartir el archivo: {str(e)}")
        return redirect('archivos_view')
    else:
        archivo = get_object_or_404(Archivo, id=pk)
        usuarios = Usuario.objects.exclude(
            archivos=archivo).exclude(id=request.user.id)
        return render(request, 'forms/compartir_archivo.html', {'archivo': archivo, 'usuarios': usuarios})

#########################################################################################################


#######################
### Vistas USUARIOS ###
#######################
@login_required
@grupos_required(['Administrador'])
def usuarios_view(request):
    return render(request, "pages/usuarios.html")


@login_required
@grupos_required(['Administrador'])
def ApiUsuarios(request):
    lista_usuarios = []
    usuarios = Usuario.objects.filter(is_active=True).exclude(id=request.user.id)
    for x in usuarios:
        login = x.last_login.strftime(
            "%d/%m/%Y a las %HH:%MM") if x.last_login else 'No ha ingresado nunca'
        if x.is_active == True:
            html = f'<a class="btn bg-secondary" href="{x.id}"> <i class="fa fa-user-pen"></i></a><a class="btn bg-danger" href="/bloquear/usuario/{x.id}/"><i class="fa fa-user-lock"></i></a>'
        else:
            html = f'<a class="btn bg-secondary" href="{x.id}"><i class="fa fa-user-pen"></i></a><a class="btn desbloquear" href="/bloquear/usuario/{x.id}/"><i class="fa fa-user-check"></i></a>'
        grupo = x.groups.first().name
        lista_usuarios.append([f"{x.first_name.title()} {x.last_name.title()}", x.email.lower(
        ), x.phone,  grupo, html])

    return JsonResponse(lista_usuarios, safe=False)


@method_decorator(login_required, name='dispatch')
@method_decorator(grupos_required(['Administrador']), name='dispatch')
class UsuariosFormView(TemplateView):
    template_name = 'forms/usuarios_form.html'

    def get(self, request, *args: Any, **kwargs: Dict[str, Any]):
        form = UsuarioForm()
        context = {
            'form': form,
            'titulo': "Nuevo"
        }
        if kwargs['pk'] != '0':
            usuario = get_object_or_404(Usuario, id=kwargs['pk'])
            form = UsuarioChangeForm(instance=usuario)
            context["usuario"] = usuario
            context["form"] = form
            context["dv"] = dv(usuario.username)
            context["titulo"] = "Actualizar"

        return render(request, self.template_name, context)

    def post(self, request, *args: Any, **kwargs: Dict[str, Any]):
        pk = kwargs.get('pk')
        form = UsuarioForm(request.POST)

        if pk != '0':
            usuario = get_object_or_404(Usuario, id=pk)
            form = UsuarioChangeForm(request.POST, instance=usuario)

        if form.is_valid():
            # eliminar puntos del rut
            if pk != '0':
                form.save()  # Guarda el usuario en la base de datos
                messages.add_message(
                    request, messages.SUCCESS, "¡Usuario actualizado correctamente!")
                return redirect('usuarios_form', pk=pk)
            else:
                user = form.save(commit=False)
                # Establece la cuenta como inactiva hasta que se active por correo electrónico
                user.is_active = False
                user.username = user.username.replace(".", "")
                user.save()
                grupo = form.cleaned_data.get('grupo')
                # Envía el correo electrónico de activación
                current_site = get_current_site(request)
                subject = 'Activación de cuenta'
                message = render_to_string('mails/activation.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': user.id,
                    'token': generate_activation_token(user.id),
                    'grupo': grupo
                })
                # Versión de texto plano del correo electrónico
                plain_message = strip_tags(message)
                send_mail(subject, plain_message, 'noreply@cafuv.cl',
                          [user.email], html_message=message)

                messages.add_message(
                    request, messages.SUCCESS, "¡Usuario agregado correctamente!")
                return redirect('usuarios_view')

        else:
            messages.add_message(request, messages.ERROR,
                                 "¡Ha ocurrido un error al agregar el usuario!")
            pk = '0'
            if pk != '0':
                pk = pk
                messages.add_message(
                    request, messages.ERROR, "¡Ha ocurrido un error al actualizar el usuario!"
                )
        return redirect('usuarios_form', pk=pk)
#########################################################################################################


#####################
### Vistas Extras ###
#####################
def dv(rut):
    # Eliminar puntos y guión (si están presentes)
    rut = rut.replace(".", "").replace("-", "")
    # Invertir los dígitos y convertirlos a enteros
    reversed_digits = map(int, reversed(str(rut)))
    factors = cycle(range(2, 8))  # Ciclo infinito de los factores

    # Suma ponderada de dígitos por factores
    total = sum(digit * factor for digit,
                factor in zip(reversed_digits, factors))

    digito_verificador = 11 - (total % 11)  # Obtener el dígito verificador

    if digito_verificador == 11:
        return '0'
    elif digito_verificador == 10:
        return 'K'
    else:
        return str(digito_verificador)


def generate_activation_token(user_id):
    # Genera un UUID aleatorio único
    token = uuid.uuid4().hex

    # Hashea el UUID junto con el ID del usuario para mayor seguridad
    hashed_token = hashlib.sha256(
        f"{user_id}{token}".encode('utf-8')).hexdigest()

    return hashed_token


def activate_account(request, uidb64, token, grupo):
    if request.method == 'GET':
        return render(request, 'mails/activation_validate.html')

    if request.method == 'POST':
        try:
            grupo = Group.objects.get(name=grupo)
            user = Usuario.objects.get(id=uidb64)
            username = request.POST.get('username')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 != password2:
                messages.add_message(
                    request, messages.ERROR, "¡Las contraseñas no coinciden!")
                return redirect('activate', uidb64=uidb64, token=token, grupo=grupo)

            if not Usuario.objects.filter(username=username).exists():
                messages.add_message(
                    request, messages.ERROR, "¡La cuenta ingresada, no corresponde a un usuario de CAFUV!")
            user.is_active = True
            user.set_password(password1)
            user.save()
            user.groups.add(grupo)
            user.save()
            messages.add_message(request, messages.SUCCESS,
                                 "¡Cuenta activada correctamente!")
            return redirect('login')
        except:
            messages.add_message(request, messages.ERROR,
                                 "¡El enlace de activación es inválido!")
            return redirect('login')


def get_logged_user(request):
    usuarios = Usuario.objects.filter(loggin=True).exclude(id=request.user.id)
    lista_usuarios = []
    for x in usuarios:
        imagen = f'<img src="{x.image.url}" width="30px">' if x.image != 'usuarios/default.png' else '<div class="icono"><i class="fa-solid fa-user"></i></div>'
        nombre = f"<label>{x.first_name} <br> {x.last_name}</label>"

        lista_usuarios.append(
            "<div class='usuario'>"+'<i class="fa-solid fa-circle" style="color:rgb(9, 219, 9); font-size:xx-small"></i>'+imagen+nombre+"</div>")
    return JsonResponse(lista_usuarios, safe=False)


def change(request):
    usuario = get_object_or_404(Usuario, id=request.user.id)
    if usuario.loggin == False:
        usuario.loggin = True
    else:
        usuario.loggin = False
    usuario.save()
    view = request.META.get('HTTP_REFERER')
    print(view)
    view = view.split('/')
    view = view[3]
    if view == '':
        return redirect('home')
    else:
        return redirect(view+'_view')


def ApiListaEspera(request):
    solicitudes = Solicitud.objects.filter(atencion=None)
    lista_solicitudes = []
    for x in solicitudes:
        lista_solicitudes.append(
            [f"{x.paciente.nombre} {x.paciente.apellido}", x.fecha_input, x.motivo, x.id])

    return JsonResponse(lista_solicitudes, safe=False)


def perfil_usuario(request):
    return render(request, 'pages/perfil_usuario.html')


def subir_imagen(request):
    imagen = request.FILES.get('imagen')
    request.user.image = imagen
    request.user.save()
    return redirect('perfil_usuario')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Actualiza la sesión del usuario si la contraseña cambió
            messages.success(request, '¡Tu contraseña ha sido cambiada con éxito!')
            return redirect('perfil_usuario')  # Reemplaza 'ruta_a_tu_perfil' con la URL de tu página de perfil o donde desees redirigir después de cambiar la contraseña
        else:
            messages.error(request, 'Ha ocurrido un error al intentar cambiar la contraseña, por favor intente nuevamente.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'forms/password.html', {'form': form})

def bloquear_usuario(request, pk):
    usuario = get_object_or_404(Usuario, id=pk)
    if usuario.loggin == True:
        messages.add_message(request, messages.ERROR,
                             "¡El usuario se encuentra conectado!")
        return redirect('usuarios_view')
    if usuario.is_active == False:
        usuario.is_active = True
        msge = f"¡{usuario.first_name} {usuario.last_name} ha sido desbloqueado!"
    else:
        usuario.is_active = False
        msge = f"¡{usuario.first_name} {usuario.last_name} ha sido bloqueado!"
    usuario.save()
    messages.add_message(request, messages.SUCCESS, msge)
    return redirect('usuarios_view')

