# Generated by Django 4.2.6 on 2023-12-29 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sesiones', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sesion',
            name='respuesta',
            field=models.TextField(blank=True, null=True),
        ),
    ]
