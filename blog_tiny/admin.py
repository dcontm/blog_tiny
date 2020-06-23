from django.contrib import admin
from django.db import models
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
from tinymce import TinyMCE


class TagInline(admin.TabularInline):
    model = Tag.post.through


class PostAdmin(admin.ModelAdmin):

    list_display = ("headline", "author", "created")
    list_filter = (
        "author",
        "created",
    )
    inlines = [TagInline]


formfield_overrides = {
    models.TextField: {"widget": TinyMCE(mce_attrs={"width": 800})},
}


class LikeSystemAdmin(admin.ModelAdmin):
    list_display = ("user",)


class TagAdmin(admin.ModelAdmin):
    list_display = ("word",)
    list_filter = ("post",)


class CommentAdmin(admin.ModelAdmin):
    list_display = ["id", "author", "content_type"]
    list_filter = (
        "content_type",
        "author",
        "created",
    )


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)


class NewsAdmin(admin.ModelAdmin):
    list_display = ["headline", "created"]
    list_filter = (
        "author",
        "created",
        "question",
        "question_is_active",
    )


class VariableAdmin(admin.ModelAdmin):
    list_display = ["title", "news"]
    list_filter = ("news",)


class VoteAdmin(admin.ModelAdmin):
    list_display = ["news", "variable", "user"]
    list_filter = (
        "news",
        "variable",
        "user",
    )


admin.site.register(Post, PostAdmin)
admin.site.register(LikeSystem, LikeSystemAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Profile, ProfileAdmin)

admin.site.register(News, NewsAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(Variable, VariableAdmin)
