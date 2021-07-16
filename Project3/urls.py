from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from users.forms import *
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('register/', user_views.register, name='register'),
    path('register/airlinestaff', user_views.RegisterAirlineStaffView.as_view(), name='registerAirlineStaff'),
    path('register/customer', user_views.RegisterCustomerView.as_view(), name='registerCustomer'),
    path('register/bookingagent', user_views.RegisterBookingAgentView.as_view(), name='registerBookingAgent'),

    path('profile/', user_views.ProfileView.as_view(), name='profile'),

    path('login/', user_views.login, name='login'),
    path('login/airlinestaff', user_views.LoginAirlineStaffView.as_view(), name='loginAirlineStaff'),
    path('login/customer', user_views.LoginCustomerView.as_view(), name='loginCustomer'),
    path('login/bookingagent', user_views.LoginBookingAgentView.as_view(), name='loginBookingAgent'),

    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('', include('airticket_booking.urls')),
]
