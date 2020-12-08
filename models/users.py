from tortoise import Model, fields
import settings


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.TextField()
    email = fields.CharField(max_length=100, unique=True)
    hashed_password = fields.CharField(max_length=50)
    activated = fields.BooleanField(default=False)

    def check_password(self, password: str) -> bool:
        return settings.pwd_context.verify(password, self.hashed_password)

    @classmethod
    async def create_user(cls, username, email, password, activated=False) -> 'User':
        user = cls(username=username, email=email)
        if activated:
            user.activated = activated
        user.set_password(password)
        await user.save()
        return user

    def set_password(self, password: str):
        self.hashed_password = settings.pwd_context.hash(password)