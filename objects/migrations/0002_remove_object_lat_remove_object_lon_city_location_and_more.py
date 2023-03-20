# Generated by Django 4.0.3 on 2022-03-04 08:27

import django.contrib.gis.db.models.fields
import django.contrib.gis.geos.point
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='object',
            name='lat',
        ),
        migrations.RemoveField(
            model_name='object',
            name='lon',
        ),
        migrations.AddField(
            model_name='city',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(default=django.contrib.gis.geos.point.Point(0.0, 0.0), geography=True, srid=4326),
        ),
        migrations.AddField(
            model_name='object',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(default=django.contrib.gis.geos.point.Point(0.0, 0.0), geography=True, srid=4326),
        ),
    ]