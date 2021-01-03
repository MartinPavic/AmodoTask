from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('', views.api_root),
    path('companies/', views.CompanyList.as_view(), name='company-list'),
    path('companies/<int:pk>', views.CompanyDetail.as_view(), name='company-detail'),
    path('drivers/', views.DriverList.as_view(), name='driver-list'),
    path('drivers/<int:pk>/', views.DriverDetail.as_view(), name='driver-detail'),
    path('vehicles/', views.VehicleList.as_view(), name='vehicle-list'),
    path('vehicles/<int:pk>/', views.VehicleDetail.as_view(), name='vehicle-detail'),
    path('trips/', views.TripList.as_view(), name='trip-list'),
    path('register/', views.register_driver, name='register-driver')
]

urlpatterns = format_suffix_patterns(urlpatterns)
