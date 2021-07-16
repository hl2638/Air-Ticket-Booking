from django.shortcuts import render
from .models import *
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, RedirectView, FormView
from django.utils.timezone import now, timedelta
from django.urls import reverse
from django.db import transaction
from django.db.models import Max, Sum, Avg, Count
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import HttpResponse
from datetime import datetime, timedelta


def get_display_name(request):
    user = request.user
    try:
        user_type = user.user_type
    except:
        return None
    # display name
    if user_type == User.CUSTOMER:
        customer = Customer.objects.get(user=user)
        return customer.name
    elif user_type == User.BOOKING_AGENT:
        booking_agent = BookingAgent.objects.get(user=user)
        return booking_agent.agent_id
    elif user_type == User.AIRLINE_STAFF:
        return user.username
    elif user_type == User.ADMIN:
        return user.username


def get_last_month(date):
    #     returns the last day of the last month
    return date - timedelta(days=date.day)


def get_month_end(date):
    #     returns the last day of this month
    if date.month != 12:
        date = date.replace(month=date.month + 1)
    else:
        date = date.replace(year=date.year + 1, month=1)
    return date - timedelta(days=date.day)


class UserTemplateView(TemplateView):

    def get_context_data(self, **kwargs):
        user = self.request.user
        user_type = user.user_type
        # display name
        if user_type == User.CUSTOMER:
            customer = Customer.objects.get(user=user)
            kwargs['display_name'] = customer.name
        elif user_type == User.BOOKING_AGENT:
            booking_agent = BookingAgent.objects.get(user=user)
            kwargs['display_name'] = booking_agent.agent_id
        elif user_type == User.AIRLINE_STAFF:
            kwargs['display_name'] = user.username
        elif user_type == User.ADMIN:
            kwargs['display_name'] = user.username
        return super().get_context_data(**kwargs)


def home(request):
    title = 'Home'
    all_flights = Flight.objects.all()
    recent_flights = Flight.objects.filter(arrival_time__gte=now() - timedelta(hours=2),
                                           departure_time__lte=now() + timedelta(hours=2)).order_by('departure_time')
    if len(recent_flights) == 0:
        recent_flights = Flight.objects.all()[:max(10, Flight.objects.count())]
    for flight in recent_flights:
        if flight.departure_time != now().day:
            flight.departure_date = flight.departure_time.strftime('%m-%d-%Y')
        flight.departure_time = flight.departure_time.strftime('%H:%M')
        flight.arrival_time = flight.arrival_time.strftime('%H:%M')

    messages = []
    if request.user.user_type == User.ADMIN:
        messages = ["You are logged in as ADMIN. It is not intended for anything outside of admin page. Please log out to try the use cases."]
    display_name = get_display_name(request)
    return render(request, 'airticket_booking/home.html',
                  {'title': title, 'flights': recent_flights, 'display_name': display_name, 'messages': messages})


def search_flights(request):
    template = 'airticket_booking/search_flights.html'
    display_name = get_display_name(request)

    if request.method == 'POST':
        form = FlightSearchForm(request.POST)
        if form.is_valid():
            airline_name = form.cleaned_data.get('airline_name')
            flight_num = form.cleaned_data.get('flight_num')
            print(flight_num)
            departure_airport = form.cleaned_data.get('departure_airport')
            arrival_airport = form.cleaned_data.get('arrival_airport')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            kwargs = {
                'airplane__airline_name': airline_name,
                'flight_num': flight_num,
                'departure_airport': departure_airport,
                'arrival_airport': arrival_airport,
                'departure_time__date__gte': start_date,
                'departure_time__date__lte': end_date,
            }
            items = list(kwargs.items())
            for key, value in items:
                if value is None or value == '':
                    kwargs.pop(key)
            print(kwargs)
            results = Flight.objects.filter(**kwargs)[
                      :20]  # only first 20 results to prevent crash (wouldn't happen unless there's a million of them though)
            no_result = False
            if len(results) == 0:
                no_result = True
            return render(request, template,
                          {'form': form, 'results': results, 'no_result': no_result, 'display_name': display_name})

    else:
        form = FlightSearchForm()
        return render(request, template, {'form': form, 'display_name': display_name})


