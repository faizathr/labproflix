from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class RegisterForm(UserCreationForm):
    usable_password = None
    class Meta:
        model = get_user_model()
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]