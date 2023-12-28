from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from .models import *
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from random import sample
import random
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from .models import Notification as note
# Create your views here.

def register(request):
    if request.method == 'POST':
        blogname = request.POST['blog-name']
        email = request.POST['email']
        password1=request.POST['password1']
        password2=request.POST['password2']


        if not blogname:
            messages.error(request, "Blog name is required.")
            return redirect('register')

        if not email:
            messages.error(request, "Email is required.")
            return redirect('register')
        if not password1:
            messages.error(request, "Enter First Password")
            return redirect('register')
        if not password2:
            messages.error(request, "Enter Second Password")
            return redirect('register')

        if password1 == password2:
            if User.objects.filter(username=blogname).exists():
                messages.info(request, "Username Taken")
                return redirect('register')
            else:
                user=User.objects.create_user(username=blogname, email=email, password=password1)
                user.save()

                user_login=auth.authenticate(username=blogname, password=password1)
                auth.login(request, user_login)

                user_model = User.objects.get(username=blogname, email=email)
                new_profile=Profile.objects.create(username=user_model, email=email)
                new_profile.save()
                return redirect('settings')


    else:
        return render(request, 'base/register1.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['blogname']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('login')

    else:
        return render(request, 'base/login1.html')

def logoutUser(request):
    logout(request)
    return redirect("login")
@login_required
def home(request):
    # current_user=request.GET.get('user')
    current_user = request.user


    profile = Profile.objects.get(username=request.user)
    users_already_following = profile.username.following.all()
    suggested_users = Profile.objects.exclude(id=profile.id).exclude(id__in=users_already_following).order_by('?')[:3]
    posts=Post.objects.all()
    context={'posts':posts, 'profile':profile, 'suggested_users':suggested_users}
    return render(request, 'base/feed.html', context)

def settings(request):
    profile=Profile.objects.get(username=request.user)
    if request.method == 'POST':
        if request.FILES.get('image') == None:
            blogname = request.POST['username']
            image = profile.profile_img
            bio = request.POST['bio']
            phone_no=request.POST['phone-no']



            if User.objects.filter(username=blogname).exists() and blogname != request.user.username:
                messages.info(request, "Blog Name Taken")
                return redirect('settings')
            else:
                user = User.objects.get(username=request.user.username)
                user.username = blogname
                user.save()

                profile.profile_img = image
                profile.bio = bio
                profile.phone_no = phone_no
                if phone_no is not None:
                    try:
                        phone_no = int(phone_no)
                    except ValueError:
                        phone_no = None
                profile.phone_no = phone_no
                profile.save()

        if request.FILES.get('image') != None:
            blogname = request.POST['username']
            image = request.FILES.get('image')
            bio = request.POST.get['bio']
            phone_no = request.POST['phone-no']

            if User.objects.filter(username=blogname).exists() and blogname != request.user.username:
                messages.info(request, "Blog Name Taken")
                return redirect('settings')
            else:
                user = User.objects.get(username=request.user.username)
                user.username = blogname
                user.save()

                profile.profile_img = image
                profile.bio = bio
                if phone_no is not None:
                    try:
                        phone_no = int(phone_no)
                    except ValueError:
                        phone_no = None
                profile.phone_no = phone_no
                profile.save()

        return redirect('settings')
    return render(request, 'base/settings.html', {'profile': profile})

def create_post(request):
    if request.method == 'POST':
        author = request.user
        title=request.POST['post-title']
        post_cover=request.FILES.get('post-cover-image')
        post_text=request.POST['post-text']
        profile=Profile.objects.get(username=author)
        new_post = Post.objects.create(author=author, title=title, content=post_text, post_cover=post_cover)
        new_post.save()
        
        return redirect('/')
    else:
        return redirect('/')

def post_detail(request, pk):
    post=Post.objects.get(id=pk)

    post.read.add(request.user)
    user = request.user
    profile= Profile.objects.get(username=user)
    if request.method == 'POST':
        post=Post.objects.get(id=pk)
        author = request.user
        comment = request.POST['comment']

        new_comment = Comment.objects.create(author=author, text=comment, post=post)
        new_comment.save()
        return redirect('post-detail', pk=pk)
    context={'post':post, 'profile':profile}
    return render(request, 'base/post-detail.html', context)

def delete_post(request, pk):
    post=Post.objects.get(id=pk)
    post.delete()
    return redirect('/')

def edit_post(request, pk):
    post = Post.objects.get(id=pk)
    if request.method == 'POST':
        post.title = request.POST['post-title']
        new_cover = request.FILES.get('post-cover-image')
        if new_cover:
            post.post_cover = new_cover
        post.content = request.POST['post-text']
        post.edited = True
        post.save()
        return redirect('post-detail', pk=pk)

def profile(request, pk):
    user_object=get_object_or_404(User, id=pk)
    profile = Profile.objects.get(username=user_object)
    user_posts = Post.objects.filter(author=user_object)
    top_pick_posts = profile.top_picks.filter(is_top_pick=True).order_by('-top_pick_selected_at')[:3]
    suggested_posts = sample(list(user_posts), min(3, len(user_posts)))


    context = {
        'top_pick_posts':top_pick_posts,
        'profile': profile,
        'user_posts': user_posts,
        'suggested_posts':suggested_posts,
    }

    return render(request, 'base/profile-page.html', context)


def add_to_picks(request, pk):
    user_profile = Profile.objects.get(username=request.user)
    post = get_object_or_404(Post, id=pk)
    post.is_top_pick = True
    user_profile.top_picks.add(post)
    post.top_pick_selected_at = timezone.now()  # Update timestamp
    post.save()
    return HttpResponse(status=204)


def remove_from_picks(request, pk):
    post = get_object_or_404(Post, id=pk)
    if post.is_top_pick:
        post.is_top_pick = False
        post.top_pick_selected_at = None
        post.save()
    return HttpResponse(status=204)

def follow(request, username):
    user = User.objects.get(username=username)
    user_profile = Profile.objects.get(username=user)
    user_profile.followers.add(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
def unfollow(request, username):
    user = User.objects.get(username=username)
    user_profile = Profile.objects.get(username=user)
    user_profile.followers.remove(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def format_time_difference(created_at):
    now = timezone.now()
    time_difference = now - created_at

    # If the notification was created less than 2 minutes ago
    if time_difference.total_seconds() < 120:
        return "Just Now"

    # If the notification was created less than 1 hour ago
    elif time_difference.total_seconds() < 3600:
        minutes_ago = int(time_difference.total_seconds() / 60)
        return f"{minutes_ago} {'minute' if minutes_ago == 1 else 'minutes'} ago"

    # If the notification was created less than 24 hours ago
    elif time_difference.total_seconds() < 86400:
        hours_ago = int(time_difference.total_seconds() / 3600)
        return f"{hours_ago} {'hour' if hours_ago == 1 else 'hours'} ago"

    # If the notification was created less than 48 hours ago (but more than 24 hours ago)
    elif time_difference.total_seconds() < 172800:
        return "Yesterday"

    # If the notification was created less than 1 week ago (but more than 48 hours ago)
    elif time_difference.total_seconds() < 604800:
        days_ago = int(time_difference.total_seconds() / 86400)
        return f"{days_ago} {'day' if days_ago == 1 else 'days'} ago"

    # For any other case, return the formatted date and time
    else:
        return created_at.strftime("%Y-%m-%d %H:%M:%S")
    
def get_notifications(request):
    user = request.user 
    notifications = note.objects.filter(user=user).order_by('-created_at')[:10]
    data = [
        {'message': notification.message, 
         'post.id':notification.post.id,
         'author': notification.comment.author.username,
         'created_at_formatted': format_time_difference(notification.created_at),
         } 
         for notification in notifications
         ]
    return JsonResponse(data, safe=False)