class CustomerViewFlightsView(LoginRequiredMixin, UserTemplateView):
    template_name = 'airticket_booking/customer_view_flights.html'

    def get_context_data(self, **kwargs):
        # query for purchases. get flight from purchase.
        user = self.request.user
        kwargs['denied'] = False
        user_type = user.user_type
        if user_type != User.CUSTOMER:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)
        customer = Customer.objects.get(user=user)
        purchases = Purchases.objects.filter(customer_email=customer)
        past_flights = []
        current_flights = []
        for purchase in purchases:
            flight = purchase.ticket_id.flight

            if flight.arrival_time < now():
                past_flights.append(flight)
            else:
                current_flights.append(flight)

            if flight.departure_time != now().day:
                flight.departure_date = flight.departure_time.strftime('%m-%d-%Y')
            flight.departure_time = flight.departure_time.strftime('%H:%M')
            flight.arrival_time = flight.arrival_time.strftime('%H:%M')
        kwargs['past_flights'] = sorted(past_flights, key=lambda x: x.departure_time)
        kwargs['current_flights'] = sorted(current_flights, key=lambda x: x.departure_time)
        return super().get_context_data(**kwargs)


class BookingAgentViewFlightsView(LoginRequiredMixin, UserTemplateView):
    template_name = 'airticket_booking/booking_agent_view_flights.html'

    def get_context_data(self, **kwargs):
        # query for purchases. get flight from purchase.
        user = self.request.user
        kwargs['denied'] = False
        user_type = user.user_type
        if user_type != User.BOOKING_AGENT:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)
        booking_agent = BookingAgent.objects.get(user=user)
        purchases = Purchases.objects.filter(booking_agent_id=booking_agent)
        flights = []
        for purchase in purchases:
            flight = purchase.ticket_id.flight
            flights.append(flight)
            if flight.departure_time != now().day:
                flight.departure_date = flight.departure_time.strftime('%m-%d-%Y')
            flight.departure_time = flight.departure_time.strftime('%H:%M')
            flight.arrival_time = flight.arrival_time.strftime('%H:%M')
            flight.customer_email = purchase.customer_email.email
        kwargs['flights'] = sorted(flights, key=lambda x: x.departure_time)
        return super().get_context_data(**kwargs)


class AirlineStaffViewFlightsView(LoginRequiredMixin, FormView, UserTemplateView):
    template_name = 'airticket_booking/airline_staff_view_flights.html'
    form_class = AirlineFlightSearchForm

    def get_context_data(self, **kwargs):
        # query for purchases. get flight from purchase.
        user = self.request.user
        kwargs['denied'] = False
        user_type = user.user_type
        if user_type != User.AIRLINE_STAFF:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)
        airline_staff = AirlineStaff.objects.get(user=user)
        current_flights = Flight.objects.filter(airplane__airline_name=airline_staff.airline_name,
                                                arrival_time__gte=now())
        for flight in current_flights:
            if flight.departure_time != now().day:
                flight.departure_date = flight.departure_time.strftime('%m-%d-%Y')
            flight.departure_time = flight.departure_time.strftime('%H:%M')
            flight.arrival_time = flight.arrival_time.strftime('%H:%M')
        kwargs['current_flights'] = sorted(current_flights, key=lambda x: x.departure_time)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = self.request.user
        user_type = user.user_type
        if user_type != User.AIRLINE_STAFF:
            return
        airline_staff = AirlineStaff.objects.get(user=user)
        airline_name = airline_staff.airline_name
        flight_num = form.cleaned_data.get('flight_num')
        print(flight_num)
        departure_airport = form.cleaned_data.get('departure_airport')
        arrival_airport = form.cleaned_data.get('arrival_airport')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        kwargs = {
            'airplane__airline_name': airline_name,
            'flight_num': flight_num,
            'departure_airport': departure_airport,
            'arrival_airport': arrival_airport,
            'departure_time__date__gte': start_date,
            'departure_time__date__lte': end_date,
        }
        items = list(kwargs.items())
        for key, value in items:
            if value is None or value == '':
                kwargs.pop(key)
        # print(kwargs)
        result = {
            'flights': Flight.objects.filter(**kwargs)[:20]
            # only first 20 results to prevent crash (wouldn't happen unless there's a million of them though)
        }
        return render(self.request, self.template_name,
                      {'form': form, 'result': result})


class CustomerPortalView(LoginRequiredMixin, UserTemplateView):
    template_name = 'airticket_booking/customer_portal.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        user_type = user.user_type
        kwargs['denied'] = False
        if user_type != User.CUSTOMER:
            kwargs['denied'] = True
        return super().get_context_data(**kwargs)


class BookingAgentPortalView(LoginRequiredMixin, UserTemplateView):
    template_name = 'airticket_booking/booking_agent_portal.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        user_type = user.user_type
        kwargs['denied'] = False
        if user_type != User.BOOKING_AGENT:
            kwargs['denied'] = True
        return super().get_context_data(**kwargs)


class AirlineStaffPortalView(LoginRequiredMixin, UserTemplateView):
    template_name = 'airticket_booking/airline_staff_portal.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        user_type = user.user_type
        kwargs['denied'] = False
        if user_type != User.AIRLINE_STAFF:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)


