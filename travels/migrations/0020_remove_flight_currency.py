# Generated by Django 2.1.5 on 2019-01-15 09:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('travels', '0019_auto_20190115_1006'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flight',
            name='currency',
        ),
    ]
