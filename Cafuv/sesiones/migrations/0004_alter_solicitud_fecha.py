# Generated by Django 4.2.6 on 2023-12-29 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sesiones', '0003_remove_atencion_respuesta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitud',
            name='fecha',
            field=models.DateTimeField(),
        ),
    ]