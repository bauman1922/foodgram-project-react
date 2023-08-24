from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from django.core.validators import (EmailValidator, MinLengthValidator,
                                    RegexValidator)
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        verbose_name="Логин",
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+\z",
                message="Имя пользователя может содержать "
                "только буквы, цифры и символы: @/./+/-/_"
            ),
        ]
    )
    password = models.CharField(
        max_length=150,
        verbose_name="Пароль",
        validators=[
            MinLengthValidator(
                8,
                message="Пароль должен содержать как минимум 8 символов."
            ),
            validate_password,
        ],
        help_text="Пароль должен содержать как минимум одну цифру, "
        "одну букву в верхнем регистре и одну букву в нижнем регистре."
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Почтовый адрес",
        max_length=150,
        validators=[EmailValidator(
            message="Введите корректный адрес электронной почты.")]
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name="Имя",
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name="Фамилия",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор прецепта",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "author"],
                                    name="unique_subscription")
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.user.username} подписан на {self.author.username}"

    @classmethod
    def subscribe(cls, user, author):
        if not cls.objects.filter(user=user, author=author).exists():
            cls.objects.create(user=user, author=author)

    @classmethod
    def unsubscribe(cls, user, author):
        cls.objects.filter(user=user, author=author).delete()
