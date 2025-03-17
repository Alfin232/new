from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import ContactMessage, Vehicle, Booking, Payment, CustomUser
from django.db import models
from django.core.exceptions import ValidationError

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit phone number')]
    )
    license_number = forms.CharField(
        max_length=15,
        validators=[RegexValidator(r'^[A-Z]{2}\d{13}$', 'Enter a valid license format (e.g., KL0000000000000)')]
    )
    profile_image = forms.ImageField(required=True)
    license_image = forms.ImageField(required=True)
    address = forms.CharField(max_length=255, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone', 
                 'license_number', 'profile_image', 'license_image', 'address']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if ' ' in username:
            raise ValidationError("Username cannot contain spaces.")
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if CustomUser.objects.filter(phone=phone).exists():
            raise forms.ValidationError('This phone number is already registered.')
        return phone

    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        if CustomUser.objects.filter(license_number=license_number).exists():
            raise forms.ValidationError('This license number is already registered.')
        return license_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            CustomUser .objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                license_number=self.cleaned_data['license_number'],
                profile_image=self.cleaned_data['profile_image'],
                license_image=self.cleaned_data['license_image'],
                address=self.cleaned_data['address']
            )
        return user

class VehicleSearchForm(forms.Form):
    vehicle_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Vehicle.VEHICLE_TYPES,
        required=False
    )
    min_price = forms.DecimalField(required=False)
    max_price = forms.DecimalField(required=False)
    capacity = forms.IntegerField(required=False)
    brand = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')

        if min_price and max_price and min_price > max_price:
            raise forms.ValidationError("Minimum price should not be greater than maximum price")
        return cleaned_data

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['name', 'brand', 'model', 'vehicle_type', 'price', 
                 'capacity', 'image1', 'image2', 'image3', 'description']
        
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero")
        return price

    def clean_capacity(self):
        capacity = self.cleaned_data.get('capacity')
        if capacity <= 0:
            raise forms.ValidationError("Capacity must be greater than zero")
        return capacity

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_date', 'end_date', 'start_time', 'end_time', 'starting_location', 'ending_location']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date.")
        return cleaned_data

class PaymentForm(forms.ModelForm):
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking'),
    ]

    payment_method = forms.ChoiceField(choices=PAYMENT_METHODS, required=True)

    class Meta:
        model = Payment
        fields = ['amount', 'payment_method']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero")
        return amount
    
    
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message'}),
        }
    
    
class UserProfileForm(forms.ModelForm): 
    class Meta:
        model = CustomUser    
        fields = ['phone', 'license_number', 'address', 'profile_image']  # Add any other fields you want to edit
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your license number'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your address'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError("Enter a valid 10-digit phone number.")
        return phone

    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        if not license_number.isalnum():
            raise forms.ValidationError("License number must be alphanumeric.")
        return license_number

    


class BookingForm(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    pickup_location = models.CharField(max_length=255)  # Ensure this field exists
    return_location = models.CharField(max_length=255)  # Ensure this field exists
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)
    

from django import forms

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your registered email'
    }))


from django import forms

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter the OTP sent to your email'
    }))


from django import forms

class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your new password'
    }))
