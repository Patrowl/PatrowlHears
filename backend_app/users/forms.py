from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class CustUserCreationForm(UserCreationForm):

    class Meta:
        model = get_user_model()
        fields = ('username', 'password1', 'password2', 'email')
