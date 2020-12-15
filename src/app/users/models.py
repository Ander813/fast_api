from passlib.context import CryptContext
from tortoise import Model, fields
from src.app.base import utils, secrets


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=100, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    hashed_password = fields.CharField(max_length=50)
    activated = fields.BooleanField(default=False)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    @classmethod
    async def create_user(cls, username, email, password, activated=False) -> 'User':
        user = cls(username=username, email=email)
        if activated:
            user.activated = activated
        user.set_password(password)
        await user.save()
        return user

    def set_password(self, password: str) -> None:
        self.hashed_password = pwd_context.hash(password)

    def set_unusable_password(self, unusable_prefix: str = secrets.UNUSABLE_PASSWORD_PREFIX) -> None:
        self.hashed_password = self._generate_unusable_password(unusable_prefix=unusable_prefix)

    def _generate_unusable_password(self, unusable_prefix: str):
        return unusable_prefix + self._generate_unusable_suffix()

    def _generate_unusable_suffix(self,
                                  unusable_suffix_len=40,
                                  signs='abcdefghijklmnopqrstuvwxyz'
                                        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                                        '1234567890') -> str:
        return ''.join([utils.random_sign(signs) for _ in range(unusable_suffix_len)])

    def if_password_usable(self):
        if self.hashed_password.startswith(secrets.UNUSABLE_PASSWORD_PREFIX):
            return False
        return True
