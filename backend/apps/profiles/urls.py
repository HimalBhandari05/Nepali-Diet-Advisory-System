from django.urls import path
from .views import (
    AllergyListView,
    DietaryRestrictionListView,
    MedicalConditionListView,
    UserProfileAPIView,
)

urlpatterns = [
    path("user-profile/", UserProfileAPIView.as_view(), name="user-profile"),
    path(
        "medical-conditions/",
        MedicalConditionListView.as_view(),
        name="medical-conditions",
    ),
    path("allergies/", AllergyListView.as_view(), name="allergies"),
    path(
        "dietary-restrictions/",
        DietaryRestrictionListView.as_view(),
        name="dietary-restrictions",
    ),
]