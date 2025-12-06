from rest_framework import serializers
from .models import Post, Category, Tag, Comment, DraftAutosave


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        required=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "excerpt",
            "story",
            "body",
            "status",
            "categories",
            "tags",
            "featured_image",
            "reading_time",
            "published_at",
            "author",
        ]
        read_only_fields = ["reading_time", "published_at", "author", "slug"]
    def create(self, validated_data):
        categories = validated_data.pop('categories', [])
        tags = validated_data.pop('tags', [])

        # Create post (featured_image will be handled from validated_data if present)
        post = Post.objects.create(**validated_data)

        if categories:
            post.categories.set(categories)
        if tags:
            post.tags.set(tags)

        return post

    def update(self, instance, validated_data):
        categories = validated_data.pop('categories', None)
        tags = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if categories is not None:
            instance.categories.set(categories)
        if tags is not None:
            instance.tags.set(tags)

        return instance


class DraftAutosaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = DraftAutosave
        fields = ["id", "user", "post", "title", "body", "updated_at"]
        read_only_fields = ["updated_at", "user"]
