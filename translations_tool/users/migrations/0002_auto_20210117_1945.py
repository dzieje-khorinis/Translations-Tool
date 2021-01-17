# Generated by Django 3.1.5 on 2021-01-17 19:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='chief',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subordinates', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, choices=[('ADMIN', 'Admin'), ('COORDINATOR', 'Coordinator'), ('TRANSLATOR', 'Translator')], max_length=255),
        ),
        migrations.AddField(
            model_name='user',
            name='role_related_language',
            field=models.CharField(blank=True, choices=[('en', 'English'), ('pl', 'Polish'), ('de', 'German'), ('ru', 'Russian')], max_length=2),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
    ]