class PortalRedirectView(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        user_type = user.user_type
        url = None
        if user_type == User.CUSTOMER:
            url = reverse('customer-portal')
        elif user_type == User.BOOKING_AGENT:
            url = reverse('booking-agent-portal')
        elif user_type == User.AIRLINE_STAFF:
            url = reverse('airline-staff-portal')
        elif user_type == User.ADMIN:
            url = reverse('admin')
        return url


class CustomerPurchaseTicketView(LoginRequiredMixin, UserTemplateView):
    template_name = 'airticket_booking/customer_purchase_ticket.html'

    def get_context_data(self, **kwargs):
        flight_pk = self.kwargs['flight_pk']
        flight = Flight.objects.get(pk=flight_pk)
        user = self.request.user
        kwargs['denied'] = False
        user_type = user.user_type

        if user_type != User.CUSTOMER:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)
        customer = Customer.objects.get(user=user)
        with transaction.atomic():
            max_ticket_id = Ticket.objects.all().aggregate(Max('ticket_id'))['ticket_id__max']
            new_ticket_id = max_ticket_id + 1
            ticket_kwargs = {
                'flight': flight,
                'ticket_id': new_ticket_id,
            }
            new_ticket = Ticket(**ticket_kwargs)
            new_ticket.save()
            purchase_kwargs = {
                'ticket_id': new_ticket,
                'customer_email': customer,
                'purchase_date': datetime.today()
            }
            new_purchase = Purchases(**purchase_kwargs)
            new_purchase.save()
            kwargs['flight'] = flight
            kwargs['customer_email'] = user.email
            return super().get_context_data(**kwargs)


class BookingAgentPurchaseTicketView(LoginRequiredMixin, FormView, UserTemplateView):
    template_name = 'airticket_booking/booking_agent_purchase_ticket.html'
    form_class = BookingAgentTicketPurchaseForm

    def get_context_data(self, **kwargs):
        user = self.request.user
        user_type = user.user_type
        kwargs['denied'] = False
        if user_type != User.BOOKING_AGENT:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        print("Form valid.")
        flight_pk = self.kwargs['flight_pk']
        flight = Flight.objects.get(pk=flight_pk)
        user = self.request.user
        booking_agent = BookingAgent.objects.get(user=user)
        customer_email = form.cleaned_data.get('customer_email')
        customer_user = User.objects.get(email=customer_email)
        customer = Customer.objects.get(user=customer_user)
        with transaction.atomic():
            max_ticket_id = Ticket.objects.all().aggregate(Max('ticket_id'))['ticket_id__max']
            new_ticket_id = max_ticket_id + 1
            ticket_kwargs = {
                'flight': flight,
                'ticket_id': new_ticket_id,
            }
            new_ticket = Ticket(**ticket_kwargs)
            new_ticket.save()
            purchase_kwargs = {
                'ticket_id': new_ticket,
                'customer_email': customer,
                'booking_agent_id': booking_agent,
                'purchase_date': datetime.today()
            }
            new_purchase = Purchases(**purchase_kwargs)
            new_purchase.save()
            print("Ticket purchase success for booking agent.")
            kwargs = {
                'ticket_id': new_ticket.ticket_id,
                'flight': flight,
                'customer_email': customer_email,
                'booking_agent_id': booking_agent.agent_id
            }
            return render(self.request, self.template_name, kwargs)


