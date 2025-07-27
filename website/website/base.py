from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR, '.env'))

if "SECRET_KEY" in os.environ:
    SECRET_KEY = os.environ["SECRET_KEY"]
else:
    SECRET_KEY = "dummy-secret-key-for-gunicorn-testing-only-1234567890abcdefghijklmnopqrstuvwxyz"
    print("WARNING: SECRET_KEY environment variable is NOT set! Using a dummy key for testing.")

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

if "CSRF_TRUSTED_ORIGINS" in os.environ:
    CSRF_TRUSTED_ORIGINS = os.environ["CSRF_TRUSTED_ORIGINS"].split(",")
else:
    CSRF_TRUSTED_ORIGINS = [] 


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'bavaalapps',
    'blog',
    'webstory',
    'influencer',
    'django_ckeditor_5',
    # Required for allauth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # Add providers for social logins you want to support
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'django.contrib.sitemaps',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'website.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'website.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), # If you have a project-level static folder
]


# Or, if you prefer to collect static files from each app's 'static' folder:
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # For production deployment

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # This will be E:\projectbavaal\website\media

CKEDITOR_UPLOAD_PATH = "uploads/"


# CKEditor 5 Configuration (ADD THIS ENTIRE DICTIONARY)
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', '|', 'undo', 'redo'],
        # 'height': '200px', # Optional: Set editor height
        # 'width': '100%',   # Optional: Set editor width
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft', 'imageStyle:full', 'imageStyle:alignRight'],
            'styles': ['full', 'alignLeft', 'alignRight']
        },
        'theme': 'lark', # 'lark' is the default, can be 'balloon', 'classic', 'document', 'inline'
    },
    'extends': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', '|', 'undo', 'redo', 'codeBlock'],
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote', 'codeBlock',
        ],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft', 'imageStyle:full', 'imageStyle:alignRight'],
            'styles': ['full', 'alignLeft', 'alignRight']
        },
        'theme': 'lark',
    },
    # Add more configurations as needed
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_ID = 1 # Required by django.contrib.sites

# Allauth specific settings
LOGIN_REDIRECT_URL = '/' # Where to redirect after login
ACCOUNT_LOGOUT_REDIRECT_URL = '/' # Where to redirect after logout
ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'

AUTHENTICATION_BACKENDS = (
    # Required for allauth to function
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)