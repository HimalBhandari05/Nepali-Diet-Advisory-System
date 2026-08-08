from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import UserProfile
from .serializers import UserProfileSerializer


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        if UserProfile.objects.filter(user=request.user).exists():
            return Response(
                {"status": False, "message": "User profile already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = UserProfileSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user) # save to db 

            return Response(
                {
                    "status": True,
                    "message": "User profile created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "status": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response(
                {"status": False, "message": "User profile does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserProfileSerializer(profile)

        return Response(
            {
                "status": True,
                "message": "User profile retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response(
                {"status": False, "message": "User profile does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "status": True,
                    "message": "User profile updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
