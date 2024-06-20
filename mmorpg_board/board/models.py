from django.contrib.auth.models import AbstractUser
from django.db import models
from ckeditor.fields import RichTextField

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

class EmailVerificationCode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Ad(models.Model):
    title = models.CharField(max_length=100)
    description = RichTextField()  # Используйте RichTextField из ckeditor
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='ads/images/', blank=True, null=True)
    video = models.FileField(upload_to='ads/videos/', blank=True, null=True)

    def __str__(self):
        return self.title

class Reply(models.Model):
    ad = models.ForeignKey(Ad, related_name='replies', on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Reply to {self.ad.title} by {self.author.username}'
    
