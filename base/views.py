import imgkit
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from .models import *
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from random import sample
from datetime import datetime
from django.views.generic import ListView ,DetailView
from django.utils.decorators import method_decorator
import re
from django.db.models import Count,Q
from datetime import date
from django.views import View
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.core import paginator
from django.core.paginator import Paginator
from .models import Notification as note
from django.template.loader import render_to_string
from .forms import PostForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
import os
# Create your views here.


POST_COUNT_PER_PAGE = 9
@csrf_exempt
def upload_editor_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_name = default_storage.save(uploaded_file.name, uploaded_file)
        file_url = default_storage.url(file_name)
        return JsonResponse({'location': file_url})
    return JsonResponse({'error': 'No file uploaded'}, status=400)

def organization_top_posts_view(request, organization_id):
    organization = get_object_or_404(Organization, id=organization_id)
    top_three_posts = Post.objects.filter(organization=organization,) \
                                  .annotate(read_count=Count('read')) \
                                  .order_by('-read_count')[:3]
    
    context = {
        'organization': organization,
        'top_three_posts': top_three_posts,
    }
    
    return render(request, 'organization_top_posts.html', context)


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

def logoutUser(request):
    logout(request)
    return redirect("login")

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })
# def get_read_time(words):
#     """
#     Calculates the estimated reading time for the post's content.
#     """
#     word_count = len(words)
#     read_time_in_seconds = word_count*0.5
#     if read_time_in_seconds<60:
#         return round(read_time_in_seconds)
#     else:
#         read_time_in_minutes = read_time_in_seconds/60
#         return round(read_time_in_minutes)


class HomeView(ListView):
    model = Post
    context_object_name = 'posts'
    paginate_by = 10



    def get_template_names(self):
        if self.request.htmx:
            return "feed_posts.html"
        return "feed.html"
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return Post.objects.filter(status='published').order_by("-updated")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user

        profile = Profile.objects.get(username=current_user)
        users_already_following = profile.username.following.all()
        suggested_users = Profile.objects.exclude(id=profile.id).exclude(id__in=users_already_following) \
                                         .annotate(post_count=Count('username__post', filter=Q(username__post__status='published'))) \
                                         .order_by('?')[:5]
        form = PostForm(self.request.POST or None)
        

        page_obj = context['page_obj']
        for post in page_obj:
            content_without_images_or_empty_paragraphs = re.sub(r'(<img[^>]*>)|(<p>&nbsp;</p>)', '', post.content)
            post.content_without_images_or_empty_paragraphs = content_without_images_or_empty_paragraphs

        context.update({
            'profile': profile,
            'suggested_users': suggested_users,
            
            'form': form,
        })
        return context

# @login_required
# def home(request):
#     # current_user=request.GET.get('user')
#     current_user = request.user

#     profile = Profile.objects.get(username=request.user)
#     users_already_following = profile.username.following.all()
#     suggested_users = Profile.objects.exclude(id=profile.id).exclude(id__in=users_already_following).order_by('?')[:3]
#     posts=Post.objects.filter(status='published').order_by("-updated")
#     paginator = Paginator(posts, 10)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     if page_number:
#         if int(page_number) <= paginator.num_pages:

#             obj_list = paginator.get_page(page_number)

#             # obj_list = obj_list.object_list.values()
#             data = []
#             for obj in obj_list:
#                 content_without_images_or_empty_paragraphs = re.sub(r'(<img[^>]*>)|(<p>&nbsp;</p>)', '', obj.content)
#                 item = {
#                     "id": obj.id,
#                     "title": obj.title,
#                     "cover": obj.post_cover.url if obj.post_cover else None,
#                     "content": content_without_images_or_empty_paragraphs,
#                     "author": obj.author.username,
#                     "liked": True if request.user in obj.likes.all() else False,
#                     "count": obj.like_count,
#                     "category": obj.category.name if obj.category else None,  
#                     "created":obj.created,
#                     "get_read_time_in_minutes": obj.get_read_time_in_minutes(),
#                 }
#                 data.append(item)
#             return JsonResponse(data, status=200, safe=False)

