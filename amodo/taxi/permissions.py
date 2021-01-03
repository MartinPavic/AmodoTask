from rest_framework import permissions

from .models import Driver


class IsVehicleOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, vehicle):
        try:
            driver = Driver.objects.get(user=request.user)
        except Driver.DoesNotExist:
            return False
        return vehicle == driver.vehicle
