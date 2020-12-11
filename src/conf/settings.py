import os


SECRET_KEY = "09d25e094faa6ca2336c91816dbea9563b93f7f99f6f0f4caa6cf63b88e8d3e7"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


API_V1_STR = 'api/v1'


APPS_MODELS = ['src.app.records.models',
               'src.app.users.models']