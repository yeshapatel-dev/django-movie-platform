from django import forms # type: ignore
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm # type: ignore
from .models import Users

class RegistrationForm(UserCreationForm):
    class Meta:
        model = Users
        fields = ('username', 'user_role')

class SigninForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))