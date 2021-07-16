from django import forms
from datetime import datetime
from .models import *

YEAR_CHOICES = [str(year) for year in range(2000, datetime.now().year + 20)]


class DateRangeForm(forms.Form):

    start_date = forms.DateField(initial=datetime.now(),
                           widget=forms.SelectDateWidget(years=YEAR_CHOICES, attrs={'class': 'm-2'}))
    end_date = forms.DateField(initial=datetime.now(),
                           widget=forms.SelectDateWidget(years=YEAR_CHOICES, attrs={'class': 'm-2'}))

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['start_date'] <= cleaned_data['end_date']:
            return cleaned_data
        else:
            raise forms.ValidationError("Date range invalid.")


class AirlineFlightSearchForm(DateRangeForm):
    flight_num = forms.CharField(required=False)
    departure_airport = forms.ModelChoiceField(required=False, queryset=Airport.objects.all())
    arrival_airport = forms.ModelChoiceField(required=False, queryset=Airport.objects.all())


class FlightSearchForm(DateRangeForm):
    airline_name = forms.ModelChoiceField(required=False, queryset=Airline.objects.all())
    flight_num = forms.CharField(required=False)
    departure_airport = forms.ModelChoiceField(required=False, queryset=Airport.objects.all())
    arrival_airport = forms.ModelChoiceField(required=False, queryset=Airport.objects.all())


class CustomerTicketPurchaseForm(forms.Form):
    # customer_email = forms.EmailField()
    pass


class BookingAgentTicketPurchaseForm(forms.Form):
    customer_email = forms.EmailField()

    def clean_customer_email(self):
        cleaned_data = super().clean()
        try:
            email = cleaned_data.get('customer_email')
            user = User.objects.get(email=email)
            return email
        except:
            raise forms.ValidationError("No customer with the given email address exists.")


class FlightCreationForm(forms.Form):
    flight_num = forms.IntegerField()
    airplane = forms.ModelChoiceField(queryset=Airplane.objects.all())
    departure_airport = forms.ModelChoiceField(queryset=Airport.objects.all())
    departure_time = forms.DateTimeField(initial=datetime.now(),)
    arrival_airport = forms.ModelChoiceField(queryset=Airport.objects.all())
    arrival_time = forms.DateTimeField(initial=datetime.now(),)
    price = forms.DecimalField()
    status = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.airline_name = kwargs.pop('airline_name', None)
        super().__init__(*args, **kwargs)
        self.fields['airplane'].queryset = Airplane.objects.filter(airline_name=self.airline_name)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['departure_time'] < cleaned_data['arrival_time']:
            return cleaned_data
        else:
            raise forms.ValidationError("Time range invalid.")


class FlightStatusChangeForm(forms.Form):
    status = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.status = kwargs.pop('status', None)
        super().__init__(*args, **kwargs)
        self.fields['status'].initial = self.status


class AirplaneCreationForm(forms.Form):
    airplane_id = forms.IntegerField()
    seats = forms.IntegerField()


class AirportCreationForm(forms.Form):
    airport_name = forms.CharField()
    airport_city = forms.CharField()
