from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.text import Truncator

from blog.constants import MAX_LENGTH, MAX_TEXT, MAX_WORDS_LENGTH

User = get_user_model()


class PublishedBaseModel(models.Model):
    is_published = models.BooleanField(
        default=True, verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Добавлено',
    )

    class Meta:
        abstract = True


class Category(PublishedBaseModel):
    title = models.CharField(
        max_length=MAX_LENGTH, unique=True,
        verbose_name='Заголовок',
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return (Truncator(self.title).words(MAX_WORDS_LENGTH))


class Location(PublishedBaseModel):
    name = models.CharField(
        max_length=MAX_LENGTH, verbose_name='Название места',
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return (Truncator(self.name).words(MAX_WORDS_LENGTH))


class Post(PublishedBaseModel):
    title = models.CharField(max_length=MAX_LENGTH, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.',
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Местоположение',
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
    )
    image = models.ImageField(
        upload_to='post_images',
        blank=True,
        verbose_name='Изображение к публикации'
    )

    class Meta:
        default_related_name = 'posts'
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return (Truncator(self.title).words(MAX_WORDS_LENGTH))

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.pk})


class Comment(PublishedBaseModel):
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Комментарий',
    )

    class Meta:
        default_related_name = 'comments'
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарий'
        ordering = ('created_at',)

    def __str__(self):
        return (f'Комментарий автора {self.author}'
                f'к посту "{self.post}",'
                f'текст: {self.text[:MAX_TEXT]}')
