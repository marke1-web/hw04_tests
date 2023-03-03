from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

LENGHT = 15


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField("Текст поста", help_text="Текст нового поста")
    pub_date = models.DateTimeField(
        "Дата публикации", auto_now_add=True, db_index=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts"
    )
    image = models.ImageField("Картинка", upload_to="posts/", blank=True)

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.text[:LENGHT]

    group = models.ForeignKey(
        Group,
        verbose_name="Группа",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        help_text="Группа, к которой будет относиться пост",
    )

    class Meta:
        ordering = ["-pub_date"]

        def __str__(self):
            return self.text[:LENGHT]


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField(
        verbose_name="Текст комментария", help_text="Напишите комментарий"
    )
    created = models.DateTimeField(
        verbose_name="date published",
        auto_now_add=True,
        help_text="Дата публикации",
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, unique=False, related_name="following"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="user_author"
            )
        ]

    def __str__(self):
        return f"Пользователь:{self.user} подписался на {self.author}"
