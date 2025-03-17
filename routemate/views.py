from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import OTPVerificationForm
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import random

from django.views import View
from django.contrib.auth.hashers import make_password
import random
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .forms import ForgotPasswordForm, ResetPasswordForm
from django.db import IntegrityError
from .models import ContactMessage, Vehicle, Booking, Payment, CustomUser, User
from .forms import (
    UserRegistrationForm,
    VehicleSearchForm,
    ReservationForm,
    PaymentForm,
    VehicleForm,
    BookingForm,
    ContactForm,
    UserProfileForm,
    Booking
)
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password


def home(request):
    """Render the home page."""
    return render(request, 'home.html', {'show_login': not request.user.is_authenticated})


def register(request):
    """Handle user registration."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Save the user instance
                user = form.save()
                
                # Save additional user details in CustomUser
                CustomUser.objects.create(
                    user=user,
                    phone=form.cleaned_data['phone'],
                    license_number=form.cleaned_data['license_number'],
                    profile_image=form.cleaned_data['profile_image'],
                    license_image=form.cleaned_data['license_image'],
                    address=form.cleaned_data['address']
                )
                
                # Log the user in after successful registration
                login(request, user)
                messages.success(request, 'Registration successful! Welcome to RouteMate.')
                return request('home')
            except IntegrityError:
                form.add_error(None, 'A user with this email or username already exists.')
    else:
        form = UserRegistrationForm()

    # Render the template with the form (including any errors if applicable)
    return render(request, 'register.html', {'form': form})


def login_view(request):
    """Handle user login with email and password."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid email or password.")
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
    return render(request, 'login.html')


# def gallery_view(request):
#     """Display a gallery of vehicles."""
#     vehicle_type = request.GET.get('vehicle_type')
#     vehicles = Vehicle.objects.filter(vehicle_type__iexact=vehicle_type) if vehicle_type else Vehicle.objects.all()
#     vehicle_types = Vehicle.objects.values_list('vehicle_type', flat=True).distinct()

#     context = {
#         'vehicles': vehicles,
#         'selected_type': vehicle_type.capitalize() if vehicle_type else None,
#         'vehicle_types': vehicle_types,
#     }
#     return render(request, 'gallery.html', context)

def gallery_view(request):
    """Display a gallery of vehicles with optional filtering and search."""
    vehicle_type = request.GET.get('vehicle_type')  # Vehicle type filter
    search_query = request.GET.get('search')       # Search term

    # Retrieve all vehicles
    vehicles = Vehicle.objects.all()

    # Filter by vehicle type
    if vehicle_type:
        vehicles = vehicles.filter(vehicle_type__iexact=vehicle_type)

    # Filter by search query
    if search_query:
        vehicles = vehicles.filter(name__icontains=search_query)

    # Get distinct vehicle types for filtering options
    vehicle_types = Vehicle.objects.values_list('vehicle_type', flat=True).distinct()

    context = {
        'vehicles': vehicles,
        'selected_type': vehicle_type.capitalize() if vehicle_type else None,
        'search_query': search_query,
        'vehicle_types': vehicle_types,
    }
    return render(request, 'gallery.html', context)


# def booking_history(request):
#     user_bookings = Booking.objects.filter(user=request.user.customuser)  # Adjust based on your model structure
#     return render(request, 'booking_history.html', {'bookings': user_bookings})
def booking_history(request):
    # Fetch bookings where status is not 'Cancelled'
    user_bookings = Booking.objects.filter(user=request.user.customuser).exclude(status='Cancelled').order_by('-booking_id')
    
    return render(request, 'booking_history.html', {'bookings': user_bookings})


@login_required
def bookings(request):
    """Render the user's bookings page."""
    user_bookings = Booking.objects.filter(user=request.user.customuser)  # Adjust based on your model structure
    return render(request, 'cart.html', {'bookings': user_bookings})  # Make sure you have a bookings.html template



# @login_required
# def cancel_booking(request, booking_id):
#     """Cancel a booking if it is more than 2 days before the start date."""
#     booking = get_object_or_404(Booking, id=booking_id, user=request.user.customuser)
#     start_date = booking.start_date  # Assuming you have a start_date field in your Booking model
#     days_before_start = (start_date - timezone.now()).days

