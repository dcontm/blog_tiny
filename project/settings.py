"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 2.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings
"""
from __future__ import absolute_import, unicode_literals
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'u6ov+m)%#t_e=zq+fldtm!plaa)n*7mxq-)ph%mgt+hvrnnsk4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
	'filebrowser',

	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',

	'blog_tiny',

	'social_django',


	'imagekit',
	'tinymce',

]


MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'blog_tiny.middleware.ActivateUserMiddleware',           #check user online 
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [os.path.join(BASE_DIR, 'templates/blog')],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
				'social_django.context_processors.backends', # for auth
				'blog_tiny.context_processors.profile',
			],
		},
	},
]

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
	}
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'static'
MEDIA_URL = '/media/'
MEDIA_ROOT = 'media'

#-----------------------------------------------------------------------------------------------#
#                                 Setting Djanfo-Social App                                      #
#-----------------------------------------------------------------------------------------------#

AUTHENTICATION_BACKENDS  =  ( 
	'social_core.backends.vk.VKOAuth2',
	'django.contrib.auth.backends.ModelBackend', 
)

LOGIN_REDIRECT_URL = '/profile/'
SOCIAL_AUTH_VK_OAUTH2_SCOPE = ['email']

SOCIAL_AUTH_VK_OAUTH2_KEY = '7125221'
SOCIAL_AUTH_VK_OAUTH2_SECRET = '4DhZU1b3tZO9BXnLio4v'

SOCIAL_AUTH_PIPELINE = (
	# Get the information we can about the user and return it in a simple
	# format to create the user instance later. On some cases the details are
	# already part of the auth response from the provider, but sometimes this
	# could hit a provider API.
	'social_core.pipeline.social_auth.social_details',

	# Get the social uid from whichever service we're authing thru. The uid is
	# the unique identifier of the given user in the provider.
	'social_core.pipeline.social_auth.social_uid',

	# Verifies that the current auth process is valid within the current
	# project, this is where emails and domains whitelists are applied (if
	# defined).
	'social_core.pipeline.social_auth.auth_allowed',

	# Checks if the current social-account is already associated in the site.
	'social_core.pipeline.social_auth.social_user',

	# Make up a username for this person, appends a random string at the end if
	# there's any collision.
	'social_core.pipeline.user.get_username',

	# Send a validation email to the user to verify its email address.
	# Disabled by default.
	# 'social_core.pipeline.mail.mail_validation',

	# Associates the current social details with another user account with
	# a similar email address. Disabled by default.
	# 'social_core.pipeline.social_auth.associate_by_email',

	# Create a user account if we haven't found one yet.
	'social_core.pipeline.user.create_user',

	#my way
	'blog_tiny.social_auth_utils.save_profile',

	# Create the record that associates the social account with the user.
	'social_core.pipeline.social_auth.associate_user',

	# Populate the extra_data field in the social record with the values
	# specified by settings (and the default ones like access_token, etc).
	'social_core.pipeline.social_auth.load_extra_data',

	# Update the user record with any changed info from the auth service.
	'social_core.pipeline.user.user_details',
)


#-----------------------------------------------------------------------------------------------#
#                                 Setting Caches (memcached)                                    #
#-----------------------------------------------------------------------------------------------#

CACHES = {
	'default':{
		"BACKEND":'django.core.cache.backends.memcached.MemcachedCache',
		"LOCATION": '127.0.0.1:11211',
	}
}

USER_ONLINE_TIMEOUT = 180                           #check user online
USER_LASTSEEN_TIMEOUT = 60*60*24*7					#check user online

#-----------------------------------------------------------------------------------------------#
#                                 Setting Email Backend                                         #
#-----------------------------------------------------------------------------------------------#

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'dcontm@gmail.com'
EMAIL_HOST_PASSWORD = 'vonderland'
DEFAULT_FROM_EMAIL = 'dcontm@gmail.com'
DEFAULT_TO_EMAIL = 'dcontm@gmail.com'

#-----------------------------------------------------------------------------------------------#
#                                 Setting Celery                                                #
#-----------------------------------------------------------------------------------------------#

CELERY_BROKER_URL = 'amqp://localhost'

#-----------------------------------------------------------------------------------------------#
#                                 Setting Sentry                                                #
#-----------------------------------------------------------------------------------------------#
'''
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
	dsn="https://0319587e158d45f49ec572a89e40b6bb@sentry.io/1862635",
	integrations=[DjangoIntegration()],

	# If you wish to associate users to errors (assuming you are using
	# django.contrib.auth) you may enable sending PII data.
	send_default_pii=True
)'''
#-----------------------------------------------------------------------------------------------#