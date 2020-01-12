from django.core.exceptions import ValidationError
import uuid


def path_label_img(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'label_img/{0}'.format(uuid.uuid4())


def path_to_avatar(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'avatars/{0}'.format(uuid.uuid4())


def validate_avatar(avatar):

	file_size = avatar.file.size
	limit_size = 1024*1024*4		#4mb
	if file_size > limit_size:
		raise ValidationError("Максимальный размер файла 5 МБ")

