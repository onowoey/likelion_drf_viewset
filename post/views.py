from django.shortcuts import render
from rest_framework import viewsets, mixins

# Create your views here.

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = 
