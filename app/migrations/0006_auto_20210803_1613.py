# Generated by Django 3.2.6 on 2021-08-03 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20210803_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='idea',
            name='collaborators',
            field=models.ManyToManyField(null=True, to='app.UserProfile'),
        ),
        migrations.AlterField(
            model_name='idea',
            name='validity',
            field=models.DateField(),
        ),
    ]
