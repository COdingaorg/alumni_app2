# Generated by Django 3.2.6 on 2021-08-03 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(to='app.UserProfile'),
        ),
    ]