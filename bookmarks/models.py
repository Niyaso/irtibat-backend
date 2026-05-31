from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#6366f1")

    class Meta:
        unique_together = ("user", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Collection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collections")
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "slug")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Bookmark(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")

    url = models.URLField(max_length=2000)
    title = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)

    # Auto-scraped metadata
    thumbnail_url = models.URLField(max_length=2000, blank=True)
    favicon_url = models.URLField(max_length=2000, blank=True)

    collections = models.ManyToManyField(Collection, blank=True, related_name="bookmarks")
    tags = models.ManyToManyField(Tag, blank=True, related_name="bookmarks")

    is_read = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or self.url