class PurchaseTicketRedirectView(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        user_type = user.user_type
        url = None
        if user_type == User.CUSTOMER:
            url = reverse('customer-purchase-ticket', args=args, kwargs=kwargs)
        elif user_type == User.BOOKING_AGENT:
            url = reverse('booking-agent-purchase-ticket', args=args, kwargs=kwargs)
        return url


class CustomerTrackSpendingView(LoginRequiredMixin, FormView, UserTemplateView):
    template_name = 'airticket_booking/customer_track_spending.html'
    form_class = DateRangeForm

    def get_context_data(self, **kwargs):
        user = self.request.user
        kwargs['denied'] = False
        user_type = user.user_type
        if user_type != User.CUSTOMER:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)
        # to render: list for labels, list for values
        customer = Customer.objects.get(user=user)
        my_purchases_without_agent = Purchases.objects.filter(customer_email=customer, booking_agent_id=None,
                                                              purchase_date__year=now().year - 1)
        my_purchases_with_agent = Purchases.objects.filter(
            Q(customer_email=customer) & ~Q(booking_agent_id=None) & Q(purchase_date__year=now().year - 1))
        sum1 = my_purchases_without_agent.aggregate(sum=Sum('ticket_id__flight__price'))['sum']
        if sum1 is None:    sum1 = 0
        sum2 = my_purchases_with_agent.aggregate(sum=Sum('ticket_id__flight__price'))['sum']
        if sum2 is None:    sum2 = 0
        total = float(sum1) + float(sum2) * 1.1
        labels = []
        data = []
        dt = time.today()
        date_start = get_last_month(dt) + timedelta(days=1)
        date_end = dt
        for i in range(6):
            labels.append(date_end.strftime('%Y-%m'))
            my_purchases_without_agent = Purchases.objects.filter(
                Q(customer_email=customer) & Q(booking_agent_id=None) & Q(purchase_date__gte=date_start) & Q(
                    purchase_date__lte=date_end))
            my_purchases_with_agent = Purchases.objects.filter(
                Q(customer_email=customer) & ~Q(booking_agent_id=None) & Q(purchase_date__gte=date_start) & Q(
                    purchase_date__lte=date_end))
            sum1 = my_purchases_without_agent.aggregate(sum=Sum('ticket_id__flight__price'))['sum']
            if sum1 is None:    sum1 = 0
            sum2 = my_purchases_with_agent.aggregate(sum=Sum('ticket_id__flight__price'))['sum']
            if sum2 is None:    sum2 = 0
            data.append(float(sum1) + float(sum2) * 1.1)
            date_end = get_last_month(date_end)
            date_start = get_last_month(date_end) + timedelta(days=1)
        labels.reverse()
        data.reverse()
        kwargs['total'] = total
        kwargs['labels'] = labels
        kwargs['data'] = data
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = self.request.user
        user_type = user.user_type
        if user_type != User.CUSTOMER:
            return
        customer = Customer.objects.get(user=user)
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        labels = []
        data = []
        tmp_start, tmp_end = start_date, min(end_date, get_month_end(start_date))
        while tmp_end <= end_date:
            labels.append(tmp_start.strftime('%Y-%m'))
            my_purchases_without_agent = Purchases.objects.filter(
                Q(customer_email=customer) & Q(booking_agent_id=None) & Q(purchase_date__gte=tmp_start) & Q(
                    purchase_date__lte=tmp_end))
            my_purchases_with_agent = Purchases.objects.filter(
                Q(customer_email=customer) & ~Q(booking_agent_id=None) & Q(purchase_date__gte=tmp_start) & Q(
                    purchase_date__lte=tmp_end))
            sum1 = my_purchases_without_agent.aggregate(sum=Sum('ticket_id__flight__price'))['sum']
            if sum1 is None:    sum1 = 0
            sum2 = my_purchases_with_agent.aggregate(sum=Sum('ticket_id__flight__price'))['sum']
            if sum2 is None:    sum2 = 0
            data.append(float(sum1) + float(sum2) * 1.1)
            tmp_start = tmp_end + timedelta(days=1)
            tmp_end = get_month_end(tmp_start)
        kwargs = self.get_context_data(**self.kwargs)
        kwargs['result'] = {'labels': labels, 'data': data}
        return render(self.request, self.template_name, kwargs)


class BookingAgentViewCommissionView(LoginRequiredMixin, FormView, UserTemplateView):
    template_name = 'airticket_booking/booking_agent_view_commission.html'
    form_class = DateRangeForm

    def get_context_data(self, **kwargs):
        user = self.request.user
        kwargs['denied'] = False
        user_type = user.user_type
        if user_type != User.BOOKING_AGENT:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)
        booking_agent = BookingAgent.objects.get(user=user)
        # total comm in past 30 days; avg comm; tol # of tickets
        start_date = datetime.today() - timedelta(days=29)
        end_date = datetime.today()
        purchases = Purchases.objects.filter(
            Q(booking_agent_id=booking_agent) & Q(purchase_date__gte=start_date) & Q(purchase_date__lte=end_date))

        total_commission = purchases.aggregate(sum=Sum('ticket_id__flight__price'))['sum']
        if total_commission is None: total_commission = 0
        total_commission = float(total_commission) * 0.1

        avg_commission = purchases.aggregate(avg=Avg('ticket_id__flight__price'))['avg']
        if avg_commission is None: avg_commission = 0
        avg_commission = float(avg_commission) * 0.1

        num_tickets = len(purchases)

        kwargs['total_commission'] = total_commission
        kwargs['avg_commission'] = avg_commission
        kwargs['num_tickets'] = num_tickets
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = self.request.user
        user_type = user.user_type
        if user_type != User.BOOKING_AGENT:
            return
        booking_agent = BookingAgent.objects.get(user=user)
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        purchases = Purchases.objects.filter(
            Q(booking_agent_id=booking_agent) & Q(purchase_date__gte=start_date) & Q(purchase_date__lte=end_date))

        total_commission = purchases.aggregate(sum=Sum('ticket_id__flight__price'))['sum']
        if total_commission is None:    total_commission = 0
        total_commission = float(total_commission) * 0.1

        avg_commission = purchases.aggregate(avg=Avg('ticket_id__flight__price'))['avg']
        if avg_commission is None: avg_commission = 0
        avg_commission = float(avg_commission) * 0.1

        num_tickets = len(purchases)

        kwargs = self.get_context_data(**self.kwargs)
        kwargs['result'] = {
            'total_commission': total_commission,
            'avg_commission': avg_commission,
            'num_tickets': num_tickets
        }
        return render(self.request, self.template_name, kwargs)


