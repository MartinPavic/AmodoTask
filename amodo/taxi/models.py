from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token


class Company(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    wage_per_km = models.FloatField()

    class Meta:
        verbose_name_plural = 'Companies'

    def __str__(self) -> str:
        return f"{self.name}"


class Vehicle(models.Model):
    car_manufacturer = models.CharField(max_length=200)
    model = models.CharField(max_length=200)
    year_of_production = models.IntegerField('year of production')
    license_plate = models.CharField(max_length=200)

    def __str__(self) -> str:
        return f"{self.car_manufacturer}: {self.model}, {self.year_of_production}"


class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vehicle = models.OneToOneField(
        Vehicle, null=True, on_delete=models.DO_NOTHING)
    company = models.OneToOneField(
        Company, null=True, on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return f"Driver: {self.id}"


class Trip(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.DO_NOTHING)
    lat = models.FloatField()
    lng = models.FloatField()
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self) -> str:
        return f"Trip: {self.id}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
