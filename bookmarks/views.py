from django.shortcuts import render

# Create your views here.
from rest_framework import generics, viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.http import HttpResponse

from .models import Bookmark, Collection, Tag
from .serializers import (
    RegisterSerializer, UserSerializer,
    BookmarkSerializer, CollectionSerializer,
    TagSerializer, PublicCollectionSerializer,
)
from .scraper import scrape_url_metadata


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Collection.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        name = serializer.validated_data.get("name", "")
        slug = serializer.validated_data.get("slug") or slugify(name)
        serializer.save(user=self.request.user, slug=slug)


class PublicCollectionView(generics.RetrieveAPIView):
    serializer_class = PublicCollectionSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        username = self.kwargs["username"]
        slug = self.kwargs["slug"]
        return generics.get_object_or_404(
            Collection,
            user__username=username,
            slug=slug,
            is_public=True,
        )


class BookmarkViewSet(viewsets.ModelViewSet):
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "url"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = Bookmark.objects.filter(user=self.request.user).prefetch_related("tags", "collections")

        is_read = self.request.query_params.get("is_read")
        if is_read is not None:
            qs = qs.filter(is_read=is_read.lower() == "true")

        tag_id = self.request.query_params.get("tag")
        if tag_id:
            qs = qs.filter(tags__id=tag_id)

        collection_id = self.request.query_params.get("collection")
        if collection_id:
            qs = qs.filter(collections__id=collection_id)

        return qs.distinct()

    def perform_create(self, serializer):
        url = serializer.validated_data.get("url", "")
        metadata = {}
        if not serializer.validated_data.get("title"):
            metadata = scrape_url_metadata(url)

        serializer.save(
            user=self.request.user,
            title=serializer.validated_data.get("title") or metadata.get("title", ""),
            description=serializer.validated_data.get("description") or metadata.get("description", ""),
            thumbnail_url=metadata.get("thumbnail_url", ""),
            favicon_url=metadata.get("favicon_url", ""),
        )

    @action(detail=True, methods=["patch"], url_path="toggle-read")
    def toggle_read(self, request, pk=None):
        bookmark = self.get_object()
        bookmark.is_read = not bookmark.is_read
        bookmark.save()
        return Response({"is_read": bookmark.is_read})

    @action(detail=False, methods=["get"], url_path="read-later")
    def read_later(self, request):
        qs = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class QuickSaveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        url = request.data.get("url", "").strip()
        title = request.data.get("title", "").strip()

        if not url:
            return Response({"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent duplicates
        existing = Bookmark.objects.filter(user=request.user, url=url).first()
        if existing:
            return Response(
                {"message": "Already saved", "id": str(existing.id)},
                status=status.HTTP_200_OK,
            )

        metadata = {}
        if not title:
            metadata = scrape_url_metadata(url)

        bookmark = Bookmark.objects.create(
            user=request.user,
            url=url,
            title=title or metadata.get("title", ""),
            description=metadata.get("description", ""),
            thumbnail_url=metadata.get("thumbnail_url", ""),
            favicon_url=metadata.get("favicon_url", ""),
        )

        return Response(
            {"message": "Saved!", "id": str(bookmark.id), "title": bookmark.title},
            status=status.HTTP_201_CREATED,
        )