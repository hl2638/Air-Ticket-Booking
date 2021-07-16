from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='airticket_booking-home'),
    path('search_flights/', views.search_flights, name='search-flights'),

    path('customer_view_flights/', views.CustomerViewFlightsView.as_view(), name='customer-view-flights'),
    path('booking_agent_view_flights/', views.BookingAgentViewFlightsView.as_view(), name='booking-agent-view-flights'),
    path('airline_staff_view_flights/', views.AirlineStaffViewFlightsView.as_view(), name='airline-staff-view-flights'),

    path('portal/', views.PortalRedirectView.as_view(), name='portal'),
    path('customer_portal/', views.CustomerPortalView.as_view(), name='customer-portal'),
    path('booking_agent_portal/', views.BookingAgentPortalView.as_view(), name='booking-agent-portal'),
    path('airline_staff_portal/', views.AirlineStaffPortalView.as_view(), name='airline-staff-portal'),

    path('purchase_ticket/<flight_pk>', views.PurchaseTicketRedirectView.as_view(), name='purchase-ticket'),
    path('customer_purchase_ticket/<flight_pk>/', views.CustomerPurchaseTicketView.as_view(), name='customer-purchase-ticket'),
    path('booking_agent_purchase_ticket/<flight_pk>/', views.BookingAgentPurchaseTicketView.as_view(), name='booking-agent-purchase-ticket'),

    path('customer_track_spending/', views.CustomerTrackSpendingView.as_view(), name='customer-track-spending'),

    path('booking_agent_view_commission/', views.BookingAgentViewCommissionView.as_view(), name='booking-agent-view-commission'),
    path('booking_agent_view_top_customers/', views.BookingAgentViewTopCustomersView.as_view(), name='booking-agent-view-top-customers'),

    path('airline_staff_create_flight/', views.AirlineStaffCreateFlightView.as_view(), name='airline-staff-create-flight'),
    path('airline_staff_change_flight_status/<int:flight_pk>', views.AirlineStaffChangeFlightStatusView.as_view(), name='airline-staff-change-flight-status'),
    path('airline_staff_view_flight_detail/<int:flight_pk>', views.AirlineStaffViewFlightDetailView.as_view(), name='airline-staff-view-flight-detail'),
    path('airline_staff_add_airplane/', views.AirlineStaffAddAirplaneView.as_view(), name='airline-staff-add-airplane'),
    path('airline_staff_view_airplanes/', views.AirlineStaffViewAirplanesView.as_view(), name='airline-staff-view-airplanes'),
    path('airline_staff_add_airport/', views.AirlineStaffAddAirportView.as_view(), name='airline-staff-add-airport'),
    path('airline_staff_view_booking_agents/', views.AirlineStaffViewBookingAgentsView.as_view(), name='airline-staff-view-booking-agents'),
    path('airline_staff_view_frequent_customers/', views.AirlineStaffViewFrequentCustomerView.as_view(), name='airline-staff-view-frequent-customers'),
    path('airline_staff_view_customer_detail/<int:customer_pk>', views.AirlineStaffViewCustomerDetailView.as_view(), name='airline-staff-view-customer-detail'),
    path('airline_staff_view_report/', views.AirlineStaffViewReportView.as_view(), name='airline-staff-view-report'),
    path('airline_staff_view_comparison/', views.AirlineStaffViewComparisonView.as_view(), name='airline-staff-view-comparison'),

]
