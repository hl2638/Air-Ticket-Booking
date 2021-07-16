from django import forms
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from airticket_booking.models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from datetime import datetime


YEAR_CHOICES = [str(year) for year in range(1900, datetime.now().year + 20)]


# class UserRegisterForm(UserCreationForm):
#     # email = forms.EmailField()
#
#     class Meta:
#         model = User
#         # fields = ['username', 'email', 'password1', 'password2']
#         fields = ['username', 'password1', 'password2']


class AirlineStaffRegisterForm(UserCreationForm):
    airline_name = forms.ModelChoiceField(queryset=Airline.objects.all())
    date_of_birth = forms.DateField(widget=forms.SelectDateWidget(years=YEAR_CHOICES, attrs={'class': 'm-2'}))

    # def clean(self):
    #     cleaned_data = super().clean()
    #     airline_name_data = cleaned_data.get('airline_name')
    #     if Airline.objects.get(airline_name_data) is None:
    #         msg = "Airline doesn't exist."
    #         self.add_error('airline_name', msg)

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = User.AIRLINE_STAFF
        if commit:
            user.save()
        kwargs = {'user': user, 'date_of_birth': self.cleaned_data.get('date_of_birth'), 'airline_name': self.cleaned_data.get('airline_name')}
        airline_staff = AirlineStaff.objects.create(**kwargs)
        return user

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'date_of_birth', 'airline_name']


class BookingAgentRegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=50)
    agent_id = forms.CharField(max_length=50)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(user_type=User.BOOKING_AGENT, email=email):  # if booking agent with same email exists:
            raise forms.ValidationError(
                'Email already used by a Booking Agent.',
                code='email_exists',
            )
        return email

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data.get('agent_id')
        user.email = self.cleaned_data.get('email')
        user.user_type = User.BOOKING_AGENT
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            kwargs = {'user': user, 'agent_id': self.cleaned_data.get('agent_id')}
            booking_agent = BookingAgent.objects.create(**kwargs)
        return user

    class Meta:
        model = User
        fields = ['email', 'agent_id']


class CustomerRegisterForm(UserCreationForm):
    date_of_birth = forms.DateField(widget=forms.SelectDateWidget(years=YEAR_CHOICES, attrs={'class': 'm-2'}))
    email = forms.EmailField(max_length=50)
    name = forms.CharField(max_length=50)
    building_number = forms.CharField(max_length=30)
    street = forms.CharField(max_length=30)
    city = forms.CharField(max_length=30)
    state = forms.CharField(max_length=30)
    phone_number = forms.CharField(max_length=30)
    passport_number = forms.CharField(max_length=30)
    passport_expiration = forms.DateField(widget=forms.SelectDateWidget(years=YEAR_CHOICES, attrs={'class': 'm-2'}))
    passport_country = forms.CharField(max_length=50)

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = 'cust_' + self.cleaned_data.get('name').replace(' ', '_') + '_' + user.email
        user.user_type = User.CUSTOMER
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            kwargs = {'user': user,
                      'date_of_birth': self.cleaned_data.get('date_of_birth'), 'name': self.cleaned_data.get('name'),
                      'building_number': self.cleaned_data.get('building_number'), 'street': self.cleaned_data.get('street'),
                      'city': self.cleaned_data.get('city'), 'state': self.cleaned_data.get('state'),
                      'phone_number': self.cleaned_data.get('phone_number'),
                      'passport_number': self.cleaned_data.get('passport_number'), 'passport_expiration': self.cleaned_data.get('passport_expiration'),
                      'passport_country': self.cleaned_data.get('passport_country'),
                      }
            customer = Customer.objects.create(**kwargs)
        return user

    class Meta:
        model = User
        fields = ['email', 'name', 'date_of_birth', 'building_number', 'street', 'city', 'state', 'phone_number',
                  'passport_number', 'passport_expiration', 'passport_country']


class AirlineStaffLoginForm(AuthenticationForm):

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            print('Authenticating for airline staff from the form')
            self.user_cache = authenticate(self.request, username=username, password=password, user_type='AirlineStaff')
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class BookingAgentLoginForm(AuthenticationForm):

    email = forms.EmailField(max_length=50)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = authenticate(self.request, email=email, password=password, user_type='BookingAgent')
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username')
        self.order_fields(['email', 'password'])

    class Meta:
        fields = ['email', 'password']


class CustomerLoginForm(AuthenticationForm):

    email = forms.EmailField(max_length=50)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = authenticate(self.request, email=email, password=password, user_type='Customer')
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username')
        self.order_fields(['email', 'password'])

    class Meta:
        fields = ['email', 'password']