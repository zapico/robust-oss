# Generated by Django 4.0.3 on 2022-03-04 10:08

from django.conf import settings
import django.contrib.gis.db.models.fields
import django.contrib.gis.geos.point
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('objects', '0002_remove_object_lat_remove_object_lon_city_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='object',
            name='description',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='object',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(default=django.contrib.gis.geos.point.Point(0.0, 0.0), geography=True, null=True, srid=4326),
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('location', django.contrib.gis.db.models.fields.PolygonField(default='POLYGON ((0 0, 1 1, 2 2, 00))', geography=True, null=True, srid=4326)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='objects.city')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