#     form = PostForm(request.POST or None)
#     today = date.today()
#     top_read_posts = Post.objects.filter(read__in=[current_user], status='published') \
#                                   .annotate(read_count=Count('read')) \
#                                   .order_by('-read_count')[:6]
#     for post in page_obj:
#         content_without_images_or_empty_paragraphs = re.sub(r'(<img[^>]*>)|(<p>&nbsp;</p>)', '', post.content)
#         post.content_without_images_or_empty_paragraphs = content_without_images_or_empty_paragraphs
#     context={'posts':posts, 'profile':profile, 'suggested_users':suggested_users, 'top_read_posts':top_read_posts, 'form':form, 'page_obj': page_obj}
    
#     return render(request, 'feed.html', context)




def like_post(request, pk):
    post = get_object_or_404(Post, id=pk)
    user =request.user
    like = False
    if request.method == 'POST':
        post_id = request.POST['post_id']
        get_post = get_object_or_404(Post, id=post_id)
        if user in get_post.likes.all():
            get_post.likes.remove(user)
            like = False
        else:
            get_post.likes.add(user)
            like=True
        data={
            "liked":like,
            "likes_count":get_post.likes.all().count(),

        }
        return JsonResponse(data, safe=False)
    return redirect("/")
    
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
            bio = request.POST.get('bio')
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
    return render(request, 'settings.html', {'profile': profile})


def search_results_view(request):
    query = request.GET.get('search', '')
    if query:
        results = Post.objects.filter(title__contains = query)
    else:
        results = []
    context = {'results':results}
    return render(request, 'search-results.html', context)


# def search_view(request):
    
#     profile = Profile.objects.get(username=request.user)
#     if request.method == 'POST':
#         query = request.POST['query']
#         results = Post.objects.filter(title__contains=query)

#         context = {
#             'query': query,
#             'results': results,
#             'profile':profile,
#         }

#         return render(request, 'search-results.html', context)
#     else:
#         return render(request, 'search-results.html')



def create_post(request):
    profile = Profile.objects.get(username=request.user)  # Ensure you're using the correct field for filtering profile
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        
        if form.is_valid():
            author = request.user
            title = form.cleaned_data['title']
            post_cover = form.cleaned_data['post_cover']
            post_text = form.cleaned_data['content']
            category = form.cleaned_data['category']
            new_post = Post.objects.create(
                author=author, 
                title=title, 
                content=post_text, 
                post_cover=post_cover,
                category=category
            )
            
            print("POST data:", request.POST)

            if 'published' in request.POST:
                new_post.status = 'published'
                redirect_url = '/'
                # Redirect to the home page or any other appropriate page

            elif 'save_draft' in request.POST:
                new_post.status = 'draft'
                redirect_url = 'drafts'
                # Redirect to the drafts list page

            else:
                redirect_url = '/'
                  
            
            new_post.save()
            
            return redirect(redirect_url)
        else:
            messages.error(request, "Please correct the errors below.")
            return render(request, 'create-post.html', {'form': form, 'profile': profile})
    else:
        form = PostForm()
        return render(request, 'create-post.html', {'form': form, 'profile': profile}) 
    
def drafts_list(request):
    drafts = Post.objects.filter(status='draft', author=request.user)
    profile = Profile.objects.get(username=request.user)
    return render(request, 'drafts.html', {'drafts': drafts, 'profile':profile})
def publish_post(request, pk):
    post = Post.objects.get(id=pk)
    form = PostForm(instance=post)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post.status = "published"
            form.save()
            return redirect('/')
    context = {'form':form, 'post':post}
    return render(request, 'create-post.html', context)

def post_detail(request, pk):
    post=Post.objects.get(id=pk)
    all_posts=Post.objects.all()
    post.read.add(request.user)
    user = request.user
    profile= Profile.objects.get(username=user)
    suggested_posts = sample(list(all_posts), min(5, len(all_posts)))
    author = post.author
    author_profile = Profile.objects.get(username=author)
    author_followers_count = author_profile.followers.count()
    comment_count = post.comment_set.count()
    replies_count = sum(comment.replies.count() for comment in post.comment_set.all())
    total_count = comment_count + replies_count
    context={'post':post, 'profile':profile, 'suggested_posts':suggested_posts, 'total_count':total_count, 'author_followers_count': author_followers_count}
    return render(request, 'post-detail.html', context)
