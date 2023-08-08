from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
# Create your views here.
def settings(request):
    return render(request, 'settings.html')
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
    posts=Post.objects.all()
    context={'posts':posts}
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
    if request.method == 'POST':
        post=Post.objects.get(id=pk)
        author = request.user
        comment = request.POST['comment']

        new_comment = Comment.objects.create(author=author, text=comment, post=post)
        new_comment.save()
        return redirect('post-detail', pk=pk)
    context={'post':post}
    return render(request, 'post-detail.html', context)



    