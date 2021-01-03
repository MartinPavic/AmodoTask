from django.contrib import admin
from .models import *

admin.site.register([Company, Driver, Vehicle])


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("driver", "lat", "lng", "timestamp")
    list_filter = ("driver",)
