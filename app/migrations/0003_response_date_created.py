# Generated by Django 3.2.6 on 2021-08-06 11:01

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_response'),
    ]

    operations = [
        migrations.AddField(
            model_name='response',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
