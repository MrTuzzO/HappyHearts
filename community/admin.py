from django.contrib import admin
from .models import Comment, Post, PostCategory, PostImage, PostLike


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1


@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "category", "created_at")
    list_filter = ("category",)
    search_fields = ("content", "user__email")
    autocomplete_fields = ("user", "category")
    inlines = [PostImageInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "user", "created_at")
    search_fields = ("content", "user__email")
    autocomplete_fields = ("user", "post")


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "created_at")
    autocomplete_fields = ("user", "post")
