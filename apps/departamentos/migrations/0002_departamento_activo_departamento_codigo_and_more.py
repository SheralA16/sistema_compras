# Generated by Django 5.2.1 on 2025-05-13 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('departamentos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='departamento',
            name='activo',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='departamento',
            name='codigo',
            field=models.CharField(default='SIN-CODIGO', max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='departamento',
            name='nombre',
            field=models.CharField(max_length=150),
        ),
    ]
