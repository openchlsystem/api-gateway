DATABASES = {
    'default': {
        'NAME': 'apidb',
        'ENGINE': 'django.db.backends.postgresql_psycopg2', #'django.db.backends.postgresql',
        'USER': 'apiuser',
        'PASSWORD': 'apipassword',
        'PORT':'5433'
    },
    'defaultsqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}
TIME_ZONE = 'Africa/Nairobi' 
STATIC_ROOT = "/var/www/html/static/"

MEDIA_ROOT = "/var/www/html/static/media/"
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/auth/login/'
LOGIN_URL = '/auth/login/'
AUTH_USER_MODEL = 'users.User'
HELPLINE_BASE = "https://openchs.bitz-itc.com/helpline/api/"
HELPLINE_TOKEN = "dGVzdDpwQHNzdzByZA=="


