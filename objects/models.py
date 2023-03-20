from django.contrib.gis.db import models
from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.auth.models import AbstractUser
from django.core import serializers
from django.shortcuts import get_object_or_404

# Create your models here.
class City(models.Model):
    name = models.CharField(max_length=200)
    focus = models.TextField(blank=True)
    location =  models.PointField(srid=4326, null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    followup = models.TextField(null=True,blank=True)
    area =  models.PolygonField(null=True,blank=True)
    level = models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    def __str__(self):
        return self.name
    def get_location(self):
        return GEOSGeometry(self.area).json

class CustomUser(AbstractUser):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    def __str__(self):
        return self.username

class Criteria(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

MALMO = [(1,"1/1"),(2,"1/2"),(5,"1/5"),(10,"1/10"),(20,"1/20"),(50,"1/50"),(100,"1/100"),(200,"1/200"),(500,"1/500"),(1000, "1/1000"),(10000, "1/10000"),(100000,"1/100000"),(1000000,"1/1000000")]

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    returntime = models.IntegerField(blank=True, null=True, choices=MALMO)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    criteria =  models.ForeignKey(Criteria, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class Object(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True)
    location =  models.GeometryField()
    altitude = models.DecimalField(max_digits=5,decimal_places=2)
    marginal = models.DecimalField(max_digits=5,decimal_places=2,null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    def get_location(self):
        return GEOSGeometry(self.location).json
    def needs_own(self):
        n = self.measure_set.count()
        if n == 0:
            return 2
        m = self.measure_set.filter(general=False).count()
        if m >= 1:
            return 1
        else:
            return 0
    def get_margin(self):
        # Get Malmö for the event
        malmo = self.event.returntime
        returntimes = get_object_or_404(Returntimes, city=self.city.id)
        # Get the relevant returntime based on malmö
        if malmo:
            returntime = getattr(returntimes, 'y'+str(malmo))
        else:
            returntime = 0
        # Calculate margin
        margin = self.altitude - returntime
        return margin
    class Meta:
        db_table = "objects_object2"

class Measure(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    cost = models.IntegerField()
    level = models.DecimalField(max_digits=5,decimal_places=2)
    general = models.BooleanField()
    object = models.ManyToManyField(Object)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class Pathway(models.Model):
    steg1 = models.ForeignKey(Measure, related_name='measure1', verbose_name="Första åtgärd",unique=False,on_delete=models.RESTRICT)
    steg2 = models.ForeignKey(Measure, related_name='measure2', verbose_name="Andra åtgärd",unique=False,blank=True,null=True,on_delete=models.RESTRICT)
    steg3 = models.ForeignKey(Measure, related_name='measure3', verbose_name="Tredje åtgärd",unique=False,blank=True,null=True,on_delete=models.RESTRICT)
    description = models.TextField(blank=True,null=True)
    cost = models.IntegerField(blank=True,null=True)
    level = models.DecimalField(max_digits=5,decimal_places=2)
    object = models.ForeignKey(Object,on_delete=models.RESTRICT,null=True)
    city = models.ForeignKey(City,on_delete=models.RESTRICT)
    user = models.ForeignKey(CustomUser,on_delete=models.RESTRICT)
    def __str__(self):
        return str(self.id)

class Returntimes(models.Model):
    city = models.ForeignKey(City,on_delete=models.RESTRICT)
    y1 = models.DecimalField(max_digits=5,decimal_places=2)
    y2 = models.DecimalField(max_digits=5,decimal_places=2)
    y5 = models.DecimalField(max_digits=5,decimal_places=2)
    y10 = models.DecimalField(max_digits=5,decimal_places=2)
    y20 = models.DecimalField(max_digits=5,decimal_places=2)
    y50 = models.DecimalField(max_digits=5,decimal_places=2)
    y100 = models.DecimalField(max_digits=5,decimal_places=2)
    y200 = models.DecimalField(max_digits=5,decimal_places=2)
    y500 = models.DecimalField(max_digits=5,decimal_places=2)
    y1000 = models.DecimalField(max_digits=5,decimal_places=2)
    y10000 = models.DecimalField(max_digits=5,decimal_places=2)
    y100000 = models.DecimalField(max_digits=5,decimal_places=2)
    y1000000 = models.DecimalField(max_digits=5,decimal_places=2)
    description = models.TextField(blank=True,null=True)
    def __str__(self):
        return str(self.id)
