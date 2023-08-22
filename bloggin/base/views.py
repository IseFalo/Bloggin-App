from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from .models import *
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
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
        return render(request, 'register1.html')
    
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
        return render(request, 'login1.html')
    
def home(request):
    current_user=request.GET.get('user')
    logged_in_user = request.user.username
    profile = Profile.objects.get(username=request.user)
    posts=Post.objects.all()
    context={'posts':posts, 'profile':profile}
    return render(request, 'feed.html', context)

def settings(request):
    user_profile=Profile.objects.get(username=request.user)
    if request.method == 'POST':
        if request.FILES.get('image') == None:
            blogname = request.POST['username']
            image = user_profile.profile_img
            bio = request.POST['bio']
            phone_no=request.POST['phone-no']

            
            
            if User.objects.filter(username=blogname).exists() and blogname != request.user.username:
                messages.info(request, "Blog Name Taken")
                return redirect('settings')
            else:
                user = User.objects.get(username=request.user.username)
                user.username = blogname
                user.save()

                user_profile.profile_img = image
                user_profile.bio = bio
                user_profile.phone_no = phone_no
                if phone_no is not None:
                    try:
                        phone_no = int(phone_no)
                    except ValueError:
                        phone_no = None
                user_profile.phone_no = phone_no
                user_profile.save()

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

                user_profile.profile_img = image
                user_profile.bio = bio
                if phone_no is not None:
                    try:
                        phone_no = int(phone_no)
                    except ValueError:
                        phone_no = None
                user_profile.phone_no = phone_no
                user_profile.save()
            
        return redirect('settings')
    return render(request, 'settings.html', {'user_profile': user_profile})

def create_post(request):
    if request.method == 'POST':
        author = request.user
        title=request.POST['post-title']
        post_cover=request.FILES.get('post-cover-image')
        post_text=request.POST['post-text']

        new_post = Post.objects.create(author=author, title=title, content=post_text, post_cover=post_cover)
        new_post.save()
        return redirect('/')
    else:
        return redirect('/')
    
def post_detail(request, pk):
    post=Post.objects.get(id=pk)
    post.read.add(request.user)
    if request.method == 'POST':
        post=Post.objects.get(id=pk)
        author = request.user
        comment = request.POST['comment']

        new_comment = Comment.objects.create(author=author, text=comment, post=post)
        new_comment.save()
        return redirect('post-detail', pk=pk)
    context={'post':post, 'profile':profile}
    return render(request, 'post-detail.html', context)

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
    user_profile = Profile.objects.get(username=user_object)
    user_posts = Post.objects.filter(author=user_object)
    top_pick_posts = user_profile.top_picks.filter(is_top_pick=True).order_by('-top_pick_selected_at')[:3]


    context = {
        'top_pick_posts':top_pick_posts,
        'user_profile': user_profile,
        'user_posts': user_posts,
    }

    return render(request, 'profile-page.html', context)


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