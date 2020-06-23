import pendulum
import datetime
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings

from django.db import models
from django.contrib.auth import get_user_model

from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType

from django.db.models.signals import post_save, pre_save
from .tasks import newPublicationPost, newPublicationNews

from tinymce import HTMLField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

from .utils import path_label_img, path_to_avatar, validate_avatar

# Create your models here.

USER = get_user_model()

# ==================================================================================================#
class Profile(models.Model):

    user = models.ForeignKey(USER, on_delete=models.CASCADE)

    avatar_url = models.CharField(
        max_length=200, default="/media/avatars/default-XRANGE202418022019.jpg"
    )

    vk_user_ids = models.CharField(max_length=200, blank=True, null=True)

    subscribe_answers = models.BooleanField(default=False)

    subscribe_article = models.BooleanField(default=True)

    subscribe_news = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def change_subscribe_status(self, type):

        if type == "subscribe_answers":
            if self.subscribe_answers == True:
                self.subscribe_answers = False
            else:
                self.subscribe_answers = True

        if type == "subscribe_article":
            if self.subscribe_article == True:
                self.subscribe_article = False
            else:
                self.subscribe_article = True

        if type == "subscribe_news":
            if self.subscribe_news == True:
                self.subscribe_news = False
            else:
                self.subscribe_news = True

        self.save()

    def last_seen(self):
        return cache.get("seen_%s" % self.user.username)

    def online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            if now > self.last_seen() + datetime.timedelta(seconds=300):
                return False
            else:
                return True
        else:
            return False


class Post(models.Model):

    VUE = "VUE"
    DJANGO = "DJANGO"
    PYTHON = "PYTHON"
    OTHER = "OTHER"

    THEMES = (
        (DJANGO, "Django"),
        (VUE, "Vue"),
        (PYTHON, "Python"),
        (OTHER, "Other"),
    )

    label_img = ProcessedImageField(
        upload_to=path_label_img,
        default="label_img/images.jpeg",
        processors=[ResizeToFill(500, 150)],
        format="JPEG",
        options={"quality": 100},
        blank=True,
        null=True,
    )

    theme = models.CharField(choices=THEMES, max_length=150)

    headline = models.CharField(max_length=500)

    description = models.CharField(max_length=1500, blank=True, null=True)

    article = HTMLField("Article")

    author = models.ForeignKey(USER, on_delete=models.CASCADE)

    created = models.DateTimeField(default=timezone.now)

    views = models.IntegerField(default=0)

    likesystem = GenericRelation(
        "LikeSystem", related_query_name="post"
    )  # like and dislike objects

    comments = GenericRelation(
        "Comment", related_query_name="post"
    )  # comments

    class Meta:
        ordering = ["-id"]
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.headline

    def get_tags(self):
        tags = Tag.objects.all().filter(post=self)
        return tags

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("post_detail", args=[str(self.id)])

    def get_created(self):
        created = pendulum.instance(self.created)
        created = created.format("DD MMMM YYYY", locale="ru")
        return created

    def comment_count(self):
        comment = Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
        )
        return comment.count()


# ==================================================================================================#


class LikeSystemManager(models.Manager):
    use_for_related_fields = True

    def likes(self):
        # Забираем queryset с записями больше 0
        return self.get_queryset().filter(action__gt=0)

    def dislikes(self):
        # Забираем queryset с записями меньше 0
        return self.get_queryset().filter(action__lt=0)


