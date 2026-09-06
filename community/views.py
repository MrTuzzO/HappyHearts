from django.db.models import Count, Exists, OuterRef
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.permissions import IsOwnerOrReadOnly
from .models import Comment, Post, PostCategory, PostLike
from .serializers import (
    CommentCreateSerializer,
    CommentSerializer,
    PostCategorySerializer,
    PostSerializer,
    PostWriteSerializer,
)


def annotate_posts(queryset, user):
    return queryset.annotate(
        likes_count=Count("likes", distinct=True),
        comments_count=Count("comments", distinct=True),
        is_liked=Exists(PostLike.objects.filter(post=OuterRef("pk"), user=user)),
    ).order_by("-created_at")


class PostCategoryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostCategorySerializer
    queryset = PostCategory.objects.all()
    pagination_class = None


class PostListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Post.objects.select_related("user", "category").prefetch_related("images")
        category_id = self.request.query_params.get("category")
        if category_id:
            qs = qs.filter(category_id=category_id)
        return annotate_posts(qs, self.request.user)

    def get_serializer_class(self):
        return PostWriteSerializer if self.request.method == "POST" else PostSerializer

    def create(self, request, *args, **kwargs):
        serializer = PostWriteSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        post = annotate_posts(Post.objects.filter(pk=post.pk), request.user).get()
        return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_url_kwarg = "post_id"

    def get_queryset(self):
        qs = Post.objects.select_related("user", "category").prefetch_related("images")
        return annotate_posts(qs, self.request.user)

    def get_serializer_class(self):
        return PostWriteSerializer if self.request.method in ("PUT", "PATCH") else PostSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PostWriteSerializer(
            instance, data=request.data, partial=kwargs.get("partial", False), context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance = annotate_posts(Post.objects.filter(pk=instance.pk), request.user).get()
        return Response(PostSerializer(instance).data)


class PostLikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = generics.get_object_or_404(Post, pk=post_id)
        like, created = PostLike.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()

        return Response({
            "liked": created,
            "likes_count": post.likes.count(),
        })


class PostCommentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs["post_id"]).select_related("user")

    def get_serializer_class(self):
        return CommentCreateSerializer if self.request.method == "POST" else CommentSerializer

    def create(self, request, *args, **kwargs):
        post = generics.get_object_or_404(Post, pk=self.kwargs["post_id"])
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(post=post, user=request.user)
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)


class CommentDetailView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_url_kwarg = "comment_id"
    queryset = Comment.objects.all()
