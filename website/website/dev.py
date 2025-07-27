from .base import *

DEBUG = True

SECRET_KEY = "django-yvarunya-vw-2=s-5wzz13igxur_zr_kbo7!^*2lg!c!18@m&gh2=8aauj!"

ALLOWED_HOSTS = []  # Dev can be localhost or 127.0.0.1

# Email, Cache etc for Dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"