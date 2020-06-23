import itertools

from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.views.generic import TemplateView, ListView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import F  # need f
from django.db.models import Q  # rly?

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone
from django.template.loader import render_to_string


from .models import (
    Post,
    LikeSystem,
    Tag,
    Comment,
    Profile,
    News,
    Variable,
    Vote,
)
from .forms import CreateForm, CreateCommentForm, UpdateEmail
from .social_auth_utils import update_avatar
from .tasks import answer_notify_email

# ==================================================================================================#


def logout_view(request):
    logout(request)
    return redirect("/")


# ==================================================================================================#


class ProfileView(LoginRequiredMixin, TemplateView):

    template_name = "profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email_form"] = UpdateEmail
        return context


# ==================================================================================================#


class HomeView(ListView):

    template_name = "home.html"
    context_object_name = "posts"
    queryset = Post.objects.all()
    paginate_by = 12


# ==================================================================================================#


class PythonView(ListView):

    template_name = "python.html"
    context_object_name = "python_list"
    queryset = Post.objects.filter(theme="PYTHON")
    paginate_by = 12


# ==================================================================================================#


class DjangoView(ListView):

    template_name = "django.html"
    context_object_name = "django_list"
    queryset = Post.objects.filter(theme="DJANGO")
    paginate_by = 12


# ==================================================================================================#


class OthersView(ListView):

    template_name = "others.html"
    context_object_name = "others_list"
    queryset = Post.objects.filter(theme="OTHER")
    paginate_by = 12


# ==================================================================================================#


class SearchView(ListView):

    paginate_by = 12
    template_name = "search.html"
    context_object_name = "all_posts"

    def get_queryset(self, *args, **kwargs):
        query_request = self.request.GET.get("q")
        query = query_request.split(" ")
        all_posts = []

        if query:

            tags = [Tag.objects.filter(word__icontains=tag) for tag in query]
            tags = list(itertools.chain.from_iterable(tags))

            for tag in tags:
                post = Post.objects.filter(tags=tag)
                if post not in all_posts:
                    all_posts += post
            return all_posts


# ==================================================================================================#


class PostDetail(DetailView):

    model = Post
    form_class = CreateCommentForm

    def get(self, request, *args, **kwargs):

        respone = super().get(request, *args, **kwargs)

        self.object.views += 1
        self.object.save()

        return respone

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        comments = Comment.objects.filter(post=self.object)
        profiles = [
            Profile.objects.get(user=comment.author) for comment in comments
        ]
        context["last_posts"] = Post.objects.order_by("-id")[:3]
        context["popular_posts"] = Post.objects.order_by("-views")[:3]
        context["tags"] = Tag.objects.all()[:5]
        context["profiles"] = profiles
        context["comments"] = comments
        context["comments_count"] = len(
            Comment.objects.filter(post=self.object)
        )
        context["form"] = self.form_class
        return context


# ==================================================================================================#
class LikeSystemView(LoginRequiredMixin, View):
    model = None  # Значение поручаем из urls as_view()
    action_type = None  ##Значение поручаем из urls as_view()

    def post(self, request, pk):
        data = dict()
        content_object = self.model.objects.get(
            pk=pk
        )  # получаем экземпляр модели с которой работаем Post/Comment

        try:
            """ Пытаемся получить обьект likesystem для заданного обьекта конкретного пользователся
				(т.е. смотрим лайкал/дизлайкал ли этот обьект пользователь ранее)"""
            likedislike = LikeSystem.objects.get(
                content_type=ContentType.objects.get_for_model(
                    content_object
                ),  #
                object_id=content_object.id,
                user=request.user,
            )

            if (
                likedislike.action != self.action_type
            ):  # если ранее данным пользователем производились дейтсвия
                # над этим обьектом

                likedislike.action = (
                    self.action_type
                )  # если ранее лайкал, а теперь дизлайкает, или наоборот
                likedislike.save(
                    update_fields=["action"]
                )  # изменяем поле на нужное и сохраняем

            else:
                likedislike.delete()  # если повторяет дейтсвие - удаляем

        except:
            # если ранее не производились дейтвия создаем новый ообьект likesystem
            content_object.likesystem.create(
                action=self.action_type, user=request.user
            )

        data["likes"] = content_object.likesystem.likes().count()
        data["dislikes"] = content_object.likesystem.dislikes().count()

        return JsonResponse(data)


# ==================================================================================================#
class CommentView(LoginRequiredMixin, View):

    form_class = CreateCommentForm
    model = None

    def post(self, request, pk, *args, **kwargs):

        form = self.form_class(request.POST)
        content_object = self.model.objects.get(
            pk=pk
        )  # получаем экземпляр модели с которой работаем Post/News

        if form.is_valid():
            author = self.request.user
            content_type = ContentType.objects.get_for_model(content_object)

            if Comment.check_spam(author):
                message = form.cleaned_data["message"]
                comment = Comment.objects.create(
                    author=author,
                    content_type=content_type,
                    object_id=content_object.id,
                    message=message,
                )
                comments_count = len(
                    Comment.objects.filter(
                        content_type=content_type, object_id=content_object.id
                    )
                )
                new_comment = render_to_string(
                    "new_comment.html", {"comment": comment}
                )
                data = {
                    "new_comment": new_comment,
                    "comments_count": comments_count,
                }

                return JsonResponse(data, safe=False)

            else:
                return JsonResponse({"spam": True}, status=400)

        else:
            return JsonResponse(form.errors, status=400)


