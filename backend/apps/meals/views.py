from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MealLog
from .serializers import MealLogSerializer
from rest_framework.permissions import IsAuthenticated
from .meal_analysis_service import analyze_meal_image


class MealLogListCreateView(APIView):
    """
    Meal log of current user.
    GET : Fetch the data of current user.
    POST : Create the data of the current user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        meal_logs = MealLog.objects.filter(user=request.user)  # data of particular user
        serializer = MealLogSerializer(meal_logs, many=True)
        return Response(
            {
                "status": True,
                "message": "Meal logs fetched successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = MealLogSerializer(data=request.data)
        if serializer.is_valid():
            meal = serializer.save(user=request.user)
            analysis = None
            if meal.image:
                analysis = analyze_meal_image(meal)
            return Response(
                {
                    "status": True,
                    "message": "Meal log created successfully",
                    "data": serializer.data,
                    "analysis": analysis,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "status": False,
                "message": "Failed to create meal log",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class MealLogDetailView(APIView):
    """
    Meal log of current user.
    GET : Fetch the data of current user.
    PATCH : Update the data of the current user.
    DELETE : Delete the data of the current user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, meal_id):
        try:
            meal_log = MealLog.objects.get(id=meal_id, user=request.user)
        except MealLog.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Meal log not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = MealLogSerializer(meal_log)
        return Response(
            {
                "status": True,
                "message": "Meal log fetched successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, meal_id):
        try:
            meal_log = MealLog.objects.get(id=meal_id, user=request.user)
        except MealLog.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Meal log not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = MealLogSerializer(meal_log, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Meal log updated successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": False,
                "message": "Failed to update meal log",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, meal_id):
        try:
            meal_log = MealLog.objects.get(id=meal_id, user=request.user)
        except MealLog.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Meal log not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        meal_log.delete()
        return Response(
            {
                "status": True,
                "message": "Meal log deleted successfully",
            },
            status=status.HTTP_200_OK,
        )
