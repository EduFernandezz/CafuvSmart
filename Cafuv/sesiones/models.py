from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date
import uuid
from django.db.models.signals import pre_save
from django.dispatch import receiver


class Usuario(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='usuarios/', default='usuarios/default.png')
    phone = models.CharField(max_length=15, blank=True, null=True)
    loggin = models.BooleanField(default=False)
    tutorial = models.BooleanField(default=True)
    archivos = models.ManyToManyField('Archivo', related_name='usuarios', blank=True)
    eventos = models.ManyToManyField('Evento', related_name='usuarios', blank=True)

    

class Archivo(models.Model):
    nombre = models.CharField(max_length=25, blank=True, null=True)
    extension = models.CharField(max_length=10, blank=True, null=True)
    fecha = models.DateField(auto_now_add=True)
    archivo = models.FileField(upload_to='archivos/', default='archivos/default.png')

    @property
    def propietario(self):
        usuario = self.usuarios.first()
        return usuario.username

class Evento(models.Model):
    titulo = models.CharField(max_length=25, blank=False, null=False)
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateTimeField(blank=False, null=False)
    fecha_termino = models.DateTimeField(blank=True, null=True)
    creador = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING, blank=True, null=True)
    opciones = (
        ('FF0000', 'Alta'),
        ('FFFF00', 'Media'),
        ('00FF00', 'Baja'),
    )
    prioridad = models.CharField(max_length=6, choices=opciones, default="00FF00", blank=False, null=False)


class Insumo(models.Model):
    nombre = models.CharField(max_length=25, null=False, blank=False)
    descripcion = models.TextField(blank=True, null=True)
    cantidad = models.PositiveIntegerField(default=0)
    opciones = (
        ('No aplica', 'No aplica'),
        ('Nuevo', 'Nuevo'),
        ('Usado', 'Usado'),
    )
    estado = models.CharField(max_length=25, choices=opciones, blank=False, null=False)


class EntradaSalidaInsumo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    insumo = models.ForeignKey(Insumo, on_delete=models.DO_NOTHING)
    cantidad = models.PositiveIntegerField(default=1)
    fecha = models.DateTimeField(auto_now_add = True)
    tipo = models.CharField(max_length=1, null=False, default="+")


class Comuna(models.Model):
    nombre = models.CharField(max_length=50, blank=False, null=False)
    
    def __str__(self):
        return self.nombre

class Paciente(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rut = models.CharField(max_length=10, unique=True, blank=False, null=False)
    nombre = models.CharField(max_length=50, blank=False, null=False)
    apellido = models.CharField(max_length=50, blank=False, null=False)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    comuna = models.ForeignKey(Comuna, on_delete=models.DO_NOTHING, blank=True, null=True, default=1)
    telefono = models.CharField(max_length=15, blank=False, null=False)
    email = models.EmailField(blank=True, null=True)
    opciones = (
        ('Nulo', 'Prefiero no decirlo'),
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
    )
    genero = models.CharField(max_length=9, choices=opciones, blank=False, null=False)

    def __str__(self):
        return f"{self.rut} - {self.nombre} {self.apellido}"

    def calcular_edad(self):
        today = date.today()
        age = today.year - self.fecha_nacimiento.year - \
            ((today.month, today.day) <
             (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        return age

    @property
    def edad(self):
        return self.calcular_edad()

class Cargo(models.Model):
    nombre = models.CharField(max_length=50, blank=False, null=False, unique=True)



from datetime import datetime
from django.utils import timezone


class Atencion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fecha = models.DateTimeField(blank=False, null=True)
    diagnostico = models.CharField(max_length=50, blank=True, null=True)
    enfoque = models.CharField(max_length=30, blank=True, null=True)
    objetivo_general = models.CharField(max_length=100, blank=True, null=True)
    solicitud = models.OneToOneField('Solicitud', on_delete=models.DO_NOTHING, blank=False, null=False)

    @property
    def mes(self):
        return self.fecha.strftime("%B")
    
    @property
    def fecha_input(self):
        local_fecha = self.fecha.astimezone(timezone.get_current_timezone())
        value = local_fecha.strftime("%Y-%m-%dT%H:%M")
        return value if value != "None" else ""
    
    @property
    def fecha_format(self):
        local_fecha = self.fecha.astimezone(timezone.get_current_timezone())
        value = local_fecha.strftime("%d/%m/%Y - %H:%M")
        return value if value != "None" else ""

class Solicitud(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fecha = models.DateTimeField(auto_now_add=True)
    motivo = models.CharField(max_length=255, blank=False, null=False)
    paciente = models.ForeignKey(Paciente, on_delete=models.DO_NOTHING, blank=True, null=True)

    @property
    def fecha_input(self):
        local_fecha = self.fecha.astimezone(timezone.get_current_timezone())
        value = local_fecha.strftime("%d/%m/%Y - %H:%M")
        return value if value != "None" else ""
    

    
class UsuarioSolicitud(models.Model):
    cargo = models.ForeignKey(Cargo, on_delete=models.DO_NOTHING, blank=True, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING, blank=True, null=True)
    solicitud = models.ForeignKey(Solicitud, on_delete=models.DO_NOTHING, blank=True, null=True)

class Sesion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fecha = models.DateTimeField(null=False, blank=False)
    numero = models.PositiveIntegerField(null=False, blank=False)
    tiempo = models.PositiveIntegerField(null=True, blank=True)
    area = models.CharField(max_length=30, null=False, blank=False)
    objetivo = models.CharField(max_length=255, null=False, blank=False)
    material = models.CharField(max_length=30, null=False, blank=False)
    atencion = models.ForeignKey(Atencion, on_delete=models.DO_NOTHING, blank=True, null=True)
    respuesta = models.TextField(null=True, blank=True)

    @property
    def fecha_input(self):
        local_fecha = self.fecha.astimezone(timezone.get_current_timezone())
        value = local_fecha.strftime("%Y-%m-%dT%H:%M")
        return value if value != "None" else ""
    
    @property
    def fecha_format(self):
        local_fecha = self.fecha.astimezone(timezone.get_current_timezone())
        value = local_fecha.strftime("%d/%m/%Y - %H:%M")
        return value if value != "None" else ""
    
