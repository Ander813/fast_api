import os
import dotenv


DEBUG = True


if DEBUG:
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    dotenv.load_dotenv(dotenv_path)


PROJECT_NAME = os.environ.get("PROJECT_NAME")
SERVER_HOST = os.environ.get("SERVER_HOST")


SECRET_KEY = "09d25e094faa6ca2336c91816dbea9563b93f7f99f6f0f4caa6cf63b88e8d3e7"

# OAuth and JWT
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # Minutes hours days
CLIENT_ID_VK = os.environ.get("CLIENT_ID_VK")
CLIENT_SECRET_VK = os.environ.get("CLIENT_SECRET_VK")
CLIENT_ID_GITHUB = os.environ.get("CLIENT_ID_GITHUB")
CLIENT_SECRET_GITHUB = os.environ.get("CLIENT_SECRET_GITHUB")


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:4200",
    "http://localhost:3000",
    "http://localhost:8080",
]


API_V1_STR = "api/v1"


# DB
DB_URI = os.environ.get("DB_URI")
APPS_MODELS = ["src.app.records.models", "src.app.users.models", "aerich.models"]

# EMAIL BACKEND
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = os.environ.get("SMTP_PORT")
SMTP_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_FROM_NAME = os.environ.get("EMAIL_FROM_EMAIL")
EMAIL_FROM_EMAIL = os.environ.get("EMAIL_FROM_EMAIL")

EMAILS_ENABLED = SMTP_HOST and SMTP_PORT and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD

EMAIL_TEMPLATES_DIR = "src/templates/email-templates"
EMAIL_CONFIRM_EXPIRE = 60 * 60 * 24 * 7  # sec min hour day
PASSWORD_RESET_EXPIRE = 60 * 60 * 24 * 7  # sec min hour day

# REDIS
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PASSWORD = None
REDIS_DB = None