#     if days_before_start > 2:
#         # Proceed with cancellation
#         booking.delete()
#         messages.success(request, 'Your booking has been cancelled.')
#     else:
#         messages.error(request, 'You can only cancel bookings more than 2 days before the start date.')

#     return redirect('bookings')  # Redirect back to bookings page
@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking if it is more than 2 days before the start date."""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user.customuser)
    start_date = booking.start_date  # Assuming you have a start_date field in your Booking model
    # days_before_start = (start_date - timezone.now()).days
    current_date = timezone.now().date()
    days_before_start = (start_date - current_date).days

    if days_before_start > 2:
        # Proceed with cancellation if more than 2 days before start date
        booking.status = 'Cancelled'  # Change booking status to 'Cancelled'

        payment = get_object_or_404(Payment, booking=booking)
        payment.status = 'Refunded'
       
        payment.save()
        booking.save()

        messages.success(request, 'Your booking has been cancelled successfully.')

    else:
        # Apply cancellation fee and refund 50% if within 2 days of the booking start date
        cancellation_fee = (booking.total_amount / 2)  # 50% cancellation fee
        refund_amount = booking.total_amount - cancellation_fee
        
        # Update the payment status as 'Refunded' and store the refund amount
        booking.status = 'Cancelled'
        payment = get_object_or_404(Payment, booking=booking)
        payment.status = 'Refunded'
       
        payment.save()
        booking.save()

        messages.success(request, f'Your booking has been cancelled. You will receive a refund of ${refund_amount}.')

    return redirect('booking_history')  # Redirect back to bookings page


@login_required
def reservation(request, vehicle_id=None):
    """Handle vehicle reservation."""
    if not vehicle_id:
        return redirect('gallery')

    vehicle = get_object_or_404(Vehicle, vehicle_id=vehicle_id)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            # Check for existing reservations within the requested date range
            overlapping_reservations = Booking.objects.filter(
                vehicle=vehicle,
                end_date__gte=start_date,
                start_date__lte=end_date,
                status__in=['Pending', 'Confirmed']  # Check only relevant statuses
            )

            if overlapping_reservations.exists():
                messages.error(request, f'This vehicle is already booked from {start_date} to {end_date}.')
                return render(request, 'reservation.html', {'form': form, 'vehicle': vehicle})

            day_difference = (end_date - start_date).days + 1
            total_amount = vehicle.price * day_difference
            additional_costs = 0

            if 'offer1' in request.POST:
                additional_costs += 1000
            if 'offer3' in request.POST:
                additional_costs += 500
            if 'offer4' in request.POST:
                additional_costs += 1000
            if 'offer5' in request.POST:
                additional_costs += 100 * day_difference
            if 'offer6' in request.POST:
                additional_costs += 100

            total_amount += additional_costs

            booking = form.save(commit=False)
            booking.user = request.user.customuser
            booking.vehicle = vehicle
            booking.total_amount = total_amount
            booking.booking_date = timezone.now()
            booking.status = 'Pending'

            booking.save()
            messages.success(request, 'Booking successful!')
            return redirect('payment', booking_id=booking.booking_id)

    else:
        form = ReservationForm()

    return render(request, 'reservation.html', {'form': form, 'vehicle': vehicle})


# @login_required
# def payment(request, booking_id):
#     """Handle payment for a booking."""
#     print(f"Requested booking ID: {booking_id}")  # Debugging line

#     # Ensure that you are getting the booking correctly
#     booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user.customuser)
#     print(f"Retrieved booking: {booking}")  # Debugging line

#     if request.method == 'POST':
#         form = PaymentForm(request.POST)
#         if form.is_valid():
#             payment = form.save(commit=False)
#             payment.booking = booking
#             payment.amount = booking.total_amount
#             payment.user = request.user  # Assign the User instance directly
#             payment.save()
#             booking.is_paid = True
#             booking.save()
#             messages.success(request, 'Payment successful.')
#             return redirect('home')
#     else:
#         form = PaymentForm(initial={'amount': booking.total_amount})

#     return render(request, 'payment.html', {'form': form, 'booking': booking})
@login_required
def payment(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user.customuser)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.amount = booking.total_amount
            payment.user = request.user
            payment.status ='Paid'
            payment.save()
            booking.is_paid = True
            booking.save()
            messages.success(request, 'Payment successful.')

            # After successful payment, redirect to generate the PDF receipt
            return redirect('generate_payment_receipt', booking_id=booking.booking_id)
    else:
        form = PaymentForm(initial={'amount': booking.total_amount})

    return render(request, 'payment.html', {'form': form, 'booking': booking})

def generate_payment_receipt(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user.customuser)

    # Create a BytesIO buffer to hold the PDF data
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Title of the receipt
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 750, "Payment Receipt for Booking")

    # Line separator
    c.setStrokeColor(colors.grey)
    c.setLineWidth(0.5)
    c.line(100, 745, 500, 745)  # Horizontal line

    # Booking details
    c.setFont("Helvetica", 12)
    y_position = 725
    c.drawString(100, y_position, f"Booking ID: {booking.booking_id}")
    y_position -= 20
    c.drawString(100, y_position, f"User: {booking.user.user}")
    y_position -= 20
    c.drawString(100, y_position, f"Amount Paid: ${booking.total_amount}")
    y_position -= 20
    c.drawString(100, y_position, f"Payment Method: {booking.payment.payment_method}")
    y_position -= 20
    c.drawString(100, y_position, f"Booking Date: {booking.start_date.strftime('%Y-%m-%d %H:%M:%S')}")

    # Line separator
    y_position -= 30
    c.line(100, y_position, 500, y_position)

    # Footer
    y_position -= 40
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.grey)
    c.drawString(100, y_position, "Thank you for booking with RouteMate!")
    y_position -= 20
    c.drawString(100, y_position, "For any inquiries, contact support@routemate.com")

    # Save the PDF to the buffer
    c.showPage()
    c.save()

    # Return the buffer content as an HttpResponse
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="payment_receipt_{booking.booking_id}.pdf"'

    return response
@login_required
def add_vehicle(request):
    """Allow staff to add a new vehicle."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to add vehicles.')
        return redirect('home')

    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle added successfully.')
            return redirect('gallery')
    else:
        form = VehicleForm()

    return render(request, 'add_vehicle.html', {'form': form})


