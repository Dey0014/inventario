# Generated by Django 5.0.7 on 2025-05-20 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='herramientas',
            name='codigo',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
