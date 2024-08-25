from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ComponentViewSet

router = DefaultRouter()
router.register(r'components', ComponentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]