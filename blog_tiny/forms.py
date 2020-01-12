from django.forms import ModelForm
from django import forms
from . models import Post, Comment, USER



class CreateForm(ModelForm):

	class Meta:
		model = Post
		fields = ['theme','headline', 'article']

class CreateCommentForm(ModelForm):

	class Meta:
		model = Comment
		fields = ["message"]


class UpdateEmail(ModelForm):
	class Meta:
		model = USER
		fields = ['email']
			