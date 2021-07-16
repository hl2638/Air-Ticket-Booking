from django import forms
from datetime import datetime
from .models import *

YEAR_CHOICES = [str(year) for year in range(2000, datetime.now().year + 20)]


class FlightSearchForm(forms.Form):
    airline_name = forms.ModelChoiceField(required=False, queryset=Airline.objects.all())
    flight_num = forms.CharField(required=False)
    departure_airport = forms.ModelChoiceField(required=False, queryset=Airport.objects.all())
    arrival_airport = forms.ModelChoiceField(required=False, queryset=Airport.objects.all())
    date = forms.DateField(initial=datetime.now(), widget=forms.SelectDateWidget(years=YEAR_CHOICES, attrs={'class': 'm-2'}))

