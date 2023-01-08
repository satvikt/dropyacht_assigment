from rest_framework import serializers
from dropyacht_app.models import *

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"

    # def create_or_update(sel`f, instance):

class ScreenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screen
        fields = "__all__"


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"


class ShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Show
        fields = "__all__"