# Generated by Django 3.0.3 on 2020-04-23 06:24

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('user_type', models.PositiveSmallIntegerField(choices=[(1, 'Airline Staff'), (2, 'Booking Agent'), (3, 'Customer'), (4, 'admin')], default=4)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Airline',
            fields=[
                ('airline_name', models.CharField(max_length=50, primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'airline',
            },
        ),
        migrations.CreateModel(
            name='Airplane',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('airplane_id', models.IntegerField()),
                ('seats', models.IntegerField()),
                ('airline_name', models.ForeignKey(db_column='airline_name', on_delete=django.db.models.deletion.DO_NOTHING, to='airticket_booking.Airline')),
            ],
            options={
                'db_table': 'airplane',
                'unique_together': {('airline_name', 'airplane_id')},
            },
        ),
        migrations.CreateModel(
            name='Airport',
            fields=[
                ('airport_name', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('airport_city', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'airport',
            },
        ),
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flight_num', models.IntegerField()),
                ('departure_time', models.DateTimeField()),
                ('arrival_time', models.DateTimeField()),
                ('price', models.DecimalField(decimal_places=0, max_digits=10)),
                ('status', models.CharField(max_length=50)),
                ('airplane', models.ForeignKey(db_column='airplane', on_delete=django.db.models.deletion.DO_NOTHING, to='airticket_booking.Airplane')),
                ('arrival_airport', models.ForeignKey(db_column='arrival_airport', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='airticket_booking.Airport')),
                ('departure_airport', models.ForeignKey(db_column='departure_airport', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='airticket_booking.Airport')),
            ],
            options={
                'db_table': 'flight',
                'unique_together': {('flight_num', 'departure_time')},
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('ticket_id', models.IntegerField(primary_key=True, serialize=False)),
                ('flight', models.ForeignKey(db_column='flight', on_delete=django.db.models.deletion.DO_NOTHING, to='airticket_booking.Flight')),
            ],
            options={
                'db_table': 'ticket',
            },
        ),
        migrations.CreateModel(
            name='BookingAgent',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('agent_id', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'booking_agent',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('name', models.CharField(max_length=50)),
                ('building_number', models.CharField(max_length=30)),
                ('street', models.CharField(max_length=30)),
                ('city', models.CharField(max_length=30)),
                ('state', models.CharField(max_length=30)),
                ('phone_number', models.CharField(max_length=15)),
                ('passport_number', models.CharField(max_length=30)),
                ('passport_expiration', models.DateField()),
                ('passport_country', models.CharField(max_length=50)),
                ('date_of_birth', models.DateField()),
            ],
            options={
                'db_table': 'customer',
            },
        ),
        migrations.CreateModel(
            name='AirlineStaff',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('date_of_birth', models.DateField()),
                ('airline_name', models.ForeignKey(db_column='airline_name', on_delete=django.db.models.deletion.DO_NOTHING, to='airticket_booking.Airline')),
            ],
            options={
                'db_table': 'airline_staff',
            },
        ),
        migrations.CreateModel(
            name='Purchases',
            fields=[
                ('ticket_id', models.OneToOneField(db_column='ticket_id', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='airticket_booking.Ticket')),
                ('booking_agent_id', models.IntegerField(blank=True, null=True)),
                ('purchase_date', models.DateField()),
                ('customer_email', models.ForeignKey(db_column='customer_email', on_delete=django.db.models.deletion.DO_NOTHING, to='airticket_booking.Customer')),
            ],
            options={
                'db_table': 'purchases',
                'unique_together': {('ticket_id', 'customer_email')},
            },
        ),
    ]