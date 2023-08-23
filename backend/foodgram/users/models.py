from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

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
