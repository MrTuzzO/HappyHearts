from django.urls import path
from . import views

urlpatterns = [
    path("categories/", views.PostCategoryListView.as_view(), name="post-categories"),
    path("posts/", views.PostListCreateView.as_view(), name="community-posts"),
    path("posts/<int:post_id>/", views.PostDetailView.as_view(), name="community-post-detail"),
    path("posts/<int:post_id>/like/", views.PostLikeToggleView.as_view(), name="community-post-like"),
    path("posts/<int:post_id>/comments/", views.PostCommentListCreateView.as_view(), name="community-post-comments"),
    path("comments/<int:comment_id>/", views.CommentDetailView.as_view(), name="community-comment-detail"),
]
