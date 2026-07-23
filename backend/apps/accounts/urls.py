from django.urls import path , re_path
from .views import CustomUserRegisterView


urlpatterns = [
    re_path(r"^register/$", CustomUserRegisterView.as_view(), name="register"),
]