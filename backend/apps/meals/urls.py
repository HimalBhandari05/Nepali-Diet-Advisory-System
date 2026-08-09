from django.urls import path
from .views import MealLogListCreateView, MealLogDetailView

urlpatterns = [
    path("", MealLogListCreateView.as_view(), name="meal-list-create"),
    path("<int:meal_id>/", MealLogDetailView.as_view(), name="meal-detail"),
]
