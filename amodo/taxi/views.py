from django.http.response import Http404, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseServerError, JsonResponse
from django.contrib.auth import login
from django.shortcuts import render
from django.urls import reverse

from rest_framework import generics, status
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import HttpRequest, Request
from rest_framework.reverse import reverse
from rest_framework.parsers import ParseError

from .forms import CustomUserCreationForm
from .permissions import IsVehicleOwner
from .models import Company, Driver, Trip, Vehicle
from .serializers import CompanySerializer, DriverSerializer, TripSerializer, VehicleSerializer


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'drivers': reverse('driver-list', request=request, format=format),
        'companies': reverse('company-list', request=request, format=format)
    })


class CompanyList(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAdminUser]


class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAdminUser]


class DriverList(generics.ListAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class DriverDetail(generics.RetrieveUpdateAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def update(self, request: Request, *args, **kwargs):
        try:
            driver = Driver.objects.get(user=request.user)
            if driver.company != None:
                return Response("Company already chosen", status=status.HTTP_400_BAD_REQUEST)
            company = Company.objects.get(id=int(request.data['company_id']))
            driver.company = company
            driver.save()
            return Response("Company successfully chosen", status=status.HTTP_200_OK)
        except Company.DoesNotExist:
            return Http404
        except Company.MultipleObjectsReturned:
            return HttpResponseServerError
        except ParseError as e:
            return HttpResponseBadRequest(e.detail)


class VehicleList(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request: HttpRequest, *args, **kwargs):
        driver = Driver.objects.get(user=request.user)
        response = super().create(request, *args, **kwargs)
        driver.vehicle = Vehicle.objects.get(id=response.data['id'])
        driver.save()
        return response


class VehicleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated, IsVehicleOwner]


def register_driver(request: HttpRequest):
    if request.method == "GET":
        return render(
            request, "taxi/register.html",
            {"form": CustomUserCreationForm}
        )
    elif request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            driver = Driver(user=user)
            driver.save()
            serializer = DriverSerializer(driver)
            login(request, user)
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(form.errors, status=400)


class TripList(generics.ListCreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request: Request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        driver = Driver.objects.get(user=request.user)
        trip = Trip(driver=driver)
        serializer = self.get_serializer(instance=trip, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
