from django.urls import include, path
from .views import UserProfileAPIView

urlpatterns = [
    path("user-profile/", UserProfileAPIView.as_view(), name="user-profile"),
]