from rest_framework import viewsets
from .models import Component
from .serializers import ComponentSerializer

class ComponentViewSet(viewsets.ModelViewSet):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer