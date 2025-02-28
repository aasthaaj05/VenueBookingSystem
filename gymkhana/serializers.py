from rest_framework import serializers
from .models import Venue

class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ['venue_name', 'description', 'photo_url', 'capacity', 'address', 'facilities', 'department_incharge']


from rest_framework import serializers
from .models import Request, Booking, Rejection

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

    def create(self, validated_data):
        return Booking.objects.create(**validated_data)

class RejectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rejection
        fields = '__all__'


from rest_framework import serializers
from .models import RejectedBooking

class RejectedBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RejectedBooking
        fields = '__all__'



