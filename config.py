import os

WTF_CSRF_ENABLED = False
SECRET_KEY = os.getenv('SECRET_KEY', 'testing_key')
