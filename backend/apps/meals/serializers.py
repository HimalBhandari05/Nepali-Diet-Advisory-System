from rest_framework import serializers

from .models import MealLog, TotalFoodAnalysis, MealFoodItems


class MealLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealLog
        fields = "__all__"
        read_only_fields = ["user", "id", "created_at", "updated_at"]


class TotalFoodAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = TotalFoodAnalysis
        fields = "__all__"
        read_only_fields = ["meal", "id", "created_at", "updated_at"]


class MealFoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealFoodItems
        fields = "__all__"
        read_only_fields = ["food_analysis", "id", "created_at", "updated_at"]
