from django.urls import include,path
from rest_framework import routers, urlpatterns
import rest_framework
from . import views

router =routers.DefaultRouter()
router.register(r'products',views.ProductViewSet)

urlpatterns = [
    path('',include(router.urls)),
    path('api-aut/',include('rest_framework.urls',namespace='rest_framework'))
]