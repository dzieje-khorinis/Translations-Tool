# Generated by Django 3.1.5 on 2021-01-23 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_useractivity'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_active_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
