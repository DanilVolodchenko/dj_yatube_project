from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        verbose_name='Содержание',
        help_text='Введите текст постов',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой относится пост'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Изображение относящееся к посту'
    )

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Наименование',
        help_text='Группа, к которой относится пост'
    )
    slug = models.SlugField(unique=True, verbose_name='Слаг')
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        indexes = [models.Index(fields=['slug'])]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор публикации'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Текст нового комментария'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время публикации',
    )

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    # делаю пары user и author уникальными
    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow')
        )
