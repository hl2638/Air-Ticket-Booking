from django.shortcuts import render
from .models import *
from .forms import FlightSearchForm
from django.utils.timezone import now, timedelta
from django.http import HttpResponse


def home(request):
    title = 'Home'
    all_flights = Flight.objects.all()
    recent_flights = Flight.objects.filter(arrival_time__gte=now() - timedelta(hours=2),
                                           departure_time__lte=now() + timedelta(hours=2)).order_by('departure_time')
    for flight in recent_flights:
        flight.departure_time = flight.departure_time.strftime('%H:%M')
        flight.arrival_time = flight.arrival_time.strftime('%H:%M')
    return render(request, 'airticket_booking/home.html',
                  {'title': title, 'flights': recent_flights})


def search_flights(request):
    template = 'airticket_booking/search_flights.html'

    if request.method == 'POST':
        form = FlightSearchForm(request.POST)
        if form.is_valid():
            airline_name = form.cleaned_data.get('airline_name')
            flight_num = form.cleaned_data.get('flight_num')
            print(flight_num)
            departure_airport = form.cleaned_data.get('departure_airport')
            arrival_airport = form.cleaned_data.get('arrival_airport')
            date = form.cleaned_data.get('date')
            kwargs = {
                'airplane__airline_name': airline_name,
                'flight_num': flight_num,
                'departure_airport': departure_airport,
                'arrival_airport': arrival_airport,
                'departure_time__date': date,
            }
            items = list(kwargs.items())
            for key, value in items:
                if value is None or value == '':
                    kwargs.pop(key)
            print(kwargs)
            results = Flight.objects.filter(**kwargs)[:20]  # only first 20 results to prevent crash (wouldn't happen unless there's a million of them though)
            return render(request, template, {'form': form, 'results': results})

    else:
        form = FlightSearchForm()
        return render(request, template, {'form': form})


# def staff_view_flights(request):
#     title = 'View Flights'
#     flights =
