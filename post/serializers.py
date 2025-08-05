from rest_framework import serializers
from .models import Post, Comment, Tag  # * 대신 명시적으로 import

class PostSerializer(serializers.ModelSerializer): #Post 글 자세히 보기
    id = serializers.CharField(read_only=True)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)

    comments = serializers.SerializerMethodField(read_only=True)

    def get_comments(self, instance):
        serializer = CommentSerializer(instance.comments, many=True)
        return serializer.data
    
    tags = serializers.SerializerMethodField() #실제 모델에 필드가 없어도 됨
    
    def get_tags(self, instance):
        tag = instance.tags.all()
        return [t.name for t in tag]

    class Meta:
        model = Post
        fields = '__all__' #실제 모델에 없는 필드라도 커스터마이징한 후 all 로 하면 다 뜸
        # fields = '__all__'
        # fields = ['id', 'name', 'content', 'created_at', 'updated_at']
        read_only_fields = [
            'id',
            'created_at',
            'comments',
            ]
    
    image = serializers.ImageField(use_url=True, required=False)
    
class PostListSerializer(serializers.ModelSerializer):
    
    comments_cnt = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField() #실제 모델에 필드가 없어도 됨

    def get_comments_cnt(self, instance):
        return instance.comments.count()
    
    
    def get_tags(self, instance):
        tag = instance.tags.all()
        return [t.name for t in tag]

    class Meta:
        model = Post
        #fields = '__all__' #실제 모델에 없는 필드라도 커스터마이징한 후 all 로 하면 다 뜸
        # fields = '__all__'
        fields = ['id', 'name', 'created_at', 'image', 'comments_cnt', 'tags']
        read_only_fields = ['id', 'created_at', 'comments_cnt']
    image = serializers.ImageField(use_url=True, required=False)

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['movie']
        
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        
