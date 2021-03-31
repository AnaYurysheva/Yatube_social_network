import textwrap as tw

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Появилась умная мысль - пиши!')
    pub_date = models.DateTimeField(
        'published date',
        db_index=True,
        auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts')
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        blank=True,
        null=True,
        related_name='posts')
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        answer = [
            self.author,
            self.group,
            self.pub_date,
            tw.shorten(self.text, 15), ]
        return f'{answer}'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
        blank=True,
        null=True,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Текст',
        help_text='Будьте добрее друг к другу:)'
    )
    created = models.DateTimeField(
        'published date',
        auto_now_add=True)

    def __str__(self):
        return f'{self.author, self.text}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower', )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_follow')
        ]