class BookingAgentViewTopCustomersView(LoginRequiredMixin, UserTemplateView):
    template_name = 'airticket_booking/booking_agent_view_top_customers.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        kwargs['denied'] = False
        user_type = user.user_type
        if user_type != User.BOOKING_AGENT:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)
        # to render: list for labels, list for values
        booking_agent = BookingAgent.objects.get(user=user)
        # top 5 customers on num of tickets in the past 6 months, and on commission in the last year.
        today = datetime.today()

        start_date = today.replace(month=today.month - 5) if today.month > 5 else today.replace(month=today.month + 7,
                                                                                                year=today.year - 1)
        end_date = today
        purchases = Purchases.objects.filter(
            Q(booking_agent_id=booking_agent) & Q(purchase_date__gte=start_date) & Q(purchase_date__lte=end_date))
        top_customers = purchases.values('customer_email').annotate(count=Count('ticket_id')).order_by('-count')[:5]
        labels1 = [Customer.objects.get(pk=item['customer_email']).email for item in top_customers]
        data1 = [item['count'] for item in top_customers]
        print("labels1 and data 1:")
        print(labels1)
        print(data1)
        kwargs['labels1'] = labels1
        kwargs['data1'] = data1

        purchases = Purchases.objects.filter(Q(booking_agent_id=booking_agent) & Q(purchase_date__year=today.year - 1))
        top_customers = purchases.values('customer_email').annotate(
            sum=Sum(F('ticket_id__flight__price') * 0.1)).order_by('-sum')[:5]
        labels2 = [Customer.objects.get(pk=item['customer_email']).email for item in top_customers]
        data2 = [float(item['sum']) for item in top_customers]
        print("labels2 and data 2:")
        print(labels2)
        print(data2)
        if len(labels2) > 0:
            kwargs['labels2'] = labels2
            kwargs['data2'] = data2

        return super().get_context_data(**kwargs)


class AirlineStaffCreateFlightView(LoginRequiredMixin, FormView, UserTemplateView):
    template_name = 'airticket_booking/airline_staff_create_flight.html'
    form_class = FlightCreationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        user_type = user.user_type
        if user_type != User.AIRLINE_STAFF:
            return
        airline_staff = AirlineStaff.objects.get(user=user)
        kwargs['airline_name'] = airline_staff.airline_name
        return kwargs

    def get_context_data(self, **kwargs):
        user = self.request.user
        kwargs['denied'] = False
        user_type = user.user_type
        if user_type != User.AIRLINE_STAFF:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = self.request.user
        user_type = user.user_type
        if user_type != User.AIRLINE_STAFF:
            return
        airline_staff = AirlineStaff.objects.get(user=user)
        airline_name = airline_staff.airline_name
        flight_num = form.cleaned_data.get('flight_num')
        airplane = form.cleaned_data.get('airplane')
        departure_time = form.cleaned_data.get('departure_time')
        departure_airport = form.cleaned_data.get('departure_airport')
        arrival_time = form.cleaned_data.get('arrival_time')
        arrival_airport = form.cleaned_data.get('arrival_airport')
        price = form.cleaned_data.get('price')
        status = form.cleaned_data.get('status')
        flight_kwargs = {
            'airplane': airplane,
            'flight_num': flight_num,
            'departure_airport': departure_airport,
            'departure_time': departure_time,
            'arrival_airport': arrival_airport,
            'arrival_time': arrival_time,
            'price': price,
            'status': status
        }
        with transaction.atomic():
            new_flight = Flight(**flight_kwargs)
            new_flight.save()
            kwargs = {
                'success': True,
                'flight': new_flight
            }
            return render(self.request, self.template_name,
                          kwargs)


class AirlineStaffChangeFlightStatusView(LoginRequiredMixin, FormView, UserTemplateView):
    template_name = 'airticket_booking/airline_staff_change_flight_status.html'
    form_class = FlightStatusChangeForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        flight_pk = self.kwargs.get('flight_pk')
        flight = Flight.objects.get(pk=flight_pk)
        kwargs['status'] = flight.status
        return kwargs

    def get_context_data(self, **kwargs):
        user = self.request.user
        kwargs['denied'] = False
        user_type = user.user_type
        if user_type != User.AIRLINE_STAFF:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = self.request.user
        user_type = user.user_type
        if user_type != User.AIRLINE_STAFF:
            return
        status = form.cleaned_data.get('status')
        flight_pk = self.kwargs.get('flight_pk')
        flight = Flight.objects.get(pk=flight_pk)
        with transaction.atomic():
            flight.status = status
            kwargs = {
                'success': True,
                'flight': flight
            }
            flight.save()
            return render(self.request, self.template_name,
                          kwargs)


