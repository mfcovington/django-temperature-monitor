# Generated by Django 2.1.4 on 2019-11-05 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('temperature_monitor', '0002_auto_20190102_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensor',
            name='battery',
            field=models.CharField(blank=True, max_length=7, null=True),
        ),
    ]
