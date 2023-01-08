from datetime import datetime
import datetime as datetime_lib

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from rest_framework import status

from .serializers import *
from dropyacht_app.models import *


def create_seat_matrix():
    matrix = []
    for i in range(96):
        matrix.append(
            {
                "id": i,
                "status": "Available"
            }
        )
    return matrix


def create_movie(name, description, start_time, end_time, screen_id):
    movie_data = {
        "name": name,
        "description": description
    }

    movie_serializer = MovieSerializer(data=movie_data)
    if not movie_serializer.is_valid():
        return movie_serializer.errors, status.HTTP_400_BAD_REQUEST
    with transaction.atomic():
        movie, created = Movie.objects.get_or_create(pk=None, defaults=movie_serializer.validated_data)

        screen, created = Screen.objects.get_or_create(id=screen_id)
        start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

        show_data = {
            "movie": movie.id,
            "screen": screen.id,
            "start_time": start_time,
            "end_time": end_time,
            "seats": create_seat_matrix()
        }

        show_serializer = ShowSerializer(data=show_data)

        if not show_serializer.is_valid():
            return show_serializer.errors, status.HTTP_400_BAD_REQUEST
        show_serializer.save()
        show = show_serializer.data

        return {
            "movie_details": movie.name,
            "show_timings": {
                "start_time": show["start_time"],
                "end_time": show["end_time"]
            },
            "screen": show["screen"]
        }, status.HTTP_201_CREATED


def list_movies(date):
    date = datetime.strptime(date, '%Y-%m-%d')
    shows = Show.objects.filter(end_time__date=datetime_lib.date(date.year, date.month, date.day))

    date_shows = []
    if len(shows) == 0:
        return {
            "status": "error",
            "message": "no movie shows found matching given input"
        },status.HTTP_400_BAD_REQUEST

    for show in shows:
         show = dict(
             movie_name=show.movie.name,
             start_time=show.start_time,
             end_time=show.end_time,
             screen=show.screen.id
         )
         date_shows.append(show)

    return {
        "status": "success",
        "message": date_shows
    }, status.HTTP_200_OK


def book_seat(movie_name, start_time, end_time, screen_id, start_seat_number, end_seat_number, user_email):
    movie = Movie.objects.filter(name=movie_name)
    screen = Screen.objects.get(id=screen_id)
    start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if len(movie) == 0:
        return {"status": "error", "message": "invalid movie details provided, please try again"}, status.HTTP_400_BAD_REQUEST
    show = Show.objects.filter(movie=movie[0], start_time=start_time, end_time=end_time, screen=screen)[0]
    seats = show.seats
    available_seats = list(filter(lambda x: x["status"] == "Available", seats))
    available_indices = set(map(lambda x: x["id"], available_seats))
    desired_seat_range = range(start_seat_number, end_seat_number+1)
    if not set(desired_seat_range).issubset(available_indices):
        return {"status": "error", "message": "desired seat(s) unavailable. Please try with different seat(s)"}, status.HTTP_400_BAD_REQUEST

    try:
        with transaction.atomic():
            for seat in seats:
                if seat["id"] in desired_seat_range and seat["status"] != "Booked":
                    # seats.remove(seat)
                    seats.append({
                        "id": seat["id"],
                        "status": "Booked"
                    })

                    booking_data = {
                        "show": show.id,
                        "user_email": user_email,
                        "seat_id": seat["id"]
                    }
                    booking_serializer = BookingSerializer(data=booking_data)
                    if booking_serializer.is_valid(raise_exception=True):
                        booking_serializer.save()

            for seat in desired_seat_range:
                matching_seats = list(filter(lambda x: x["id"] == seat, seats))
                seat_to_delete = list(filter(lambda x: x["status"] == "Available", matching_seats))[0]
                seats.remove(seat_to_delete)
            show.seats = seats
            show.save()


        return {
            "status": "success",
            "message": f"seats {list(desired_seat_range)} are successfully booked!"
        }, status.HTTP_200_OK

    except Exception:
        return {"status": "error", "message": "An unexpected error occurred, please try again later"}, status.HTTP_400_BAD_REQUEST


def get_available_seats(movie_name, start_time, end_time, screen_id):
    movie = Movie.objects.filter(name=movie_name)
    screen = Screen.objects.get(id=screen_id)
    start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if len(movie) == 0:
        return {"status": "error", "message": "invalid movie details provided, please try again"}, status.HTTP_400_BAD_REQUEST
    show = Show.objects.filter(movie=movie[0], start_time=start_time, end_time=end_time, screen=screen)[0]

    if not show:
        return {"status":"error", "message": "No movies matching the given input"}, status.HTTP_400_BAD_REQUEST

    available_seats = list(filter(lambda x: x["status"] == "Available", show.seats))
    available_indices = list(map(lambda x: x["id"], available_seats))

    return {
        "status": "success",
        "message": f"following seat numbers are available to book",
        "data": available_indices
    }, status.HTTP_200_OK


def get_user_for_seat(movie_name, start_time, end_time, screen_id, seat_id):
    try:
        movie = Movie.objects.filter(name=movie_name)
        screen = Screen.objects.get(id=screen_id)
        start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        if len(movie) == 0:
            return {"status": "error",
                    "message": "invalid movie details provided, please try again"}, status.HTTP_400_BAD_REQUEST
        show = Show.objects.filter(movie=movie[0], start_time=start_time, end_time=end_time, screen=screen)[0]

        booking = Booking.objects.get(show=show.id,seat_id=seat_id)

        return {
            "status": "success",
            "message": f"this booking is made by {booking.user_email}"
        }, status.HTTP_200_OK

    except ObjectDoesNotExist:
        return {
            "status": "error",
            "message": "no booking exists for given input"
        }, status.HTTP_400_BAD_REQUEST
