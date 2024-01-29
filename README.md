# CafuvSmart

Este es mi proyecto de título para la carrera de analista Programador.
El proyecto consiste en la optimización del sistema de archivos, registros de pacientes y la dispersion de datos que se tiene en el centro de atención fonoaudiológica de la Universidad de Valparaíso.

El lenguaje de programación ocupado es Python, el framework es Django y la base de datos ocupada es MySQL.

## Instalacion
Para instalar los paquetes y librerías del proyecto
1. Navega al directorio del proyecto `cd cafuv`
2. Escribir en consola `pip install -r requirements.txt`

## Estructura del Proyecto


    Cafuv
    |
    |__CafuvSmart
    |	|____settings.py
    |	|____urls.py
    |
    |__media
    |	|__archivos
    |	|__usuarios
    |__sesiones
    |	|____static
    |	|	|____css
    |	|	|	|____main.css
    |	|	|	|____login.css
    |	|	|	|____navigations.css
    |	|	|____ico
    |	|	|____img
    |	|	|____js
    |	|		|____base.js
    |	|		|____login.js
    |	|
    |	|____templates
    |	|		|____forms
    |	|		|	|____atencion.html
    |	|		|	|____compartir_archivo.html
    |	|		|	|____entrada_salida_form.html
    |	|		|	|____eventos_form.html
    |	|		|	|____fonoaudiologo.html
    |	|		|	|____insumos_form.html
    |	|		|	|____pacientes_form.html
    |	|		|	|____password.html
    |	|		|	|____sesion.html
    |	|		|	|____solicitud.html
    |	|		|	|____usuarios_form.html
    |	|		|____mails
    |	|		|	|____activation_validate.html
    |	|		|	|____activation.html
    |	|		|	|____welcome.html
    |	|		|____pages
    |	|		|	|____archivos.html
    |	|		|	|____index.html
    |	|		|	|____insumos.html
    |	|		|	|____pacientes.html
    |	|		|	|____perfil_paciente.html
    |	|		|	|____perfil_usuario.html
    |	|		|	|____usuarios.html
    |	|		|____registration
    |	|		|		|____login.html
    |	|		|____base.html
    |	|____models.py
    |	|____forms.py
    |	|____signals.py
    |	|____urls.py
    |	|____views.py
    |
    |__manage.py
    |__passenger_wsgi
    |__requirements.txt


## Licencia

Este proyecto está bajo la licencia "Apache-2.0 license". Consulta el archivo `LICENSE` para obtener más detalles.
