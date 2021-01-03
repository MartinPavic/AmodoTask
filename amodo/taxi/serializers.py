from django.contrib.auth.models import User

from rest_framework import serializers

from .models import Company, Driver, Trip, Vehicle


class UserDriverRelation(serializers.RelatedField):
    queryset = User.objects.all()

    def to_representation(self, value):
        return {
            'id': value.id,
            'username': value.username,
            'email': value.email,
            'password': value.password
        }


class VehicleDriverRelation(serializers.RelatedField):
    queryset = Vehicle.objects.all()

    def to_representation(self, value):
        return {
            'id': value.id,
            'car_manufacturer': value.car_manufacturer,
            'model': value.model,
            'year_of_production': value.year_of_production,
            'license_plate': value.license_plate
        }


class CompanyDriverRelation(serializers.RelatedField):
    queryset = Company.objects.all()

    def to_representation(self, value):
        return {
            'id': value.id,
            'name': value.name,
            'address': value.address,
            'wage_per_km': value.wage_per_km,
        }


class DriverSerializer(serializers.ModelSerializer):
    user = UserDriverRelation()
    vehicle = VehicleDriverRelation()
    company = CompanyDriverRelation()

    class Meta:
        model = Driver
        fields = ['user', 'vehicle', 'company']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'address', 'wage_per_km']


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'car_manufacturer', 'model',
                  'year_of_production', 'license_plate']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['id', 'lat', 'lng', 'timestamp']
