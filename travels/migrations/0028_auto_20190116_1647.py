# Generated by Django 2.1.5 on 2019-01-16 15:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('travels', '0027_auto_20190116_1647'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='flight',
            options={'ordering': ['date']},
        ),
        migrations.RenameField(
            model_name='flight',
            old_name='date2',
            new_name='date',
        ),
    ]
