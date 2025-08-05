from django.shortcuts import render
from rest_framework import viewsets, mixins
from .models import Post, Comment, Tag
from .serializers import PostListSerializer, PostSerializer, CommentSerializer, TagSerializer

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
import re
from .permissions import IsOwnerReadOnly
from rest_framework.decorators import action


# Create your views here.

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()#뷰셋이 처리할 기본 데이터 설정
    
    ##self.action 이란 -> 현재 실행 중인 ViewSet 메서드 종류
    def get_serializer_class(self):
        if self.action == "list": #list 조회일때는 간단한 리스트만 보여줌 -> 여기서는 댓글 자세히 못보고 개수로만 볼 수 있게 설정
            return PostListSerializer
        return PostSerializer # 그외에는 자세한 정보 포함되게 보여줌
    
    def get_permissions(self): #updatem destroy, partial_update 함수 실행시에는 꼭 본인만 가능하게 해야함
        if self.action in ["update", "destroy", "partial_update"]:
            return [IsOwnerReadOnly()] #본인만 수정이나 삭제 가능
        return []
    
    def create(self, request): #self = 해당 객체
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer) # 실제 생성은 perform_create 에서 실행됨
        
        post = serializer.instance
        self.handle_tags(post)
        
        return Response(serializer.data)
    
    def perform_update(self,serializer):
        post = serializer.save()
        post.tags.clear()
        self.handle_tags(post)
        
        
    def handle_tags(self, post):
        words = re.split(r'[\s,]+', post.content.strip())
        tag_list = []
        
        for w in words:
            if len(w) > 0:
                if w[0] == '#':
                    tag_list.append(w[1:])
        for t in tag_list:
            tag, _ = Tag.objects.get_or_create(name=t)
            post.tags.add(tag)
        post.save()
        
    @action(methods=["get"], url_path="likes", detail=True)
    #detail 이 true 라서 url 에 pk 반영 -> posts/3/likes 이런느낌
    def like(self, request, pk=None):
        post = self.get_object()
        post.likes += 1
        post.save(update_fields=["likes"])
        return Response({"likes": post.likes})
    
    @action(methods=["get"], url_path="top3like", detail=False)
    #얘는 detail 이 false 라서 url에 pk 반영 안됨 ->/posts/top3like
    def top_liked(self, request):
        top_posts = Post.objects.order_by("-likes")[:3]
        serializer = self.get_serializer(top_posts, many=True)
        return Response(serializer.data)
        
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    #def get_permissions(self):
        #if self.action in ["update", "destroy", "partial_update"]:
            #return [IsOwnerReadOnly()]
        #return []
    
class PostCommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        post = self.kwargs.get("post_id") #self.kwargs는 URL에서 전달된 파라미터들
        queryset = Comment.objects.filter(post_id= post)
        return queryset
    
    def create(self, request, post_id=None):
        post = get_object_or_404(Post, id = post_id)
        serializer = self.get_serializer(data= request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post)
        #외래키(post)를 꼭 넘겨줘야 하는 상황에서는, self.perform_create(serializer) 이것만 단순히 쓰기 불가능
        #def perform_create(self, serializer):
            #post = get_object_or_404(Post, id=self.kwargs.get("post_id"))
            #serializer.save(post=post)
        #위처럼 오버라이딩해서 사용하거나 serializer.save(post=post) 이렇게 사용.
        
        return Response(serializer.data)   
    
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = "name"
    lookup_url_kwarg = "tags_name"
    
    def retrieve(self, request, *args, **kwargs):
        tags_name = kwargs.get("tags_name")
        tags = get_object_or_404(Tag, name= tags_name)
        posts = Post.objects.filter(tags=tags)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)