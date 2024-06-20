import random
import string
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.http import HttpResponse
from .models import Ad, Reply, CustomUser, EmailVerificationCode, Category
from .forms import AdForm, ReplyForm, CustomUserCreationForm, CustomAuthenticationForm
from .tasks import send_verification_email_task
from celery import shared_task

def generate_verification_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            code = generate_verification_code()
            EmailVerificationCode.objects.create(user=user, code=code)
            send_verification_email_task.delay(user.id, code)
            return redirect('verify_email', user_id=user.id)
    else:
        form = CustomUserCreationForm()
    return render(request, 'board/signup.html', {'form': form})

def verify_email(request, user_id):
    if request.method == 'POST':
        confirmation_code = request.POST.get('confirmation_code')
        if not confirmation_code:
            return HttpResponse('Confirmation code is required!', status=400)
        try:
            user = CustomUser.objects.get(pk=user_id)
            email_verification_code = EmailVerificationCode.objects.get(user=user)
            if email_verification_code.code == confirmation_code:
                user.is_active = True
                user.save()
                email_verification_code.delete()
                return redirect('login')
            else:
                return HttpResponse('Invalid confirmation code!', status=400)
        except CustomUser.DoesNotExist:
            return HttpResponse('User does not exist!', status=404)
        except EmailVerificationCode.DoesNotExist:
            return HttpResponse('Verification code not found!', status=404)
        except Exception as e:
            return HttpResponse(f'Error verifying email: {str(e)}', status=500)
    else:
        return render(request, 'board/verify_email.html', {'user_id': user_id})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'board/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

def index(request):
    ads = Ad.objects.all()
    return render(request, 'board/index.html', {'ads': ads})

def ad_detail(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    replies = ad.replies.all()
    return render(request, 'board/ad_detail.html', {'ad': ad, 'replies': replies})

def ad_create(request):
    if request.method == 'POST':
        form = AdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.author = request.user
            ad.save()
            return redirect('index')
    else:
        form = AdForm()
    return render(request, 'board/ad_form.html', {'form': form})

def ad_edit(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            form.save()
            return redirect('ad_detail', pk=ad.pk)
    else:
        form = AdForm(instance=ad)
    return render(request, 'board/ad_form.html', {'form': form})

def reply_create(request, ad_pk):
    ad = get_object_or_404(Ad, pk=ad_pk)
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.ad = ad
            reply.author = request.user
            reply.save()
            send_mail(
                'New reply to your ad',
                f'You have a new reply to your ad "{ad.title}".',
                'from@example.com',
                [ad.author.email],
            )
            return redirect('ad_detail', pk=ad_pk)
    else:
        form = ReplyForm()
    return render(request, 'board/reply_form.html', {'form': form, 'ad': ad})

@login_required
def profile_view(request):
    user_ads = Ad.objects.filter(author=request.user)
    return render(request, 'board/profile.html', {'user_ads': user_ads})

@login_required
def manage_replies(request):
    user_ads = Ad.objects.filter(author=request.user)
    replies = Reply.objects.filter(ad__in=user_ads).select_related('ad')
    if 'ad' in request.GET:
        ad_id = request.GET['ad']
        replies = replies.filter(ad_id=ad_id)
    return render(request, 'board/manage_replies.html', {'replies': replies})

@login_required
def accept_reply(request, reply_id):
    reply = get_object_or_404(Reply, pk=reply_id, ad__author=request.user)
    reply.is_accepted = True
    reply.save()
    send_mail(
        'Your reply has been accepted',
        f'Your reply to the ad "{reply.ad.title}" has been accepted.',
        'from@example.com',
        [reply.author.email],
    )
    return redirect('manage_replies')

@login_required
def delete_reply(request, reply_id):
    reply = get_object_or_404(Reply, pk=reply_id, ad__author=request.user)
    reply.delete()
    return redirect('manage_replies')

@receiver(post_save, sender=Reply)
def send_reply_notification(sender, instance, created, **kwargs):
    if created:
        ad = instance.ad
        send_mail(
            'New reply to your ad',
            f'You have a new reply to your ad "{ad.title}".',
            'from@example.com',
            [ad.author.email],
        )

@receiver(post_save, sender=Reply)
def send_reply_accept_notification(sender, instance, **kwargs):
    if instance.is_accepted:
        send_mail(
            'Your reply has been accepted',
            f'Your reply to the ad "{instance.ad.title}" has been accepted.',
            'from@example.com',
            [instance.author.email],
            fail_silently=False,
        )

@shared_task
def send_newsletter(subject, message):
    recipients = CustomUser.objects.values_list('email', flat=True)
    send_mail(
        subject,
        message,
        'from@example.com',
        recipients,
        fail_silently=False,
    )