from .models import Profile


def profile(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        return {"profile": profile}
    else:
        return {}
