import webcolors
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Ingredient, Tag
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.models import Subscription, User


class UserRegistrationSerializer(UserCreateSerializer):
    """Сериализатор пользователя при регистрации."""
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class UserProfileSerializer(UserSerializer):
    """Сериализатор пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed"
        )

    def get_is_subscribed(self, obj):
        current_user = self.context["request"].user
        if not current_user.is_authenticated:
            return False
        return Subscription.objects.filter(
            user=current_user, author=obj).exists()


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"
