from django.http import JsonResponse
from rest_framework.generics import *

from dropyacht_app.functions import *


# Create your views here.
class CreateMovieView(CreateAPIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        result = create_movie(
            name=data.get("movie").get("name"),
            description=data.get("movie").get("description"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            screen_id=data.get("screen_id")
        )

        return JsonResponse(data=result[0], status=result[1])

class BookShowView(CreateAPIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        result, status = book_seat(
            movie_name=data.get("movie_name"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            screen_id=data.get("screen_id"),
            start_seat_number=data.get("start_seat_number"),
            end_seat_number=data.get("end_seat_number"),
            user_email=data.get("user_email")
        )

        return JsonResponse(data=result, status=status)


class GetAvailableSeatsView(RetrieveAPIView):
    def get(self, request, *arg, **kwargs):
        data = request.data
        result, status = get_available_seats(
            movie_name=data.get("movie_name"),
            screen_id=data.get("screen_id"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time")
        )

        return JsonResponse(data=result, status=status)


class GetUserForSeatView(RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        data = request.data
        result, status = get_user_for_seat(
            movie_name=data.get("movie_name"),
            screen_id=data.get("screen_id"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            seat_id=data.get("seat_id")
        )

        return JsonResponse(data=result, status=status)


class ListMoviesView(ListAPIView):
    def get(self, request, *args, **kwargs):
        result, status = list_movies(kwargs.get("date"))
        return JsonResponse(data=result, status=status)
