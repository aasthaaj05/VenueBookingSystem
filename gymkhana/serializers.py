from rest_framework import serializers
from .models import Venue ,  Request, Booking, Rejection
from .models import RejectedBooking


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ['venue_name', 'description', 'photo_url', 'capacity', 'address', 'facilities', 'department_incharge']



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


class RejectedBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RejectedBooking
        fields = '__all__'



