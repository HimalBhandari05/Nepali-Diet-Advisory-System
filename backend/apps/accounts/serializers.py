from rest_framework.serializers import ModelSerializer
from .models import CustomUser


class UserSerializer(ModelSerializer):
    """
    It is read only serializer for CustomUser model.
    It is used to serialize the user data when we want to send it in response.
    """

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
            "date_joined",
            "created_at",
            "updated_at",
        ]


class UserRegisterSerializer(ModelSerializer):
    """
    It is write only serializer for CustomUser model.
    It is used to deserialize the user data when we want to create a new user.
    """

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        """
        Create and return a new `CustomUser` instance, given the validated data without the password.
        """
        password = validated_data.pop("password", None)
        # user = CustomUser(**validated_data)
        # if password is not None:
        #     user.set_password(password)
        # user.save()

        user = CustomUser.objects.create_user(**validated_data, password=password)
        return user
