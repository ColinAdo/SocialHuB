from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from .models import Profile, Post, LikePost


def home(request):
    template = 'core/index.html'
    posts = Post.objects.all()
    
    context = {
        'posts': posts,
    }
    return render(request, template, context)


def signup(request):
    template = 'core/signup.html'

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email already exists')
                return redirect('core:signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already exists')
                return redirect('core:signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.save()

                # Creating profile for a user
                new_user = User.objects.get(username=username)
                profile = Profile.objects.create(user=new_user)
                profile.save()
                messages.success(request, 'User created successfully, you can now login')
                return redirect('core:signup')
        else:
            messages.info(request, 'Password mismatch')

    context = {}
    return render(request, template, context)

def signin(request):
    template = 'core/signin.html'
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Login successful for {username}, welcome to socialHuB!')
            return redirect('core:home')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('core:signin')
    context = {}
    return render(request, template, context)

def signout(request):
    logout(request)
    messages.info(request, 'You have Just Signed-out')
    return redirect('core:signin')

def settings(request):
    template = 'core/settings.html'
    user = request.user
    user_profile = Profile.objects.get(user=user)
    if request.method == 'POST':
        if request.FILES.get('image') is None:
            bio = request.POST['bio']
            image = user_profile.image
            location = request.POST['location']

            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
            messages.success(request, 'Settings updated successfully')
            return redirect('core:settings')
        else:
            image = request.FILES['image']
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.bio = bio
            user_profile.image = image
            user_profile.location = location
            user_profile.save()
            messages.success(request, 'Settings updated successfully')
            return redirect('core:settings')
    context = {
        'user_profile': user_profile
    }
    return render(request, template, context)

def uploadpost(request):
    template = 'core/uploadpost.html'
    user = request.user

    if request.method == 'POST':
        author = User.objects.get(username=user)
        image = request.FILES.get('image')
        caption = request.POST['caption']

        new_post = Post.objects.create(author=author, image=image, caption=caption)
        new_post.save()
        messages.success(request, 'You have posted successfully')
        return redirect('core:home')
    context = {}
    return render(request, template, context)

def likePost(request):
    logged_in_user = request.user
    user = User.objects.get(username=logged_in_user)
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)
    filter_likes = LikePost.objects.filter(post_id=post, user=user).first()

    if filter_likes is None:
        like = LikePost.objects.create(post_id=post, user=user)
        like.save()

        post.no_of_likes = post.no_of_likes + 1
        post.save()
    else:
        filter_likes.delete()

        post.no_of_likes = post.no_of_likes - 1
        post.save()
    prev_url = request.META.get('HTTP_REFERER')
    return redirect(prev_url)