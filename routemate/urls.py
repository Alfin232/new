from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('register/', views.register, name='register'),  # User registration
    path('login/', views.login_view, name='login'),  # User login
    path('logout/', views.logout_view, name='logout'),  # User logout
    path('gallery/', views.gallery_view, name='gallery'),  # Gallery of vehicles
    path('reservation/', views.reservation, name='reservation'),
    path('booking_history/', views.booking_history, name='booking_history'),
    path('reservation/<int:vehicle_id>/', views.reservation, name='reservation_with_id'),  # Reservation for specific vehicle
    path('reserve/', views.reserve_vehicle, name='reserve_vehicle'),  # Add this line for reserving a vehicle
    path('payment/<int:booking_id>/', views.payment, name='payment'),  # Payment page
    path('add_vehicle/', views.add_vehicle, name='add_vehicle'),  # Add a new vehicle
    path('edit_vehicle/<int:vehicle_id>/', views.edit_vehicle, name='edit_vehicle'),  # Edit vehicle details
    path('delete_vehicle/<int:vehicle_id>/', views.delete_vehicle, name='delete_vehicle'),  # Delete a vehicle
    path('search/', views.search_vehicle, name='search_vehicle'),  # Search for vehicles
    path('about/', views.about, name='about'),  # About page
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_user/', views.verify_user, name='verify_user'),
    path('contact/', views.contact_view, name='contact'),  # Contact page
    path('profile/', views.profile, name='profile'),  # User profile page
    path('bookings/', views.bookings, name='bookings'),  # User's bookings
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),  # Cancel booking
    path('submit-contact-form/', views.submit_contact_form, name='submit_contact_form'),
    path('edit_account/', views.edit_account, name='edit_account'),  # Edit account information
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('payment-receipt/<int:booking_id>/', views.generate_payment_receipt, name='generate_payment_receipt'),
    

    #ADMIN

    path('admin_home/', views.admin_home, name='admin_home'),
    path('booking_list/', views.booking_list, name='booking_list'),
    path('payment_list/', views.payment_list, name='payment_list'),
    path('message_list/', views.message_list, name='message_list'),
    path('add-car/', views.add_car, name='add_car'),
    path('car-list/', views.car_list, name='car_list'),
    path('edit-car/<int:vehicle_id>/', views.edit_car, name='edit_car'),
    path('delete-car/<int:vehicle_id>/', views.delete_car, name='delete_car'),
    path('admin_login/', views.admin_login, name='admin_login'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)