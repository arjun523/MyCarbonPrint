from django.db import models
from django.utils import timezone

# Create your models here.
class co2web(models.Model):
    url = models.CharField(default="",primary_key=True,max_length=10000)
    co2 = models.FloatField(default=0.0)
    date = models.CharField(default="",max_length=100)
    green_web = models.BooleanField(default=False)
    cleaner_than = models.IntegerField(default=0)
    co2_equivalent = models.FloatField(default=0.0)
    sumo_weight = models.FloatField(default=0.0)
    cups = models.IntegerField(default=0)
    tree = models.IntegerField(default=0)
    energy = models.FloatField(default=0.0)
    car_distance = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    msg1 = models.CharField(default="",max_length=100)
    msg2 = models.CharField(default="",max_length=100)
    msg3 = models.CharField(default="",max_length=100)

    
