from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ad/<int:pk>/', views.ad_detail, name='ad_detail'),
    path('ad/new/', views.ad_create, name='ad_create'),
    path('ad/<int:pk>/edit/', views.ad_edit, name='ad_edit'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('ad/<int:pk>/reply/', views.reply_create, name='reply_create'),
    path('profile/', views.profile_view, name='profile'),
    path('signup/', views.signup, name='signup'),
    path('verify_email/<int:user_id>/', views.verify_email, name='verify_email'),
    path('', views.index, name='index'),
]
