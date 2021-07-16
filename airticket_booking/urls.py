from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='airticket_booking-home'),
    path('search_flights/', views.search_flights, name='search_flights'),
]
