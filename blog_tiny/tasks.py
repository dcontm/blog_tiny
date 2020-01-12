from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time

from django.core.mail import send_mail
from django.conf import settings

from django.apps import apps
from django.contrib.auth import get_user_model

from django.db.models.signals import post_save, pre_save

#Нужно это в отдельный файл
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template.loader import render_to_string




USER=get_user_model()

#===============================================================================================#
@shared_task
def newPublicationPost(headline, link_to):

	users=USER.objects.all()

	Profile=apps.get_app_config('blog_tiny').get_model('Profile')

	htmly = 'email/email_new_post.html'

	for user in users:
		first_name = user.first_name
		profile=Profile.objects.get(user=user)
			
		if profile.subscribe_article:
			content={'first_name':first_name,'headline':headline, 'link_to':link_to}
			message=render_to_string(htmly,content)
			try:
				email=user.email
				send_mail('Новая публикация на Tiny.',
							'',
							settings.DEFAULT_FROM_EMAIL,
							[email], 
							fail_silently=False,
							html_message=message)
			except:
				pass
#===============================================================================================#
@shared_task
def newPublicationNews(headline,link_to):

	users=USER.objects.all()

	Profile=apps.get_app_config('blog_tiny').get_model('Profile')

	htmly = 'email/email_new_news.html'

	for user in users:
		first_name = user.first_name
		profile=Profile.objects.get(user=user)
			
		if profile.subscribe_article:
			content={'first_name':first_name,'headline':headline, 'link_to':link_to}
			message=render_to_string(htmly,content)
			try:
				email=user.email
				send_mail('Новая публикация на Tiny.',
							'',
							settings.DEFAULT_FROM_EMAIL,
							[email],
							fail_silently=False,
							html_message=message)
			except:
				pass
#================================================================================================#
@shared_task
def send_email_new_user(email, first_name):

	htmly = 'email/email_new_user.html' 
	content={'first_name':first_name}

	message=render_to_string(htmly,content)
			
	try:
		send_mail('Регистрация на Tiny.',
					'',
					settings.DEFAULT_FROM_EMAIL,
					[email], 
					fail_silently=False,
					html_message=message)
	except:
		pass
#================================================================================================#
@shared_task
def answer_notify_email(user_id, headline, link_to, original_text, request_user_name):

	htmly     = 'email/email_comment_notify.html'
	user = USER.objects.get(pk=user_id)
	email=user.email

	content={'first_name':user.first_name, 'headline':headline, 'link_to':link_to,
			'original_text':original_text, 'request_user_name':request_user_name}

	message=render_to_string(htmly,content)

	try:
		send_mail('Уведомление Tiny.',
						'',
						settings.DEFAULT_FROM_EMAIL,
						[email], 
						fail_silently=False,
						html_message=message)
	except:
		pass

#================================================================================================#