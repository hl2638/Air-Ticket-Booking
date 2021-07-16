# Generated by Django 3.0.3 on 2020-05-11 20:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('airticket_booking', '0003_auto_20200511_2042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchases',
            name='booking_agent_id',
            field=models.ForeignKey(db_column='booking_agent_id', default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='airticket_booking.BookingAgent'),
        ),
    ]