def post_image(request, pk):
    post = Post.objects.get(id=pk)
    post_cover_url = request.build_absolute_uri(post.post_cover.url)
    html = render_to_string('post_image.html', {'post': post, 'post_cover_url': post_cover_url,})
    options = {
        'format': 'png',
        'encoding': 'UTF-8',
        'enable-local-file-access': '',
    }
    wkhtmltoimage_path = r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltoimage.exe'
    config = imgkit.config(wkhtmltoimage=wkhtmltoimage_path)
    img = imgkit.from_string(html, False, options=options, config=config)
    response = HttpResponse(img, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="{post.title}.png"'
    return response
def comment_sent(request, pk):
    if request.method == 'POST':
        post=Post.objects.get(id=pk)
        author = request.user
        comment = request.POST['comment']

        new_comment = Comment.objects.create(author=author, text=comment, post=post)
        new_comment.save()
        context={'post':post}
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    

def delete_post(request, pk):
    post=Post.objects.get(id=pk)
    post.delete()
    return redirect('/')

def edit_post(request, pk):
    profile = Profile.objects.get(username=request.user)
    post = get_object_or_404(Post, id=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        
        if form.is_valid():
            form.save()
            post.edited = True
            post.save()
            return redirect('post-detail', pk=pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PostForm(instance=post)
    
    return render(request, 'edit-post.html', {'form': form, 'post': post, 'profile':profile})
def save_post(request, pk):
    user_profile=Profile.objects.get(username=request.user)
    post = Post.objects.get(id=pk)
    user_profile.saved_posts.add(post)
    user_profile.save()
    return redirect('/')
def saved_posts_list(request):
    profile = Profile.objects.get(username=request.user)
    saved_posts = profile.saved_posts.all()
    context = {'saved_posts': saved_posts, 'profile':profile}
    return render(request, 'saved_posts_list.html', context)
def profile(request, username):
    user_object = get_object_or_404(User, username=username)
    profile = Profile.objects.get(username=request.user)
    user_posts = Post.objects.filter(status='published', author=user_object)
    user_posts_count = user_posts.count()

    # Process each post
    for post in user_posts:
        content_without_images_or_empty_paragraphs = re.sub(r'(<img[^>]*>)|(<p>&nbsp;</p>)', '', post.content)
        post.content_without_images_or_empty_paragraphs = content_without_images_or_empty_paragraphs
        post.comment_count = Comment.objects.filter(post=post).count()

    author_profile = Profile.objects.get(username=user_object)
    top_pick_posts = author_profile.top_picks.filter(is_top_pick=True).order_by('-top_pick_selected_at')[:3]
    top_read_posts = sorted(Post.objects.filter(author=user_object, status='published'), key=lambda x: x.read_count, reverse=True)[:5]
    suggested_posts = sample(list(user_posts), min(5, len(user_posts)))
    user_series = Series.objects.filter(creator=user_object)
    saved_posts = profile.saved_posts.all()
    created_organizations = Organization.objects.filter(creator=request.user)

    context = {
        'top_pick_posts': top_pick_posts,
        'profile': profile,
        'user_posts': user_posts,
        'suggested_posts': suggested_posts,
        'author_profile': author_profile,
        'user_object': user_object,
        'user_series': user_series,
        'saved_posts': saved_posts,
        'created_organizations': created_organizations,
        'top_read_posts': top_read_posts,
        'user_posts_count': user_posts_count,
    }

    template_name = "profile-page-posts.html" if request.htmx else "profile-page.html"
    return render(request, template_name, context)



class ProfilePostListView(ListView):
    model = Post
    context_object_name = 'user_posts'
    paginate_by = 10
    def get_template_names(self):
        if self.request.htmx:
            return "profile_post_list_posts.html"
        return "profile_post_list.html"
    def get_queryset(self):
        self.user_object = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(status='published', author=self.user_object)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_object = self.user_object
        profile = Profile.objects.get(username=self.request.user)
        author_profile = Profile.objects.get(username=user_object)
        top_pick_posts = author_profile.top_picks.filter(is_top_pick=True).order_by('-top_pick_selected_at')[:3]
        user_posts = Post.objects.filter(status='published', author=user_object)
        user_posts_count = user_posts.count()
        page_obj = context['page_obj']
        for post in user_posts:
            content_without_images_or_empty_paragraphs = re.sub(r'(<img[^>]*>)|(<p>&nbsp;</p>)', '', post.content)
            post.content_without_images_or_empty_paragraphs = content_without_images_or_empty_paragraphs
            post.comment_count = Comment.objects.filter(post=post).count()
        context.update({
            'user_object': user_object,
            'profile': profile,
            'author_profile': author_profile,
            'top_pick_posts': top_pick_posts,
            'user_posts_count':user_posts_count,
        })
        return context

class ProfileProductListView(ListView):
    model = Product
    context_object_name = 'user_products'
    paginate_by = 9
    def get_template_names(self):
        if self.request.htmx:
            return "profile-product-list.html"
        return "profile-product-list.html"
    def get_queryset(self):
        self.user_object = get_object_or_404(User, username=self.kwargs['username'])
        return Product.objects.filter(owner=self.user_object)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_object = self.user_object
        profile = Profile.objects.get(username=self.request.user)
        author_profile = Profile.objects.get(username=user_object)
        top_pick_posts = author_profile.top_picks.filter(is_top_pick=True).order_by('-top_pick_selected_at')[:3]
        user_posts = Post.objects.filter(status='published', author=user_object)
        user_posts_count = user_posts.count()
        context.update({
            'user_object': user_object,
            'profile': profile,
            'author_profile': author_profile,
            'top_pick_posts': top_pick_posts,
            'user_posts_count':user_posts_count,
        })
        return context

def profile_bio(request, username):
    user_object = get_object_or_404(User, username=username)
    author_profile = get_object_or_404(Profile, username=user_object)
    profile = Profile.objects.get(username=request.user)
    context = {
        'profile':profile,
        'user_object':user_object,
        'author_profile': author_profile,
    }
    return render(request, 'profile-bio.html', context)



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
def get_notifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    profile = Profile.objects.get(username=user)
    context = {
        'notifications': notifications,
        'profile':profile
    }
    return render(request, 'notifications.html', context)
# def format_time_difference(created_at):
#     now = timezone.now()
#     time_difference = now - created_at

#     # If the notification was created less than 2 minutes ago
#     if time_difference.total_seconds() < 120:
#         return "Just Now"

#     # If the notification was created less than 1 hour ago
#     elif time_difference.total_seconds() < 3600:
#         minutes_ago = int(time_difference.total_seconds() / 60)
#         return f"{minutes_ago} {'minute' if minutes_ago == 1 else 'minutes'} ago"

#     # If the notification was created less than 24 hours ago
#     elif time_difference.total_seconds() < 86400:
#         hours_ago = int(time_difference.total_seconds() / 3600)
#         return f"{hours_ago} {'hour' if hours_ago == 1 else 'hours'} ago"

#     # If the notification was created less than 48 hours ago (but more than 24 hours ago)
#     elif time_difference.total_seconds() < 172800:
#         return "Yesterday"

#     # If the notification was created less than 1 week ago (but more than 48 hours ago)
#     elif time_difference.total_seconds() < 604800:
#         days_ago = int(time_difference.total_seconds() / 86400)
#         return f"{days_ago} {'day' if days_ago == 1 else 'days'} ago"

#     # For any other case, return the formatted date and time
#     else:
#         return created_at.strftime("%Y-%m-%d %H:%M:%S")
    
# def get_notifications(request):
#     user = request.user 
#     notifications = note.objects.filter(user=user).order_by('-created_at')[:10]
#     data = [
#         {'message': notification.message, 
#          'post.id':notification.post.id,
#          'author': notification.comment.author.username,
#          'created_at_formatted': format_time_difference(notification.created_at),
#          } 
#          for notification in notifications
#          ]
#     return JsonResponse(data, safe=False)



def add_post_to_series(request, post_id):
    if request.method == 'POST':
        series_id = request.POST.get('series_id')
        series = Series.objects.get(id=series_id)
        post_to_add = Post.objects.get(id=post_id)
        post_to_add.series = series
        post_to_add.save()
        return redirect('/')
    

def create_series(request):
    user = request.user
    name=request.POST['series-name']
    selected_organization_id = request.POST.get('organization_id')
    organization = Organization.objects.get(pk=selected_organization_id)
    new_series = Series.objects.create(creator=user, name=name, organization=organization)
    new_series.save()
    return redirect('/')

def series_detail(request, pk):
  series = Series.objects.get(pk=pk)
  series_posts = Post.objects.filter(series=series, author=request.user)
  context = {'series': series, 'series_posts': series_posts}
  return render(request, 'series-detail.html', context)



# def series_list(request, username):
#     user_object=User.objects.get(username=username)
#     user_series = Series.objects.filter(creator=user_object)
#     for series in user_series:
#         post_count = series.post_set.count()
#         series.post_count = post_count
#     author_profile = Profile.objects.get(username=user_object)
#     profile = Profile.objects.get(username=request.user)
#     created_organizations=Organization.objects.filter(creator=request.user)
#     top_pick_posts = author_profile.top_picks.filter(is_top_pick=True).order_by('-top_pick_selected_at')[:3]
#     context = {'user_series':user_series, 'author_profile':author_profile, 'user_object':user_object, 'created_organizations':created_organizations, 'top_pick_posts':top_pick_posts, 'profile':profile}
#     return render(request, 'profile-series-list.html', context)



class SeriesListView(ListView):
    model = Series
    context_object_name = 'user_series'
    paginate_by = 10

    def get_template_names(self):
        if self.request.htmx:
            return "profile-series-list-items.html"
        return "profile-series-list.html"

    def get_queryset(self):
        username = self.kwargs.get('username')
        user_object = get_object_or_404(User, username=username)
        user_series = Series.objects.filter(creator=user_object)
        for series in user_series:
            series.post_count = series.post_set.count()
        return user_series

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get('username')
        user_object = get_object_or_404(User, username=username)
        author_profile = get_object_or_404(Profile, username=user_object)
        profile = get_object_or_404(Profile, username=self.request.user)
        created_organizations = Organization.objects.filter(creator=self.request.user)
        top_pick_posts = author_profile.top_picks.filter(is_top_pick=True).order_by('-top_pick_selected_at')[:3]

        context.update({
            'author_profile': author_profile,
            'user_object': user_object,
            'created_organizations': created_organizations,
            'top_pick_posts': top_pick_posts,
            'profile': profile,
        })
        return context




def create_organization_profile(request):
    if request.method == 'POST':
        org_name = request.POST['org-name']
        org_bio = request.POST['org-bio']
        new_org = Organization.objects.create(creator=request.user, name=org_name, bio=org_bio)
        new_org.members.add(request.user)
        new_org.save()
    return redirect('/')

def organization_profile_list(request, username):
    user_object=User.objects.get(username=username)
    author_profile = Profile.objects.get(username=user_object)
    user_organizations = user_object.organizations.all()
    profile = Profile.objects.get(username=request.user)
    top_pick_posts = author_profile.top_picks.filter(is_top_pick=True).order_by('-top_pick_selected_at')[:3]
    context = {'user_object':user_object, 'author_profile':author_profile, 'user_organizations':user_organizations, 'top_pick_posts':top_pick_posts, 'profile':profile}
    return render(request, 'profile-organization-list.html', context)


class OrganizationProfileView(DetailView):
    model = Organization
    context_object_name = 'organization_profile'
    template_name = 'organization-profile.html'
    pk_url_kwarg = 'pk'

    def get_template_names(self):
        if self.request.htmx:
            return ["organization-profile-posts-parts.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization_profile = self.object
        organization_posts = Post.objects.filter(organization=organization_profile)
        paginator = Paginator(organization_posts, 5)  # 5 posts per page
        page_number = self.request.GET.get('page') or 1
        page_obj = paginator.get_page(page_number)
        top_three_posts = Post.objects.filter(organization=organization_profile, status='published') \
                                  .annotate(read_count_annotated=Count('read')) \
                                  .order_by('-read_count_annotated')[:3]
        for post in page_obj:
            content_without_images_or_empty_paragraphs = re.sub(r'(<img[^>]*>)|(<p>&nbsp;</p>)', '', post.content)
            post.content_without_images_or_empty_paragraphs = content_without_images_or_empty_paragraphs

        profile = get_object_or_404(Profile, username=self.request.user)
        suggested_posts = sample(list(organization_posts), min(3, len(organization_posts)))
      

        context.update({
            'page_obj': page_obj,
            'suggested_posts': suggested_posts,
            'profile': profile,
            'top_three_posts': top_three_posts,
        })
        return context

# Organization Profile as Function based view
# def organization_profile(request, pk):
#     organization_profile = get_object_or_404(Organization, pk=pk)
#     organization_posts = Post.objects.filter(organization=organization_profile)
#     paginator = Paginator(organization_posts, 5)  # 5 posts per page
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     for post in page_obj:
#         content_without_images_or_empty_paragraphs = re.sub(r'(<img[^>]*>)|(<p>&nbsp;</p>)', '', post.content)
#         post.content_without_images_or_empty_paragraphs = content_without_images_or_empty_paragraphs

#     profile = get_object_or_404(Profile, username=request.user)
#     suggested_posts = sample(list(organization_posts), min(3, len(organization_posts)))
#     most_read_posts = Post.objects.annotate(read_count=Count('read')).order_by('-read_count')[:3]

#     context = {
#         'organization_profile': organization_profile,
#         'page_obj': page_obj,
#         'suggested_posts': suggested_posts,
#         'profile': profile,
#         'most_read_posts': most_read_posts
#     }
#     template_name = "organization-profile-posts-parts.html" if request.htmx else "organization-profile.html"
#     return render(request, template_name, context)


def organization_series(request, pk):
    organization_profile = Organization.objects.get(pk=pk)
    organization_posts = Post.objects.filter(organization=organization_profile)
    organization_series = Series.objects.filter(organization=organization_profile)
    top_three_posts = Post.objects.filter(organization=organization_profile, status='published') \
                                  .annotate(read_count_annotated=Count('read')) \
                                  .order_by('-read_count_annotated')[:3]
    profile = get_object_or_404(Profile, username=request.user)
    context = {'organization_series':organization_series, 'organization_profile':organization_profile, 'top_three_posts':top_three_posts, 'organization_posts':organization_posts, 'profile':profile}
    return render(request, 'organization_series_profile.html', context)
def organization_posts_list(request, pk):
    organization_profile = Organization.objects.get(pk=pk)
    organization_posts = Post.objects.filter(organization=organization_profile)
    profile = Profile.objects.get(username=request.user)
    top_three_posts = Post.objects.filter(organization=organization_profile, status='published') \
                                  .annotate(read_count_annotated=Count('read')) \
                                  .order_by('-read_count_annotated')[:3]
    context={'organization_profile':organization_profile,'organization_posts':organization_posts, 'profile':profile, 'top_three_posts':top_three_posts}
    return render(request, 'organization_posts_list.html', context)

def follow_organization(request, pk):
    organization_profile = Organization.objects.get(pk=pk)
    organization_profile.followers.add(request.user)
    organization_profile.save()
    return redirect('/')
# class AddUserToOrganizationView(View):
#     def post(self, request):
#         user_id = request.POST.get('user_id')
#         organization_id = request.POST.get('organization_id')
        
#         if user_id and organization_id:
#             user = User.objects.get(pk=user_id)
#             organization = Organization.objects.get(pk=organization_id)
#             organization.members.add(user)
#             organization.save()
#             return redirect('/')  # Redirect to a relevant page after adding the user
#         return redirect('/')
        
def add_org_member(request, user_id):
   if request.method == 'POST':
       selected_organization_id = request.POST.get('organization_id')
       organization = Organization.objects.get(pk=selected_organization_id)
       user = User.objects.get(pk=user_id)
       organization.members.add(user)
       organization.save()
       return 
