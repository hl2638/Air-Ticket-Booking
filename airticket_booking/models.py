from django.db import models
from django.db.models import CheckConstraint, Q, F
# from users.models import AirlineStaff, Customer, BookingAgent
from django.contrib.auth.models import AbstractUser


class Airline(models.Model):
    airline_name = models.CharField(primary_key=True, max_length=50)

    def __str__(self):
        return self.airline_name

    class Meta:
        db_table = 'airline'


class Airplane(models.Model):
    airline_name = models.ForeignKey(Airline, models.DO_NOTHING, db_column='airline_name')
    airplane_id = models.IntegerField()
    seats = models.IntegerField()

    def __str__(self):
        return f'{self.airline_name} {self.airplane_id}'

    class Meta:
        db_table = 'airplane'
        unique_together = (('airline_name', 'airplane_id'),)


class Airport(models.Model):
    airport_name = models.CharField(primary_key=True, max_length=50)
    airport_city = models.CharField(max_length=50)

    def __str__(self):
        return '%s/%s' %(self.airport_city, self.airport_name)

    class Meta:
        db_table = 'airport'


class Flight(models.Model):
    # airplane_id = models.ForeignKey(Airplane, models.DO_NOTHING, db_column='airplane_id', related_name='+')
    airplane = models.ForeignKey(Airplane, models.DO_NOTHING, db_column='airplane')
    flight_num = models.IntegerField()
    departure_airport = models.ForeignKey(Airport, models.DO_NOTHING, db_column='departure_airport', related_name='+')
    departure_time = models.DateTimeField()
    arrival_airport = models.ForeignKey(Airport, models.DO_NOTHING, db_column='arrival_airport', related_name='+')
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=0)
    status = models.CharField(max_length=50)

    @property
    def airline_name(self):
        return self.airplane.airline_name

    def __str__(self):
        return '%s %s, %s' %(self.departure_time.strftime('%m-%d-%Y', ), self.airplane.airline_name, self.flight_num)

    class Meta:
        db_table = 'flight'
        # unique_together = (('airline_name', 'flight_num', 'departure_time'), ('airline_name', 'airplane_id', 'departure_time'),)
        unique_together = (('flight_num', 'departure_time'),)


class Ticket(models.Model):
    ticket_id = models.CharField(max_length=20, primary_key=True)
    # airline_name = models.ForeignKey(Flight, models.DO_NOTHING, db_column='airline_name', related_name='+')
    # flight_num = models.ForeignKey(Flight, models.DO_NOTHING, db_column='flight_num')
    flight = models.ForeignKey(Flight, models.DO_NOTHING, db_column='flight')

    def __str__(self):
        return self.ticket_id

    class Meta:
        db_table = 'ticket'
        # unique_together = (('airline_name', 'flight_num'),)


class User(AbstractUser):
    # username is the field for identification for all users (not email), but authentication can be customized to not use username.
    USER_TYPE_CHOICES = (
        (1, 'Airline Staff'),
        (2, 'Booking Agent'),
        (3, 'Customer'),
        (4, 'admin'),
    )
    AIRLINE_STAFF = 1;
    BOOKING_AGENT = 2;
    CUSTOMER = 3;
    ADMIN = 4
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=ADMIN)

    class Meta:
        db_table = 'user'


class AirlineStaff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    date_of_birth = models.DateField()
    airline_name = models.ForeignKey(Airline, models.DO_NOTHING, db_column='airline_name')

    def __str__(self):
        return f'{self.airline_name}, {self.user.first_name} {self.user.last_name}'

    class Meta:
        db_table = 'airline_staff'


class BookingAgent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    agent_id = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.agent_id}'

    class Meta:
        db_table = 'booking_agent'


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    name = models.CharField(max_length=50)
    building_number = models.CharField(max_length=30)
    street = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15)
    passport_number = models.CharField(max_length=30)
    passport_expiration = models.DateField()
    passport_country = models.CharField(max_length=50)
    date_of_birth = models.DateField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'customer'


class Purchases(models.Model):
    ticket_id = models.OneToOneField('Ticket', models.DO_NOTHING, db_column='ticket_id', primary_key=True)
    customer_email = models.ForeignKey(Customer, models.DO_NOTHING, db_column='customer_email')
    booking_agent_id = models.IntegerField(blank=True, null=True)
    purchase_date = models.DateField()

    class Meta:
        db_table = 'purchases'
        unique_together = (('ticket_id', 'customer_email'),)