def search_vehicle(request):
    """Search for vehicles by name."""
    form = VehicleSearchForm(request.GET or None)
    vehicles = Vehicle.objects.filter(name__icontains=form.cleaned_data['name']) if form.is_valid() else None
    return render(request, 'search_results.html', {'vehicles': vehicles, 'form': form})


def calculate_total_amount(booking):
    """Calculate the total amount for a booking."""
    base_price = booking.vehicle.price_per_day * (booking.end_date - booking.start_date).days
    return base_price


def cars(request):
    """Display a list of all vehicles."""
    vehicles = Vehicle.objects.all()
    return render(request, 'gallery.html', {'vehicles': vehicles})


def about(request):
    """Render the about page."""
    return render(request, 'about.html')


@login_required
def logout_view(request):
    """Log out the user."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

def reserve_vehicle(request, vehicle_id):
    # Get the vehicle and user objects
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    user = request.user  # Assumes user is logged in

    if request.method == 'POST':
        # Process the booking form submission
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = user
            booking.vehicle = vehicle
            booking.amount = vehicle.price  # Assuming 'price' field in Vehicle
            booking.status = 'Pending'
            booking.date = timezone.now()
            booking.save()

            # Redirect to the payment page with relevant details
            return redirect('payment_page', booking_id=booking.id, user_id=user.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingForm()

    return render(request, 'reserve_vehicle.html', {
        'vehicle': vehicle,
        'form': form
    })
    
    
    
@login_required
def edit_vehicle(request, vehicle_id):
    # Implement your vehicle editing logic here
    pass

@login_required
def delete_vehicle(request, vehicle_id):
    """Delete a vehicle from the database."""
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    vehicle.delete()
    messages.success(request, 'Vehicle deleted successfully.')
    return redirect('gallery')

from django.shortcuts import render

def contact_view(request):
    """Render the contact page."""
    return render(request, 'contact.html')  # Make sure you have a contact.html template

@login_required
def profile(request):
    """Render the user profile page and handle updates."""
    user = request.user.customuser  # Get the custom user instance

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'profile.html', {'user': user, 'form': form})



@csrf_exempt  # Use this if CSRF token is not being sent correctly (not recommended for production)
def verify_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        license_number = request.POST.get('license_number')
        
        try:
            # Check if the user exists with the provided email in the User model
            user = User.objects.get(email=email)
            # Now check if the corresponding CustomUser  exists with the provided license number
            custom_user = CustomUser .objects.get(user=user, license_number=license_number)
            return JsonResponse({'valid': True})  # User found
        except User.DoesNotExist:
            return JsonResponse({'valid': False})  # User not found
        except CustomUser .DoesNotExist:
            return JsonResponse({'valid': False})  # CustomUser  not found

    return JsonResponse({'valid': False})  # In case of a GET request or other methods



@login_required
def bookings(request):
    """Render the user's bookings page."""
    user_bookings = Booking.objects.filter(user=request.user.customuser)  # Adjust based on your model structure
    return render(request, 'bookings.html', {'bookings': user_bookings})  # Make sure you have a bookings.html template

