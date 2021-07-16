from django.contrib import admin
from .models import *
# Register your models here.
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from airticket_booking.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserAdmin(admin.ModelAdmin):
    form = UserChangeForm


admin.site.register(Airline)
admin.site.register(User, UserAdmin)
admin.site.register(AirlineStaff, UserAdmin)
admin.site.register(Customer, UserAdmin)
admin.site.register(BookingAgent, UserAdmin)
admin.site.register(Flight)
admin.site.register(Airplane)
admin.site.register(Airport)
admin.site.register(Ticket)
admin.site.register(Purchases)

admin.site.unregister(Group)