class LikeSystem(models.Model):

    LIKE = 1
    DISLIKE = -1

    ACTIONS = ((DISLIKE, "like"), (LIKE, "dislike"))

    action = models.SmallIntegerField(choices=ACTIONS)

    user = models.ForeignKey(USER, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    object_id = models.PositiveIntegerField()

    content_object = GenericForeignKey()

    objects = LikeSystemManager()

    class Meta:
        ordering = ["-id"]
        verbose_name = "Лайк/дизлайк"
        verbose_name_plural = "Лайки/дизлайки"


# ==================================================================================================#


class Tag(models.Model):

    post = models.ManyToManyField("Post", related_name="tags", blank=True)

    word = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.word


# ==================================================================================================#
class Comment(models.Model):

    author = models.ForeignKey(USER, on_delete=models.CASCADE)

    message = models.CharField(max_length=1000)

    answer = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True
    )

    level = models.SmallIntegerField(default=0)

    created = models.DateTimeField(default=timezone.now)

    updated = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    object_id = models.PositiveIntegerField()

    content_object = GenericForeignKey()

    likesystem = GenericRelation(
        "LikeSystem", related_query_name="comment"
    )  # like and dislike objects

    class Meta:
        ordering = ["-id"]
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def get_author_profile(self):
        return Profile.objects.get(user=self.author)

    def get_answer(self):
        answers = Comment.objects.filter(answer=self.id)
        answers = answers.reverse()
        return answers

    def get_author_avatar(self):
        profile = Profile.objects.get(user=self.author)
        return profile.avatar_url

    def get_created(self):
        created = pendulum.instance(self.created)
        created = created.format("DD MMMM YYYY", locale="ru")
        return created

    def get_updated(self):
        updated = pendulum.instance(self.created)
        updated = created.format("DD MMMM YYYY", locale="ru")
        return updated

    @staticmethod
    def check_spam(author):
        try:
            sp = Comment.objects.all().filter(author=author)[:3]
            dif = timezone.now() - sp[2].created
            if int(dif.total_seconds()) < 180:
                return False
            else:
                return True
        except:
            return True


# ==================================================================================================#


class News(models.Model):

    author = models.ForeignKey(USER, on_delete=models.CASCADE)

    headline = models.CharField(max_length=300)

    description = models.CharField(max_length=1500, blank=True, null=True)

    comments = GenericRelation(
        "Comment", related_query_name="news"
    )  # comments

    created = models.DateTimeField(default=timezone.now)

    question = models.BooleanField(default=False)

    question_headline = models.CharField(
        max_length=1000, blank=True, null=True
    )

    question_is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"

    def __str__(self):
        return self.headline

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("news_detail", args=[str(self.id)])

    def get_created(self):
        created = pendulum.instance(self.created)
        created = created.format("DD MMMM YYYY", locale="ru")
        return created

    def get_quest_variables(self):
        variables = Variable.objects.filter(news=self)
        return variables

    def total_votes(self):
        variables = Variable.objects.filter(
            news=self
        )  # все голосавания по данной новости
        total = sum(
            [Vote.objects.filter(variable=i).count() for i in variables]
        )
        return total

    def comment_count(self):
        comments = Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
        )
        return comments.count()


# ==================================================================================================#


class Variable(models.Model):

    news = models.ForeignKey(
        "News", on_delete=models.CASCADE, related_name="news"
    )

    title = models.CharField(max_length=300)

    class Meta:
        verbose_name = "Вариант"
        verbose_name_plural = "Варианты"

    def __str__(self):
        return self.title

    def get_votes(self):
        variable_votes = Vote.objects.filter(variable=self).count()
        return variable_votes

    def get_variable_proc(self):
        variable_votes = self.get_votes()
        total_news_votes = self.news.total_votes()

        try:
            percent = (variable_votes / total_news_votes) * 100
        except:
            percent = 0

        return round(percent, 1)

    def get_variable_info(self):
        variable_votes = self.get_votes()
        percent = self.get_variable_proc()

        return (self.id, variable_votes, percent)


# ==================================================================================================#


class Vote(models.Model):

    variable = models.ForeignKey(
        "Variable", on_delete=models.CASCADE, related_name="vote"
    )

    news = models.ForeignKey(
        "News", on_delete=models.CASCADE, related_name="vote"
    )

    user = models.ForeignKey(
        USER, on_delete=models.CASCADE, related_name="vote"
    )

    class Meta:

        verbose_name = "Голос"
        verbose_name_plural = "Голоса"

    def __str__(self):
        return self.variable.title


# ==================================================================================================#
def listenPostSignal(sender, instance, created, **kwargs):
    if created:
        try:
            newPublicationPost.delay(
                instance.headline, instance.get_absolute_url()
            )
        except:
            pass


post_save.connect(
    listenPostSignal, sender=Post, dispatch_uid="listenPostSignal"
)
# ==================================================================================================#
# ==================================================================================================#
def listenNewsSignal(sender, instance, created, **kwargs):
    if created:
        try:
            newPublicationNews.delay(
                instance.headline, instance.get_absolute_url()
            )
        except:
            pass


post_save.connect(
    listenNewsSignal, sender=News, dispatch_uid="listenNewsSignal"
)
# ==================================================================================================#
