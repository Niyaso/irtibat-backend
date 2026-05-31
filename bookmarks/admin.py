from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Bookmark, Collection, Tag


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ["title", "url_short", "user", "is_read", "is_public", "created_at"]
    list_filter = ["is_read", "is_public", "created_at"]
    search_fields = ["title", "url", "description"]
    readonly_fields = ["id", "thumbnail_url", "favicon_url", "created_at", "updated_at"]

    def url_short(self, obj):
        return obj.url[:60] + "..." if len(obj.url) > 60 else obj.url
    url_short.short_description = "URL"


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "slug", "is_public", "created_at"]
    list_filter = ["is_public"]
    search_fields = ["name", "user__username"]
    readonly_fields = ["id", "created_at"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "color"]
    search_fields = ["name", "user__username"]
    readonly_fields = ["id"]