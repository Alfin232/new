from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class CustomUser (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)
    license_number = models.CharField(max_length=15)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    license_image = models.ImageField(upload_to='license_images/', null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('sedan', 'Sedan'),
        ('sports', 'Sports'),
        ('luxury', 'Luxury'),
        ('suv', 'SUV'),
        ('pickup', 'Pickup Truck'),
        ('hatchback', 'Hatchback'),
        ('4x4', '4x4'),
    ]

    vehicle_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField()
    image1 = models.ImageField(upload_to='vehicle_images/')
    image2 = models.ImageField(upload_to='vehicle_images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='vehicle_images/', blank=True, null=True)
    description = models.TextField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.brand} {self.model}"

    def check_availability(self, start_date, end_date):
        # from .models import Booking  # Import Booking here to avoid circular import
        existing_bookings = Booking.objects.filter(
            vehicle=self,
            start_date__lte=end_date,
            end_date__gte=start_date,
            status='confirmed'
        )
        return not existing_bookings.exists()

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed')
    ]

    booking_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser , on_delete=models.CASCADE)  # Link to CustomUser  
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE)  # Use string reference
    booking_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    start_time = models.TimeField()
    end_date = models.DateField()
    end_time = models.TimeField()
    starting_location = models.CharField(max_length=255, default='Default Starting Location')
    ending_location = models.CharField(max_length=255, default='Default Location')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking {self.booking_id} - {self.user.user.username}"

    def calculate_total_amount(self):
        try:
            start = datetime.combine(self.start_date, self.start_time)
            end = datetime.combine(self.end_date, self.end_time)
            if start >= end:
                raise ValueError("End date/time must be after start date/time.")
            
            duration = end - start
            days = max(duration.days + 1, 1)  # Ensure at least 1 day is charged
            
            if not hasattr(self.vehicle, 'price'):
                raise ValueError("Vehicle price is not set.")
            
            self.total_amount = self.vehicle.price * days
            self.save()
            return self.total_amount
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"Error calculating total amount: {e}")
            return 0


class Payment(models.Model):
    PAYMENT_STATUS = [
        ('not_paid', 'Not Paid'),
        ('processing', 'Processing'),
        ('paid', 'Paid'),
        ('failed', 'Failed')
    ]

    payment_id = models.AutoField(primary_key=True)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='not_paid')
    date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Payment {self.payment_id} for Booking {self.booking.booking_id}"
    

class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.email}"