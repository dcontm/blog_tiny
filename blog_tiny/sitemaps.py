from django.contrib.sitemaps import Sitemap
from .models import Post, News
from django.urls import reverse


class PostSitemap(Sitemap):
    changefreq = "monthly"
    priority = 1

    def items(self):
        return Post.objects.all()

    def lastmod(self, obj):
        return obj.created


class NewsSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return News.objects.all()

    def lastmod(self, obj):
        return obj.created


class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ["news", "about"]

    def location(self, item):
        return reverse(item)


class RootSitemap(Sitemap):
    def items(self):
        return [self]

    location = "/"
    changefreq = "weekly"
    priority = "1"


class PostPythonSitemap(Sitemap):
    def items(self):
        return [self]

    location = "/post/python/"
    changefreq = "weekly"
    priority = "1"


class PostDjangoSitemap(Sitemap):
    def items(self):
        return [self]

    location = "/post/django/"
    changefreq = "weekly"
    priority = "1"


class PostOthersSitemap(Sitemap):
    def items(self):
        return [self]

    location = "/post/others/"
    changefreq = "weekly"
    priority = "1"
