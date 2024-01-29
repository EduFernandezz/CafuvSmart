from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario, Insumo, Evento, Paciente, Archivo, EntradaSalidaInsumo
from django.contrib.auth.models import Group


class UsuarioChangeForm(UserChangeForm):
    grupos = Group.objects.all()
    grupo_choices = [(group.name, group.name) for group in grupos]
    grupo = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-input'}),
        choices=grupo_choices,
        label="Tipo Usuario"
    )

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name',
                  'email', 'phone', 'grupo')
        # Excluir los campos de contraseña
        exclude = ('password1', 'password2',)

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'oninput': "calcular_dv('id_username')"}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
        }

        labels = {
            'username': "Rut",
            'first_name': "Nombre(s)",
            'last_name': "Apellido(s)",
            'email': "Correo Electrónico",
            'phone': "Teléfono Contacto",
        }


class ArchivoForm(forms.Form):
    file = forms.FileField()


class UsuarioForm(UserCreationForm):
    grupos = Group.objects.all()
    grupo_choices = [(group.name, group.name) for group in grupos]
    grupo = forms.ChoiceField(widget=forms.Select(
        attrs={'class': 'form-input'}), choices=grupo_choices, label="Tipo Usuario")

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email',
                  'phone', 'grupo', 'password1', 'password2')
        widgets = {
            'password1': forms.HiddenInput(),
            'password2': forms.HiddenInput(),
            'username': forms.TextInput(attrs={'class': 'form-input', 'oninput': "calcular_dv('id_username')"}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'grupo': forms.Select(attrs={'class': 'form-input'}),
        }

        labels = {
            'username': "Rut",
            'first_name': "Nombre(s)",
            'last_name': "Apellido(s)",
            'email': "Correo Electrónico",
            'phone': "Teléfono Contacto",
            'grupo': "Tipo Usuario",
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        user_instance = getattr(self, 'instance', None)

        # Verificar si el nombre de usuario ha cambiado
        if user_instance and user_instance.username == username:
            return username  # Si no ha cambiado, retornar el mismo valor

        # Verificar si el nombre de usuario ya existe en otro usuario
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError('El nombre de usuario ya está en uso.')

        return username  # Retornar el nombre de usuario si no existe en otro usuario


class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ('titulo', 'fecha_inicio', 'fecha_termino',
                  'descripcion', 'prioridad')
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-input'}),
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'text', 'onfocus': 'convertir_tipo("id_fecha_inicio", "datetime-local")', 'onblur': 'convertir_tipo("id_fecha_inicio", "text")', 'onchange': 'validar_fecha_hora("id_fecha_inicio")'}),
            'fecha_termino': forms.DateTimeInput(attrs={'type': 'text', 'onfocus': 'convertir_tipo("id_fecha_termino", "datetime-local")', 'onblur': 'convertir_tipo("id_fecha_termino", "text")', 'onchange': 'validar_fecha_hora_termino("id_fecha_termino")'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input'}),
            'prioridad': forms.Select(attrs={'required': ''})
        }
        labels = {
            'titulo': "Título",
            'fecha_inicio': "Fecha de inicio",
            'fecha_termino': "Fecha de término",
            'descripcion': "Descripción",
            'prioridad': "Prioridad",
        }

    usuarios = forms.ModelMultipleChoiceField(
        queryset=Usuario.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Usuarios',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['usuarios'].initial = self.instance.usuarios.all()


class PacienteForm(forms.ModelForm):

    class Meta:
        model = Paciente
        fields = ['rut', 'nombre', 'apellido', 'fecha_nacimiento',
                  'comuna', 'genero', 'telefono', 'email']
        widgets = {
            'rut': forms.TextInput(attrs={'oninput': "calcular_dv('id_rut')"}),
            'nombre': forms.TextInput(),
            'apellido': forms.TextInput(),
            'fecha_nacimiento': forms.DateInput(attrs={'onchange': "validar_fecha_menor('id_fecha_nacimiento')"}),
            'comuna': forms.Select(attrs={'required': ''}),
            'genero': forms.Select(attrs={'required': ''}),
            'telefono': forms.TextInput(attrs={'required': ''}),
            'email': forms.EmailInput(attrs={'required': ''})
        }

    def __init__(self, *args, **kwargs):
        super(PacienteForm, self).__init__(*args, **kwargs)
        self.fields['rut'].label = 'RUT'
        self.fields['nombre'].label = 'Nombre(s)'
        self.fields['apellido'].label = 'Apellido(s)'
        self.fields['fecha_nacimiento'].label = 'Fecha de nacimiento'
        self.fields['comuna'].label = 'Comuna'
        self.fields['genero'].label = 'Género'
        self.fields['telefono'].label = 'N° Contacto'
        self.fields['email'].label = 'Correo Electrónico'
        self.fields['genero'].choices = [('Nulo', 'Prefiero no decirlo'), (
            'Masculino', 'Masculino'), ('Femenino', 'Femenino'), ('Otro', 'Otro')]


class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ('nombre', 'descripcion', 'cantidad', 'estado')
        widgets = {
            'nombre': forms.TextInput(),
            'descripcion': forms.Textarea(),
            'cantidad': forms.NumberInput(),
            'estado': forms.Select(attrs={'required': ''}),
        }
        labels = {
            'nombre': "Nombre",
            'descripcion': "Descripción",
            'cantidad': "Cantidad",
            'estado': "Estado"
        }

    def __init__(self, *args, **kwargs):
        super(InsumoForm, self).__init__(*args, **kwargs)
        self.fields['estado'].choices = [
            ('No aplica', 'No aplica'),
            ('Nuevo', 'Nuevo'),
            ('Usado', 'Usado'),
        ]
