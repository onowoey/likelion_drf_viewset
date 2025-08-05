from django.urls import path, include
from rest_framework import routers
from .views import PostViewSet, CommentViewSet, PostCommentViewSet, TagViewSet
from django.conf import settings
from django.conf.urls.static import static

app_name = "post"  # 앱 이름 맞춰서 수정

# Post
post_router = routers.SimpleRouter(trailing_slash=False)
post_router.register("posts", PostViewSet, basename="posts")

# comments(post 밑에 있는 게 아님)
comment_router = routers.SimpleRouter(trailing_slash=False)
comment_router.register("comments", CommentViewSet, basename="comments")

# 특정 post의 comments 
post_comment_router = routers.SimpleRouter(trailing_slash=False)
post_comment_router.register("comments", PostCommentViewSet, basename="post-comments")

# tags
tag_router = routers.SimpleRouter(trailing_slash=False)
tag_router.register("tags", TagViewSet, basename="tags")

urlpatterns = [
    path("", include(post_router.urls)),
    path("", include(comment_router.urls)),
    path("posts/<int:post_id>/", include(post_comment_router.urls)),
    path("", include(tag_router.urls)),
    path("likes/", include(post_router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
