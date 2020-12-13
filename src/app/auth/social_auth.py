from authlib.integrations.starlette_client import OAuth

from src.conf import settings


oauth = OAuth()

oauth.register(
    name='vk',
    client_id=settings.CLIENT_ID_VK,
    client_secret=settings.CLIENT_SECRET_VK,
    authorize_url='https://oauth.vk.com/authorize',
    access_token_url='https://oauth.vk.com/access_token',
)
oauth.register(
    name='github',
    client_id=settings.CLIENT_ID_GITHUB,
    client_secret=settings.CLIENT_SECRET_GITHUB,
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    client_kwargs={'scope': 'read:user, user:email'}
)