from .models import Profile
import requests
import json
import os

from .tasks import send_email_new_user


def save_profile(backend, user, response, *args, **kwargs):
    if backend.name == "vk-oauth2":

        try:
            profile = Profile.objects.get(user=user)

        except:

            data = {
                "user_ids": response["user_id"],
                "fields": "photo_200_orig",
                "access_token": response["access_token"],
                "v": "5.101",
            }
            first_name = response["first_name"]
            try:
                email = response["email"]
            except:
                pass
            response = requests.post(
                "https://api.vk.com/method/users.get/", data=data
            )
            response = response.json()

            if email:
                try:
                    send_email_new_user.delay(
                        email, first_name
                    )  # send email new user
                except:
                    pass

            try:
                avatar_url = response["response"][0]["photo_200_orig"]
                vk_user_ids = response["response"][0]["id"]
            except:
                avatar_url = "/media/avatars/default-XRANGE202418022019.jpg"

            Profile.objects.create(
                user=user, avatar_url=avatar_url, vk_user_ids=vk_user_ids
            )


def update_avatar(vk_user_ids):

    data = {
        "user_ids": vk_user_ids,
        "fields": "photo_200_orig",
        "access_token": os.environ.get("VK_TOKEN"),
        "v": "5.101",
    }
    try:
        response = requests.post(
            "https://api.vk.com/method/users.get/", data=data
        )
        response = response.json()
        avatar_url = response["response"][0]["photo_200_orig"]
        return avatar_url
    except:
        pass
