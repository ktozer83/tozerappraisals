from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

# not sure what exactly this does, will try to figure it out
class MyAuthBackend(object):
    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwards.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            UserModel().set_password()
