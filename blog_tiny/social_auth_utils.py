from . models import Profile
import requests
import json

from . tasks import send_email_new_user


def save_profile(backend, user, response, *args, **kwargs):
	if backend.name == 'vk-oauth2':
		try:
			profile = Profile.objects.get(user=user)
		except:
			data = {'user_ids':response['user_id'], 'fields':'photo_200_orig','access_token':response['access_token'], 'v':'5.101'}
			email=response['email']
			first_name=response['first_name']
			response = requests.post('https://api.vk.com/method/users.get/', data=data)
			response=response.json()

			send_email_new_user.delay(email,first_name) #send email new user
			
			try:
				avatar_url = response['response'][0]['photo_200_orig']
				vk_user_ids = response['response'][0]['id']
			except:
				avatar_url='/media/avatars/default-XRANGE202418022019.jpg'
				
			Profile.objects.create(user=user, avatar_url=avatar_url, vk_user_ids=vk_user_ids)


def update_avatar(vk_user_ids):
	
	data = {'user_ids':vk_user_ids, 'fields':'photo_200_orig','access_token':'c951c2472481e13f788ea7caf899af9ee13248318f4a57412ee7595e5c9ccc0e801b2369e7c7fd15d8060', 'v':'5.101'}
	response = requests.post('https://api.vk.com/method/users.get/', data=data)
	response=response.json()
	avatar_url = response['response'][0]['photo_200_orig']

	return avatar_url