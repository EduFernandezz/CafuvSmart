from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import Usuario

@receiver(user_logged_in)
def update_last_login(sender, request, user, **kwargs):
    Usuario.objects.filter(id=request.user.id).update(loggin = True)


@receiver(user_logged_out)
def update_last_logout(sender, request, user, **kwargs):
    Usuario.objects.filter(id=request.user.id).update(loggin = False)
