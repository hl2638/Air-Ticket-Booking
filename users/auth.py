from django.contrib.auth.backends import ModelBackend, BaseBackend
from django.contrib.auth.hashers import check_password
from airticket_booking.models import User, AirlineStaff, Customer, BookingAgent
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test

# dict_user_model = {
#     'AirlineStaff': AirlineStaff,
#     'Customer': Customer,
#     'BookingAgent': BookingAgent
# }

# class AirlineStaffAuthBackend(ModelBackend):
#
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         if username is None or password is None:
#             return
#         UserModel = AirlineStaff
#         try:
#             user = UserModel.objects.get(username=username)
#         except UserModel.DoesNotExist:
#             # Run the default password hasher once to reduce the timing
#             # difference between an existing and a nonexistent user (#20760).
#             UserModel().set_password(password)
#         else:
#             if user.check_password(password) and self.user_can_authenticate(user):
#                 return user


class AirlineStaffAuthBackend(BaseBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        if kwargs.get('user_type') is not None and kwargs.get('user_type') == 'AirlineStaff':
            print('AirlineStaff backend started')
            UserModel = User
        else:
            return None

        try:
            user = UserModel.objects.get(username=username, user_type=User.AIRLINE_STAFF)
            pwd_valid = user.check_password(password)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password):
                return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id, user_type=User.AIRLINE_STAFF)
        except User.DoesNotExist:
            return None


class BookingAgentAuthBackend(BaseBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        if kwargs.get('user_type') is not None and kwargs.get('user_type') == 'BookingAgent':
            print('BookingAgent backend started')
            UserModel = User
        else:
            return None

        email = kwargs['email']
        try:
            user = UserModel.objects.get(email=email, user_type=User.BOOKING_AGENT)
            pwd_valid = user.check_password(password)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password):
                return user
        return None

    def get_user(self, user_id):
        try:
            print(f'user_id = {user_id}')
            print(User.objects.filter(pk=user_id, user_type=User.BOOKING_AGENT))
            return User.objects.get(pk=user_id, user_type=User.BOOKING_AGENT)
        except User.DoesNotExist:
            return None


class CustomerAuthBackend(BaseBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        if kwargs.get('user_type') is not None and kwargs.get('user_type') == 'Customer':
            print('Customer backend started')
            UserModel = User
        else:
            return None

        email = kwargs['email']
        try:
            user = UserModel.objects.get(email=email, user_type=User.CUSTOMER)
            pwd_valid = user.check_password(password)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password):
                return user
        return None

    def get_user(self, user_id):
        try:
            # print(f'user_id = {user_id}')
            # print(User.objects.filter(pk=user_id, user_type=User.CUSTOMER))
            return User.objects.get(pk=user_id, user_type=User.CUSTOMER)
        except User.DoesNotExist:
            return None
