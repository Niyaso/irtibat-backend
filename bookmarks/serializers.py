from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Bookmark, Collection, Tag


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "color"]
        read_only_fields = ["id"]

class CollectionSerializer(serializers.ModelSerializer):
    bookmark_count = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ["id", "name", "slug", "is_public", "created_at", "bookmark_count"]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {
            "slug": {"required": False, "allow_blank": True}
        }

    def get_bookmark_count(self, obj):
        return obj.bookmarks.count()

    def validate_slug(self, value):
        user = self.context["request"].user
        qs = Collection.objects.filter(user=user, slug=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("You already have a collection with this slug.")
        return value


class BookmarkSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(),
        write_only=True, required=False, source="tags"
    )
    collections = CollectionSerializer(many=True, read_only=True)
    collection_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Collection.objects.all(),
        write_only=True, required=False, source="collections"
    )

    class Meta:
        model = Bookmark
        fields = [
            "id", "url", "title", "description",
            "thumbnail_url", "favicon_url",
            "tags", "tag_ids",
            "collections", "collection_ids",
            "is_read", "is_public",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "thumbnail_url", "favicon_url", "created_at", "updated_at"]

    def validate_tag_ids(self, tags):
        user = self.context["request"].user
        for tag in tags:
            if tag.user != user:
                raise serializers.ValidationError("Invalid tag.")
        return tags

    def validate_collection_ids(self, collections):
        user = self.context["request"].user
        for col in collections:
            if col.user != user:
                raise serializers.ValidationError("Invalid collection.")
        return collections


class PublicCollectionSerializer(serializers.ModelSerializer):
    bookmarks = BookmarkSerializer(many=True, read_only=True)
    owner = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Collection
        fields = ["id", "name", "slug", "owner", "created_at", "bookmarks"]