# ==================================================================================================#
class DeleteCommentView(LoginRequiredMixin, SingleObjectMixin, View):

    model = Comment

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()

        if (
            self.request.user == self.object.author
            or request.user.is_staff == True
        ):
            content_type = self.object.content_type
            self.object.delete()
            comments_count = len(
                Comment.objects.filter(
                    content_type=self.object.content_type,
                    object_id=self.object.object_id,
                )
            )
            data = {"comments_count": comments_count}
            return JsonResponse(data)


# ==================================================================================================#
class UpdateCommentView(LoginRequiredMixin, SingleObjectMixin, View):

    form_class = CreateCommentForm
    model = Comment

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)
        self.object = self.get_object()

        if form.is_valid():
            message = form.cleaned_data["message"]
            self.object.message = message
            self.object.updated = True
            self.object.created = timezone.now()
            object_id = self.object.object_id
            created = "0 минут"
            self.object.save()
            data = {"message": message, "created": created}
            return JsonResponse(data)
        else:
            return JsonResponse(form.errors, status=400)


# ==================================================================================================#
class CreateAnswerView(LoginRequiredMixin, SingleObjectMixin, View):

    form_class = CreateCommentForm
    model = Comment

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)
        self.object = self.get_object()

        if form.is_valid():
            author = self.request.user  # автор нового сообщения

            if Comment.check_spam(author):
                message = form.cleaned_data["message"]
                content_object = self.object.content_object

                profile = Profile.objects.get(user=self.object.author)

                user = self.object.author  # тот кому отвечают
                headline = (
                    self.object.content_object.headline
                )  # название поста/новости
                link_to = (
                    self.object.content_object.get_absolute_url()
                )  # ссылка на пост/новость
                original_text = (
                    self.object.message
                )  # cообщение на которое отвечают
                request_user_name = (
                    request.user.first_name + " " + request.user.last_name
                )  # кто отвечает

                if self.object.answer:
                    status = 1

                else:
                    status = 0

                answer = Comment.objects.create(
                    author=author,
                    content_type=self.object.content_type,
                    object_id=self.object.object_id,
                    message=message,
                    answer=self.object,
                    level=1,
                )

                if profile.subscribe_answers:

                    try:
                        answer_notify_email.delay(
                            user.id,
                            headline,
                            link_to,
                            original_text,
                            request_user_name,
                        )
                    except:
                        pass

                comments_count = len(
                    Comment.objects.filter(
                        content_type=self.object.content_type,
                        object_id=self.object.object_id,
                    )
                )
                new_answer = render_to_string(
                    "new_answer.html", {"answer": answer}
                )
                data = {
                    "new_answer": new_answer,
                    "comments_count": comments_count,
                    "status": status,
                }
                return JsonResponse(data, safe=False)
            else:
                return JsonResponse({"spam": True}, status=400)
        else:
            return JsonResponse(form.errors, status=400)


# ==================================================================================================#
class UpdateAvatarView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if self.request.is_ajax():
            profile = Profile.objects.get(user=request.user)
            avatar_url = update_avatar(profile.vk_user_ids)
            profile.avatar_url = avatar_url
            profile.save()
            data = {"avatar_url": avatar_url}
            return JsonResponse(data)
        else:
            return JsonResponse(status=400)


# ==================================================================================================#
class AboutView(TemplateView):

    template_name = "about.html"


# ==================================================================================================#
class ProfileSettingsView(LoginRequiredMixin, View):

    subscribe_type = None

    def post(self, request, *args, **kwargs):
        if self.request.is_ajax():
            profile = Profile.objects.get(user=request.user)

            if self.subscribe_type == Profile.subscribe_answers:
                profile.change_subscribe_status("subscribe_answers")

            elif self.subscribe_type == Profile.subscribe_article:
                profile.change_subscribe_status("subscribe_article")

            elif self.subscribe_type == Profile.subscribe_news:
                profile.change_subscribe_status("subscribe_news")

            data = {}

            return JsonResponse(data)

        else:

            return JsonResponse(status=400)


# ==================================================================================================#
class NewsView(ListView):

    template_name = "news.html"
    context_object_name = "news_list"
    queryset = News.objects.all()
    paginate_by = 20


# ==================================================================================================#


class NewsDetail(DetailView):

    model = News
    form_class = CreateCommentForm

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        comments = Comment.objects.filter(news=self.object)
        profiles = [
            Profile.objects.get(user=comment.author) for comment in comments
        ]

        context["last_posts"] = Post.objects.order_by("-id")[:3]
        context["popular_posts"] = Post.objects.order_by("-views")[:3]
        context["tags"] = Tag.objects.all()[:5]

        context["profiles"] = profiles
        context["comments"] = comments
        context["form"] = self.form_class
        return context


# ==================================================================================================#


class VotesView(LoginRequiredMixin, View):

    action_type = None

    def post(self, request, pk):

        data = dict()

        variable = Variable.objects.get(pk=pk)
        news = variable.news

        if news.question and news.question_is_active:

            variables = news.get_quest_variables()

            try:
                vote = Vote.objects.get(
                    news=news, user=request.user
                )  # проверка голосовал ли ранее в этом опросе

                if (
                    vote.variable == variable
                ):  # если голосовал за этот вариант и снова пытается проголосовать
                    vote.delete()

                else:  #  ранее голосовал за другой вариант
                    vote.delete()
                    Vote.objects.create(
                        news=news, variable=variable, user=request.user
                    )

            except:
                Vote.objects.create(
                    news=news, variable=variable, user=request.user
                )  # ранее не голосовал

            data["total_votes"] = news.total_votes()
            data["votes"] = [i.get_variable_info() for i in variables]

            return JsonResponse(data)


# ==================================================================================================#
