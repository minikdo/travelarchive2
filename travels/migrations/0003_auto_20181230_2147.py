# Generated by Django 2.1.4 on 2018-12-30 20:47

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('travels', '0002_flight'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='airport',
            options={'ordering': ['country', 'city']},
        ),
        migrations.AlterModelOptions(
            name='country',
            options={'ordering': ['country_name'], 'verbose_name_plural': 'countries'},
        ),
        migrations.RenameField(
            model_name='place',
            old_name='date',
            new_name='end_date',
        ),
        migrations.AddField(
            model_name='place',
            name='city',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='place',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='travels.Country'),
        ),
        migrations.AddField(
            model_name='place',
            name='start_date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='place',
            name='place',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
