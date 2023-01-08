from django.db import models
from django.contrib.postgres.fields import *

# Create your models here.

class Movie(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

#
# class User(models.Model):
#     name = models.CharField(max_length=200)
#     email = models.EmailField()


class Screen(models.Model):
    pass

class Show(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="shows")
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name="shows")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    seats = ArrayField(models.JSONField(), size=96, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("movie", "screen", "end_time")



class Booking(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name="bookings")
    user_email = models.EmailField()
    seat_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

