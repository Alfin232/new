from django.contrib import admin
from .models import ContactMessage, CustomUser, Vehicle, Booking, Payment

class VehicleAdmin(admin.ModelAdmin):
    list_display = ('vehicle_id', 'name', 'brand', 'model', 'vehicle_type', 'price', 'capacity', 'is_available')
    list_filter = ('vehicle_type', 'brand', 'is_available')
    search_fields = ('name', 'brand', 'model')
    list_editable = ('price', 'is_available')

class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'vehicle', 'start_date', 'end_date', 'status', 'total_amount')
    list_filter = ('status', 'start_date','end_date')
    search_fields = ('user__username', 'vehicle__name','status')

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'booking', 'user', 'amount', 'status', 'date')
    list_filter = ('status', 'date')
    search_fields = ('user__username', 'booking__booking_id')

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'license_number', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('user__username', 'phone', 'license_number')

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'submitted_at')
    search_fields = ('name', 'email', 'message')
    list_filter = ('submitted_at',)


# Register your models
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)