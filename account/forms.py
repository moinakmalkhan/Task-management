from django import forms
from django.forms import ValidationError
from django.contrib.auth import get_user_model, authenticate, login
from .models import UserProfile
from .utils import is_email


class BaseFrom(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(BaseFrom, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class SignUpForm(BaseFrom):
    first_name = forms.CharField(max_length=100, required=True, label="First name")
    last_name = forms.CharField(max_length=100, required=True, label="Last name")
    email = forms.EmailField(max_length=254, required=True, label="Email")
    phone = forms.CharField(max_length=30, required=True, label="Phone")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Password")
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True, label="Confirm password")

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        phone = cleaned_data.get('phone')
        password_confirm = cleaned_data.get('password_confirm')
        User = get_user_model()
        if password != password_confirm:
            raise ValidationError({'password': 'Passwords do not match.'})

        if User.objects.filter(email=email).exists():
            raise ValidationError({'email': 'Email already exists.'})

        if User.objects.filter(user_profile__phone=phone).exists():
            raise ValidationError({'phone': 'Phone already exists.'})
        return cleaned_data

    def save(self):
        data = self.cleaned_data
        user = get_user_model().objects.create_user(
            username=data['email'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        UserProfile.objects.create(
            user=user,
            phone=data['phone']
        )
        self.cleaned_data['user'] = user
        return user

    def login(self, user=None):
        user = user or self.cleaned_data.get('user')
        login(self.request, user)
        return user


class LoginFrom(BaseFrom):
    email = forms.CharField(max_length=254, required=True, label="Email or Phone")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Password")

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        User = get_user_model()
        if not is_email(email):
            user = User.objects.filter(user_profile__phone=email).first()
            email = getattr(user, 'email', None)
        user = authenticate(self.request, username=email, password=password)
        if user is None:
            raise ValidationError({'email': 'Incorrect email or password.'})
        cleaned_data['user'] = user
        return cleaned_data

    def login(self, user=None):
        user = user or self.cleaned_data.get('user')
        if user:
            login(self.request, user)
            return user
