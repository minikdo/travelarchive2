# Generated by Django 2.2.5 on 2019-09-17 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travels', '0031_auto_20190131_1225'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='address',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='place',
            name='hotel',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='place',
            name='neigh',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='neighbourhood'),
        ),
        migrations.AddField(
            model_name='place',
            name='price',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
