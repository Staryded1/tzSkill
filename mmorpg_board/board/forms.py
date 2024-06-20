from django import forms
from .models import Ad, Reply, CustomUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from ckeditor.widgets import CKEditorWidget

class AdForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = Ad
        fields = ['title', 'description', 'category', 'image', 'video']
        labels = {
            'title': 'Заголовок',
            'description': 'Описание',
            'category': 'Категория',
            'image': 'Изображение',
            'video': 'Видео'
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']
        labels = {
            'content': 'Содержание'
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Электронная почта')

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'Имя пользователя',
            'email': 'Электронная почта',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля'
        }

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Электронная почта / Имя пользователя')

class EmailVerificationForm(forms.Form):
    code = forms.CharField(max_length=6, label='Код подтверждения')