from typing import Dict, Any
from rest_framework import serializers
from my_site_api.models import Note
from django.contrib.auth.models import User


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "title", "description", "time_create"]

    def create(self, validated_data: Dict[str, Any]) -> Note:
        # извлекаем данные,которые могут быть не нужны
        validated_data.pop("extra_field", None)  #  pop удаляет только лишние данные

        note = Note.objects.create(**validated_data)
        return note


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password", "email"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data: Dict[str, Any]) -> User:
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data["email"],
        )
        return user
