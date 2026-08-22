import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-smart-campus-vue3-dev-key-18367'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'rest_framework',
    'corsheaders',
    'auth_app',
    'system_app',
    'academic_app',
    'resource_app',
    'finance_app',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'campus_server.middleware.TokenAuthMiddleware',
]

ROOT_URLCONF = 'campus_server.urls'
WSGI_APPLICATION = 'campus_server.wsgi.application'

# 多库配置：5库
DATABASES = {
    'default': {  # campus_system 默认库
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'campus_system',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    },
    'academic': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'campus_academic',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    },
    'resource': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'campus_resource',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    },
    'finance': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'campus_finance',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    },
    'health': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'campus_health',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    },
}

DATABASE_ROUTERS = ['campus_server.db_router.CampusRouter']

# JWT
JWT_SECRET = SECRET_KEY
JWT_ALGORITHM = 'HS256'
JWT_EXPIRE_DAYS = 7

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_TZ = False
USE_I18N = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = ['*']
CORS_ALLOW_METHODS = ['*']

# 白名单（无需 token）
WHITE_LIST = [
    '/userAuth/login',
    '/memberAuth/login',
    '/dictData/type/',
    '/banner/loadBanner',
    '/doc/',
]

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'UNAUTHENTICATED_USER': None,
}
