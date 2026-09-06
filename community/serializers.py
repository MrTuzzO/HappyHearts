from rest_framework import serializers

from .models import Comment, Post, PostCategory, PostImage


class PostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCategory
        fields = ("id", "name")


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ("id", "image")


class PostAuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class CommentSerializer(serializers.ModelSerializer):
    user = PostAuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "post", "user", "content", "created_at")
        read_only_fields = ("post",)


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("content",)


class PostSerializer(serializers.ModelSerializer):
    user = PostAuthorSerializer(read_only=True)
    category = PostCategorySerializer(read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id", "user", "category", "content", "images",
            "likes_count", "comments_count", "is_liked",
            "created_at", "updated_at",
        )


class PostWriteSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=PostCategory.objects.all())
    images = serializers.ListField(
        child=serializers.ImageField(), required=False, allow_empty=True, write_only=True
    )

    class Meta:
        model = Post
        fields = ("id", "category", "content", "images")

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        post = Post.objects.create(user=self.context["request"].user, **validated_data)
        PostImage.objects.bulk_create([PostImage(post=post, image=img) for img in images])
        return post

    def update(self, instance, validated_data):
        images = validated_data.pop("images", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if images:
            PostImage.objects.bulk_create([PostImage(post=instance, image=img) for img in images])
        return instance