class AirlineStaffViewFlightDetailView(LoginRequiredMixin, UserTemplateView):
    template_name = 'airticket_booking/airline_staff_view_flight_detail.html'

    def get_context_data(self, **kwargs):
        # query for purchases. get flight from purchase.
        user = self.request.user
        kwargs['denied'] = False
        user_type = user.user_type
        if user_type != User.AIRLINE_STAFF:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)
        flight = Flight.objects.get(pk=self.kwargs.get('flight_pk'))
        passenger_pks = Purchases.objects.filter(ticket_id__flight=flight).values('customer_email')
        passengers = [Customer.objects.get(pk=item['customer_email']) for item in passenger_pks]
        kwargs['flight'] = flight
        kwargs['passengers'] = passengers
        return super().get_context_data(**kwargs)


class AirlineStaffAddAirplaneView(LoginRequiredMixin, FormView, UserTemplateView):
    template_name = 'airticket_booking/airline_staff_add_airplane.html'
    form_class = AirplaneCreationForm

    def get_context_data(self, **kwargs):
        user = self.request.user
        kwargs['denied'] = False
        user_type = user.user_type
        if user_type != User.AIRLINE_STAFF:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = self.request.user
        user_type = user.user_type
        if user_type != User.AIRLINE_STAFF:
            return
        airline_staff = AirlineStaff.objects.get(user=user)
        airline_name = airline_staff.airline_name
        airplane_id = form.cleaned_data.get('airplane_id')
        seats = form.cleaned_data.get('seats')
        with transaction.atomic():
            airplane_kwargs = {
                'airline_name': airline_name,
                'airplane_id': airplane_id,
                'seats': seats
            }
            new_airplane = Airplane(**airplane_kwargs)
            new_airplane.save()
            kwargs = {
                'success': True,
                'airplane': new_airplane
            }
            return render(self.request, self.template_name,
                          kwargs)


class AirlineStaffViewAirplanesView(LoginRequiredMixin, UserTemplateView):
    template_name = 'airticket_booking/airline_staff_view_airplanes.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        kwargs['denied'] = False
        user_type = user.user_type
        if user_type != User.AIRLINE_STAFF:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)
        airline_staff = AirlineStaff.objects.get(user=user)
        airline_name = airline_staff.airline_name
        airplanes = Airplane.objects.filter(airline_name=airline_name)
        kwargs['airline_name'] = airline_name.airline_name
        kwargs['airplanes'] = airplanes
        return super().get_context_data(**kwargs)


class AirlineStaffAddAirportView(LoginRequiredMixin, FormView, UserTemplateView):
    template_name = 'airticket_booking/airline_staff_add_airport.html'
    form_class = AirportCreationForm

    def get_context_data(self, **kwargs):
        user = self.request.user
        kwargs['denied'] = False
        user_type = user.user_type
        if user_type != User.AIRLINE_STAFF:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = self.request.user
        user_type = user.user_type
        if user_type != User.AIRLINE_STAFF:
            return
        airline_staff = AirlineStaff.objects.get(user=user)
        airport_name = form.cleaned_data.get('airport_name')
        airport_city = form.cleaned_data.get('airport_city')
        try:
            airport = Airport.objects.get(airport_name=airport_name)
        except Airport.DoesNotExist:
            airport = None
        if airport is not None:
            kwargs = {
                'failed': True,
                'message': 'Could not add airport. Airport already exists.'
            }
            return render(self.request, self.template_name,
                          kwargs)
        with transaction.atomic():

            airport_kwargs = {
                'airport_name': airport_name,
                'airport_city': airport_city,
            }
            new_airport = Airport(**airport_kwargs)
            new_airport.save()
            kwargs = {
                'success': True,
                'airport': new_airport
            }
            return render(self.request, self.template_name,
                          kwargs)