@login_required
def bookings(request):
    """Render the user's bookings page."""
    user_bookings = Booking.objects.filter(user=request.user.customuser)  # Adjust based on your model structure
    return render(request, 'bookings.html', {'bookings': user_bookings})

def submit_contact_form(request):
    """Handle the submission of the contact form."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Save the data to the database
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')  # Redirect to the contact page
        else:
            messages.error(request, 'There was an error in your submission. Please try again.')
    else:
        form = ContactForm()  # Empty form for GET request

    return render(request, 'contact.html', {'form': form})

@login_required
def edit_account(request):
    """Handle editing user account information."""
    user = request.user.customuser  # Get the custom user instance

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'edit_account.html', {'form': form})  # Make sure you have an edit_account.html template

def profile_view(request):
    try:
        custom_user = CustomUser.objects.get(user=request.user)
    except CustomUser.DoesNotExist:
        custom_user = None  # Or handle appropriately (e.g., create the profile or show an error)

    return render(request, 'profile.html', {'user': custom_user})






class VerifyEmailView(View):
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            return JsonResponse({'valid': True})
        except User.DoesNotExist:
            return JsonResponse({'valid': False})



from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ForgotPasswordForm
from django.conf import settings
from django.contrib.auth.models import User
import random

# Store OTPs temporarily
otp_store = {}

# Generate a 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if not User.objects.filter(email=email).exists():  # Check if email is not registered
                form.add_error('email', 'The email address is not registered.')
            else:
                # Proceed to send OTP
                otp = generate_otp()
                otp_store[email] = otp
                send_mail(
                    'Your OTP for Password Reset',
                    f'Your OTP is {otp}. Do not share it with anyone.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                )
                request.session['email'] = email  # Store email in session for OTP verification
                return redirect('verify_otp')  # Redirect to OTP verification page
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import OTPVerificationForm

# Check if OTP is valid for the stored email and redirect to password reset
def verify_otp(request):
    email = request.session.get('email')
    
    if not email:
        # If the email is not found in session, redirect to forgot password page
        return redirect('forgot_password')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        
        if form.is_valid():
            otp = form.cleaned_data['otp']
            
            # Check if OTP is valid for the stored email
            if otp_store.get(email) == otp:
                # OTP is valid, clear it from storage
                otp_store.pop(email, None)
                
                # Save email in session for password reset
                request.session['verified_email'] = email
                
                # Redirect to the password reset page
                return redirect('reset_password')
            else:
                # Invalid OTP, add error to form
                form.add_error('otp', 'Invalid OTP. Please try again.')
    else:
        form = OTPVerificationForm()

    return render(request, 'verify_otp.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import ResetPasswordForm

def reset_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        email = request.session.get('verified_email')  # Retrieve the email from the session
        
        # Debugging: print email value before checking
        print(f"Session Email: {email}")

        if not email:
            messages.error(request, 'Session expired. Please restart the password reset process.')
            return redirect('forgot_password')  # Redirect to the forgot password page

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            # Clear the session after resetting the password
            request.session.pop('verified_email', None)

            # Debugging: print session value after clearing
            print(f"Session after password reset: {request.session.get('verified_email')}")

            messages.success(request, 'Password reset successfully. Please log in.')
            return redirect('login')  # Ensure 'login' is the correct name for your login URL
        except User.DoesNotExist:
            messages.error(request, 'User does not exist.')

    return render(request, 'reset_password.html')



#ADMIN DETAILS >>>>

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Vehicle


def admin_home(request):
    cars = Vehicle.objects.all()
    return render(request, 'admin/admin_home.html',{'cars': cars})


from .models import Booking


def booking_list(request):
    bookings = Booking.objects.select_related('user', 'vehicle').all().order_by('-booking_id')
    return render(request, 'admin/booking_list.html', {'bookings': bookings})




def payment_list(request):
    payments = Payment.objects.select_related('user', 'booking').all()
    return render(request, 'admin/payment_list.html', {'payments': payments})


def message_list(request):
    messages = ContactMessage.objects.all().order_by('-submitted_at')
    return render(request, 'admin/message_list.html', {'messages': messages})

def add_car(request):
    """Handle adding a new car."""
    if request.method == 'POST':
        name = request.POST.get('name')
        brand = request.POST.get('brand')
        model = request.POST.get('model')
        vehicle_type = request.POST.get('vehicle_type')
        price = request.POST.get('price')
        capacity = request.POST.get('capacity')
        description = request.POST.get('description')
        is_available = request.POST.get('is_available') == 'on'

        # Handling file uploads for images
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')

        # Creating a new Vehicle object with the provided data
        Vehicle.objects.create(
            name=name,
            brand=brand,
            model=model,
            vehicle_type=vehicle_type,
            price=price,
            capacity=capacity,
            description=description,
            is_available=is_available,
            image1=image1,  # Saving the uploaded images
            image2=image2,
            image3=image3
        )
        messages.success(request, "Car added successfully.")
        return redirect('car_list')

    # Pass VEHICLE_TYPES to the template
    vehicle_types = Vehicle.VEHICLE_TYPES
    return render(request, 'admin/add_car.html', {'vehicle_types': vehicle_types})


def car_list(request):
    """Display the list of cars."""
    cars = Vehicle.objects.all()
    return render(request, 'admin/car_list.html', {'cars': cars})

def edit_car(request, vehicle_id):
    """Edit an existing car."""
    car = get_object_or_404(Vehicle, pk=vehicle_id)

    if request.method == 'POST':
        car.name = request.POST.get('name')
        car.brand = request.POST.get('brand')
        car.model = request.POST.get('model')
        car.vehicle_type = request.POST.get('vehicle_type')
        car.price = request.POST.get('price')
        car.capacity = request.POST.get('capacity')
        car.description = request.POST.get('description')
        car.is_available = request.POST.get('is_available') == 'on'
        car.save()

        messages.success(request, "Car updated successfully.")
        return redirect('car_list')

    return render(request, 'admin/edit_car.html', {'car': car})

def delete_car(request, vehicle_id):
    """Delete a car."""
    car = get_object_or_404(Vehicle, pk=vehicle_id)
    car.delete()
    messages.success(request, "Car deleted successfully.")
    return redirect('car_list')


def admin_login(request):
    """Handle the admin login."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if email and password match the admin credentials
        if email == 'admin@gmail.com' and password == 'admin':
            # Redirect to the admin login page on success
            return redirect('admin_home')
        else:
            # Display error message if credentials are incorrect
            messages.error(request, "Invalid email or password")
            return redirect('admin_login')  # Redirect back to the login page

    return render(request, 'admin/admin_login.html')


