from django.contrib import admin
from .models import Category, Tag, Post, Revision, DraftAutosave, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
	prepopulated_fields = {"slug": ("name",)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
	list_display = ("title", "author", "status", "published_at")
	list_filter = ("status", "categories")
	search_fields = ("title", "excerpt", "body")
	prepopulated_fields = {"slug": ("title",)}
	readonly_fields = ("views", "reading_time")


@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
	list_display = ("post", "author", "created_at")
	readonly_fields = ("created_at",)


@admin.register(DraftAutosave)
class DraftAutosaveAdmin(admin.ModelAdmin):
	list_display = ("user", "post", "updated_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ("post", "author", "approved", "is_spam", "created_at")
	list_filter = ("approved", "is_spam")