class AirlineStaffViewBookingAgentsView(LoginRequiredMixin, UserTemplateView):
    template_name = 'airticket_booking/airline_staff_view_booking_agents.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        kwargs['denied'] = False
        user_type = user.user_type
        if user_type != User.AIRLINE_STAFF:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)
        # Top 5 booking agents based on number of tickets sales for the past month and past year. Top 5 booking agents based on the amount of commission received for the last year.
        today = datetime.today().replace(hour=0, minute=0, second=0)
        start_date = today.replace(month=today.month - 1, day=1) if today.month > 1 else today.replace(
            month=today.month + 1, year=today.year - 1, day=1)
        end_date = get_month_end(start_date)
        purchases = Purchases.objects.filter(Q(purchase_date__gte=start_date) & Q(purchase_date__lte=end_date)).exclude(
            booking_agent_id=None)
        top_booking_agents = purchases.values('booking_agent_id').annotate(count=Count('ticket_id')).order_by('-count')[
                             :5]
        booking_agents1 = [BookingAgent.objects.get(pk=item['booking_agent_id']) for item in top_booking_agents]
        kwargs['booking_agents1'] = [booking_agent for booking_agent in booking_agents1]

        start_date = today.replace(year=today.year - 1, month=1, day=1)
        end_date = today.replace(month=1, day=1) - timedelta(days=1)
        purchases = Purchases.objects.filter(Q(purchase_date__gte=start_date) & Q(purchase_date__lte=end_date)).exclude(
            booking_agent_id=None)
        top_booking_agents = purchases.values('booking_agent_id').annotate(count=Count('ticket_id')).order_by('-count')[
                             :5]
        booking_agents2 = [BookingAgent.objects.get(pk=item['booking_agent_id']) for item in top_booking_agents]
        kwargs['booking_agents2'] = [booking_agent for booking_agent in booking_agents2]

        start_date = today.replace(year=today.year - 1, month=1, day=1)
        end_date = today.replace(month=1, day=1) - timedelta(days=1)
        purchases = Purchases.objects.filter(Q(purchase_date__gte=start_date) & Q(
            purchase_date__lte=end_date)).exclude(booking_agent_id=None)
        top_booking_agents = purchases.values('booking_agent_id').annotate(
            sum=Sum(F('ticket_id__flight__price') * 0.1)).order_by('-sum')[:5]
        booking_agents3 = [BookingAgent.objects.get(pk=item['booking_agent_id']) for item in top_booking_agents]
        kwargs['booking_agents3'] = [booking_agent for booking_agent in booking_agents3]
        return super().get_context_data(**kwargs)


class AirlineStaffViewFrequentCustomerView(LoginRequiredMixin, UserTemplateView):
    template_name = 'airticket_booking/airline_staff_view_frequent_customers.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        kwargs['denied'] = False
        user_type = user.user_type
        if user_type != User.AIRLINE_STAFF:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)
        # Top 5 customers with the most purchases in the past year.
        today = datetime.today().replace(hour=0, minute=0, second=0)
        start_date = today.replace(year=today.year - 1, month=1, day=1)
        end_date = today.replace(month=1, day=1) - timedelta(days=1)
        purchases = Purchases.objects.filter(Q(purchase_date__gte=start_date) & Q(purchase_date__lte=end_date)).exclude(
            booking_agent_id=None)
        top_customers = purchases.values('customer_email').annotate(count=Count('ticket_id')).order_by('-count')[:5]
        customers = [Customer.objects.get(pk=item['customer_email']) for item in top_customers]
        kwargs['customers'] = customers
        return super().get_context_data(**kwargs)


class AirlineStaffViewCustomerDetailView(LoginRequiredMixin, UserTemplateView):
    template_name = 'airticket_booking/airline_staff_view_customer_detail.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        kwargs['denied'] = False
        user_type = user.user_type
        if user_type != User.AIRLINE_STAFF:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)
        airline_staff = AirlineStaff.objects.get(user=user)
        customer_pk = self.kwargs.get('customer_pk')
        customer = Customer.objects.get(pk=customer_pk)
        airline_name = airline_staff.airline_name
        purchases = Purchases.objects.filter(customer_email=customer)
        flights = [purchase.ticket_id.flight for purchase in purchases]
        for flight in flights:
            if flight.departure_time != now().day:
                flight.departure_date = flight.departure_time.strftime('%m-%d-%Y')
        kwargs['airline_name'] = airline_name.airline_name
        kwargs['flights'] = flights
        return super().get_context_data(**kwargs)


