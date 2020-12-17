import os
from set_config import set_config


set_config()

SECRET_KEY = "09d25e094faa6ca2336c91816dbea9563b93f7f99f6f0f4caa6cf63b88e8d3e7"

#OAuth and JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 60
CLIENT_ID_VK = os.environ.get('CLIENT_ID_VK')
CLIENT_SECRET_VK = os.environ.get('CLIENT_SECRET_VK')
CLIENT_ID_GITHUB = os.environ.get('CLIENT_ID_GITHUB')
CLIENT_SECRET_GITHUB = os.environ.get('CLIENT_SECRET_GITHUB')


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:4200",
    "http://localhost:3000",
    "http://localhost:8080",
]


API_V1_STR = 'api/v1'


#DB
DB_URI = os.environ.get('DB_URI')
APPS_MODELS = ['src.app.records.models',
               'src.app.users.models',
               'aerich.models']