# Generated by Django 4.2.6 on 2023-12-29 03:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sesiones', '0002_sesion_respuesta'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='atencion',
            name='respuesta',
        ),
    ]