class AirlineStaffViewReportView(LoginRequiredMixin, FormView, UserTemplateView):
    template_name = 'airticket_booking/airline_staff_view_report.html'
    form_class = DateRangeForm

    def get_context_data(self, **kwargs):
        user = self.request.user
        kwargs['denied'] = False
        user_type = user.user_type
        if user_type != User.AIRLINE_STAFF:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)
        # to render: list for labels, list for values
        airline_staff = AirlineStaff.objects.get(user=user)
        airline_name = airline_staff.airline_name
        today = datetime.today().replace(hour=0, minute=0, second=0)
        start_date = today.replace(year=today.year - 1, month=1, day=1)
        end_date = today.replace(month=1, day=1) - timedelta(days=1)
        labels = []
        data = []
        tmp_start_date, tmp_end_date = start_date, get_month_end(start_date)
        while tmp_end_date <= end_date:
            labels.append(tmp_start_date.strftime('%Y-%m'))
            num_tickets = len(Purchases.objects.filter(ticket_id__flight__airplane__airline_name=airline_name,
                                                       purchase_date__gte=tmp_start_date,
                                                       purchase_date__lte=tmp_end_date))
            data.append(num_tickets)
            tmp_start_date = tmp_end_date + timedelta(days=1)
            tmp_end_date = get_month_end(tmp_start_date)
        kwargs['labels'] = labels
        kwargs['data'] = data
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = self.request.user
        user_type = user.user_type
        if user_type != User.AIRLINE_STAFF:
            return
        airline_staff = AirlineStaff.objects.get(user=user)
        airline_name = airline_staff.airline_name
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        labels = []
        data = []
        tmp_start_date, tmp_end_date = start_date, get_month_end(start_date)
        while tmp_end_date <= end_date:
            labels.append(tmp_start_date.strftime('%Y-%m'))
            num_tickets = len(
                Purchases.objects.filter(ticket_id__flight__airplane__airline_name=airline_name,
                                         purchase_date__gte=tmp_start_date,
                                         purchase_date__lte=tmp_end_date))
            data.append(num_tickets)
            tmp_start_date = tmp_end_date + timedelta(days=1)
            tmp_end_date = get_month_end(tmp_start_date)
        kwargs = self.get_context_data(**self.kwargs)
        kwargs['result'] = {'labels': labels, 'data': data}
        return render(self.request, self.template_name, kwargs)


class AirlineStaffViewComparisonView(LoginRequiredMixin, UserTemplateView):
    template_name = 'airticket_booking/airline_staff_view_comparison.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        kwargs['denied'] = False
        user_type = user.user_type
        if user_type != User.AIRLINE_STAFF:
            kwargs['denied'] = True
            return super().get_context_data(**kwargs)
        # to render: list for labels, list for values
        airline_staff = AirlineStaff.objects.get(user=user)
        airline_name = airline_staff.airline_name

        today = datetime.today().replace(hour=0, minute=0, second=0)
        start_date = today.replace(month=today.month - 1, day=1) if today.month > 1 else today.replace(
            month=today.month + 11, day=1, year=today.year - 1)
        end_date = get_month_end(start_date)
        purchases = Purchases.objects.filter(Q(purchase_date__gte=start_date) & Q(purchase_date__lte=end_date))
        direct_purchases = purchases.filter(Q(ticket_id__flight__airplane__airline_name=airline_name) &
                                            Q(booking_agent_id=None))
        direct_revenue = direct_purchases.aggregate(sum=Sum(F('ticket_id__flight__price')))['sum']
        if direct_revenue is None: direct_revenue = 0
        indirect_purchases = purchases.filter(
            Q(ticket_id__flight__airplane__airline_name=airline_name) & ~Q(booking_agent_id=None))
        indirect_revenue = indirect_purchases.aggregate(sum=Sum(F('ticket_id__flight__price')))['sum']
        if indirect_revenue is None: indirect_revenue = 0
        labels1 = ['Direct Sales', 'Indirect Sales']
        data1 = [direct_revenue, indirect_revenue]
        if data1[0] == 0 and data1[1] == 0:
            labels1 = None
        kwargs['labels1'] = labels1
        kwargs['data1'] = data1

        start_date = today.replace(year=today.year - 1, month=1, day=1)
        end_date = today.replace(month=1, day=1) - timedelta(days=1)
        purchases = Purchases.objects.filter(Q(purchase_date__gte=start_date) & Q(purchase_date__lte=end_date))
        direct_purchases = purchases.filter(Q(ticket_id__flight__airplane__airline_name=airline_name) &
                                            Q(booking_agent_id=None))
        direct_revenue = direct_purchases.aggregate(sum=Sum(F('ticket_id__flight__price')))['sum']
        if direct_revenue is None: direct_revenue = 0
        indirect_purchases = Purchases.objects.filter(
            Q(ticket_id__flight__airplane__airline_name=airline_name) & ~Q(booking_agent_id=None))
        indirect_revenue = indirect_purchases.aggregate(sum=Sum(F('ticket_id__flight__price')))['sum']
        if indirect_revenue is None: indirect_revenue = 0
        labels2 = ['Direct Sales', 'Indirect Sales']
        data2 = [float(direct_revenue), float(indirect_revenue)]
        kwargs['labels2'] = labels2
        kwargs['data2'] = data2
        if data2[0] == 0 and data2[1] == 0:
            labels2 = None
        return super().get_context_data(**kwargs)
