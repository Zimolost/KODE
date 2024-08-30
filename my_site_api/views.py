from typing import Any
from rest_framework.request import Request
from django.db.models import QuerySet
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Note
from .serializers import NoteSerializer, RegisterSerializer
from django.contrib.auth.models import User

import logging
import asyncio
import aiohttp


class NoteAPIListPagination(PageNumberPagination):
    page_size: int = 3
    page_size_query_param: str = "page_size"
    max_page_size: int = 10000


async def check_spelling(text: str) -> str:
    url: str = "https://speller.yandex.net/services/spellservice.json/checkText"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data={"text": text, "lang": "ru"}) as response:
            errors: list[dict[str, Any]] = await response.json()

    logging.debug(f"Yandex.Speller response: {errors}")

    corrected_text: str = text
    for error in errors:
        word: str = error["word"]
        correction: str = error["s"][0] if error["s"] else word
        corrected_text = corrected_text.replace(word, correction, 1)

    return corrected_text


class NoteAPIList(generics.ListCreateAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    pagination_class = NoteAPIListPagination

    def get_queryset(self) -> QuerySet[Note]:
        return self.queryset.filter(owner=self.request.user)

    def perform_create(self, serializer: NoteSerializer) -> None:
        title: str = serializer.validated_data.get("title")
        description: str = serializer.validated_data.get("description")

        corrected_title: str = asyncio.run(check_spelling(title))
        corrected_description: str = asyncio.run(check_spelling(description))
        serializer.save(
            owner=self.request.user,
            description=corrected_description,
            title=corrected_title,
        )


class NoteAPIDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

    def get_queryset(self) -> QuerySet[Note]:
        return self.queryset.filter(owner=self.request.user)


class RegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer: RegisterSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: User = serializer.save()
        return Response(
            {
                "user": RegisterSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "message": "User created successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            refresh_token: str = request.data["refresh"]
            token: RefreshToken = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
