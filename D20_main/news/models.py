from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model


class Author(models.Model):
    user_author = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user_author.username


class Category(models.Model):
    tank = 'TN'
    healer = 'HL'
    damager = 'DD'
    guild_master = 'GM'
    quest_giver = 'KG'
    smith = 'KZ'
    tanner = 'KV'
    potion_maker = 'ZV'
    spell_master = 'MZ'

    TEMATIC = [
        (tank, 'Танк'),
        (healer, 'Хил'),
        (damager, 'ДД'),
        (guild_master, 'Гилдмастер'),
        (quest_giver, 'Квестгивер'),
        (smith, 'Кузнец'),
        (tanner, 'Кожевник'),
        (potion_maker, 'Зельевар'),
        (spell_master, 'Мастер заклинаний'),
    ]

    tematic = models.CharField(max_length=2, choices=TEMATIC, unique=True)
    subscribers = models.ManyToManyField(User, blank=True, related_name='categories')

    def __str__(self):
        return self.get_tematic_display()


post = 'PO'
POST = [
    (post, 'ПОСТ')
]


class Post(models.Model):
    author_post = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_news = models.CharField(max_length=2, choices=POST, default='PO')
    date_in = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=50)
    text = RichTextField()
    video_count = models.PositiveIntegerField(default=0)
    image_count = models.PositiveIntegerField(default=0)
    max_video_count = 1
    max_image_count = 3

    def add_video(self):
        if self.video_count >= self.max_video_count:
            raise ValueError("Превышено максимальное количество видео")
        self.video_count += 1

    def add_image(self):
        if self.image_count >= self.max_image_count:
            raise ValueError("Превышено максимальное количество изображений")
        self.image_count += 1

    def __str__(self):
        return self.title

    def preview(self):
        return self.text[0:124] + '...'

    def get_absolute_url(self):  # добавим абсолютный путь, чтобы после создания нас перебрасывало на страницу с постом
        return f'/news/{self.id}'

    def approved_comments(self):
        return self.comments.filter(approved_comment=True)


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    text = models.TextField()
    data_time_comment = models.DateTimeField(auto_now_add=True)
    post_comment = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_comment = models.ForeignKey(User, on_delete=models.CASCADE)
    #parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='comments_as_parent')
    subscriptions = models.ManyToManyField(get_user_model(), related_name='subscriptions', blank=True)
    # хранит связанных пользователей, которые подписаны на уведомления
    approved = models.BooleanField(default=False)
    #reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='comments_as_reply_to')
    # ссылается на родительский комментарий
    def __str__(self):
        return self.text

    def approve(self):
        self.approved = True
        self.save()


class Reply(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class BaseRegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="Имя")
    last_name = forms.CharField(label="Фамилия")

    class Meta:
        model = User
        fields = ("username",
                  "first_name",
                  "last_name",
                  "email",
                  "password1",
                  "password2", )

