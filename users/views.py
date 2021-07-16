from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView
from .forms import AirlineStaffRegisterForm, BookingAgentRegisterForm, CustomerRegisterForm, AirlineStaffLoginForm, BookingAgentLoginForm, CustomerLoginForm
from airticket_booking.models import User


def register(request):
    return render(request, 'users/register.html')


class RegisterAirlineStaffView(CreateView):
    model = User
    form_class = AirlineStaffRegisterForm
    template_name = 'users/register_base.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Airline Staff'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        username = form.cleaned_data.get('username')
        messages.success(self.request, f'Account created for {username}!')
        auth_login(self.request, user, backend='users.AirlineStaffAuthBackend')
        return redirect('airticket_booking-home')


class RegisterBookingAgentView(CreateView):
    model = User
    form_class = BookingAgentRegisterForm
    template_name = 'users/register_base.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Booking Agent'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        username = form.cleaned_data.get('agent_id')
        messages.success(self.request, f'Account created for {username}!')
        auth_login(self.request, user, backend='users.BookingAgentAuthBackend')
        return redirect('airticket_booking-home')


class RegisterCustomerView(CreateView):
    model = User
    form_class = CustomerRegisterForm
    template_name = 'users/register_base.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Customer'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        username = form.cleaned_data.get('name')
        messages.success(self.request, f'Account created for {username}!')
        auth_login(self.request, user)
        return redirect('airticket_booking-home')


def login(request):
    return render(request, 'users/login.html')


class LoginAirlineStaffView(LoginView):
    form_class = AirlineStaffLoginForm
    template_name = 'users/login_base.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'AirlineStaff'
        return super().get_context_data(**kwargs)


class LoginBookingAgentView(LoginView):
    form_class = BookingAgentLoginForm
    template_name = 'users/login_base.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'BookingAgent'
        return super().get_context_data(**kwargs)


class LoginCustomerView(LoginView):
    form_class = CustomerLoginForm
    template_name = 'users/login_base.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Customer'
        return super().get_context_data(**kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        user_type = user.user_type
        display_name = user.username
        if user_type == User.AIRLINE_STAFF:
            display_name = user.username
        elif user_type == User.BOOKING_AGENT:
            display_name = user.bookingagent.agent_id
        elif user_type == User.CUSTOMER:
            display_name = user.customer.name
        kwargs['display_name'] = display_name
        return super().get_context_data(**kwargs)