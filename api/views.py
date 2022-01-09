from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions

from api.models import Product
from .serializers import ProductSerializer

# Create your views here.


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
    permissions_classess=[permissions.AllowAny]
