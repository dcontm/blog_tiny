from django.urls import path, include
from django.contrib.auth import logout
from . import views
from .models import Post, LikeSystem, Comment, Profile, Variable, News, Vote

from django.conf.urls.static import static
from django.conf import settings

from django.contrib.sitemaps.views import sitemap  # sitemap
from . import sitemaps

sitemaps = {
    "posts": sitemaps.PostSitemap,
    "news": sitemaps.NewsSitemap,
    "static": sitemaps.StaticSitemap,
    "root": sitemaps.RootSitemap,
    "django": sitemaps.PostDjangoSitemap,
    "python": sitemaps.PostPythonSitemap,
    "others": sitemaps.PostOthersSitemap,
}


urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("", include("social_django.urls")),
    path("tinymce/", include("tinymce.urls")),
    path("search/", views.SearchView.as_view(), name="search"),
    path("logout/", views.logout_view, name="logout"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("post/python/", views.PythonView.as_view(), name="python"),
    path("post/django/", views.DjangoView.as_view(), name="django"),
    path("post/others/", views.OthersView.as_view(), name="others"),
    path("post/<pk>/", views.PostDetail.as_view(), name="post_detail"),
    path(
        "post/<pk>/comments/",
        views.CommentView.as_view(model=Post),
        name="comments",
    ),
    path(
        "post/<pk>/like/",
        views.LikeSystemView.as_view(model=Post, action_type=LikeSystem.LIKE),
        name="like",
    ),
    path(
        "post/<pk>/dislike/",
        views.LikeSystemView.as_view(
            model=Post, action_type=LikeSystem.DISLIKE
        ),
        name="dislike",
    ),
    path(
        "comment/<pk>/like/",
        views.LikeSystemView.as_view(
            model=Comment, action_type=LikeSystem.LIKE
        ),
        name="like",
    ),
    path(
        "comment/<pk>/dislike/",
        views.LikeSystemView.as_view(
            model=Comment, action_type=LikeSystem.DISLIKE
        ),
        name="dislike",
    ),
    path(
        "comment/<pk>/delete/",
        views.DeleteCommentView.as_view(),
        name="delete_comment",
    ),
    path(
        "comment/<pk>/update/",
        views.UpdateCommentView.as_view(),
        name="update_comment",
    ),
    path(
        "comment/<pk>/answer/",
        views.CreateAnswerView.as_view(),
        name="answer_comment",
    ),
    path(
        "profile/settings/answers/",
        views.ProfileSettingsView.as_view(
            subscribe_type=Profile.subscribe_answers
        ),
        name="profile_settings_answers",
    ),
    path(
        "profile/settings/article/",
        views.ProfileSettingsView.as_view(
            subscribe_type=Profile.subscribe_article
        ),
        name="profile_settings_article",
    ),
    path(
        "profile/settings/news/",
        views.ProfileSettingsView.as_view(
            subscribe_type=Profile.subscribe_news
        ),
        name="profile_settings_news",
    ),
    path(
        "update_avatar/",
        views.UpdateAvatarView.as_view(),
        name="update_avatar",
    ),
    path("news/", views.NewsView.as_view(), name="news"),
    path("news/<pk>/", views.NewsDetail.as_view(), name="news_detail"),
    path(
        "news/<pk>/comments/",
        views.CommentView.as_view(model=News),
        name="comments",
    ),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("variable/<pk>/", views.VotesView.as_view(), name="votes"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
