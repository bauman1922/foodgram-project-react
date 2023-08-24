from rest_framework import viewsets
from users.models import User
from .serializers import UserProfileSerializer
from rest_framework.permissions import AllowAny


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (AllowAny,)


class TagViewSet(viewsets.ModelViewSet):
    pass


class IngredientViewSet(viewsets.ModelViewSet):
    pass


class RecipeViewSet(viewsets.ModelViewSet):
    pass


