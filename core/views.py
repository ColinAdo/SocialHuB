from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBadRequest, HttpResponse
from django.db.models import Q

from django.core.paginator import Paginator

from .models import Profile, Post, LikePost, FollowUnFollow, Comment, Message

import random

def home(request):
    template = 'core/index.html'
    logged_in_user = request.user

    # Getting posts of the logged in user and their followers
    followers = FollowUnFollow.objects.filter(follower=logged_in_user)
    user_being_followed = [f.user_being_followed for f in followers]
    posts = Post.objects.filter(
        Q(author=logged_in_user) | Q(author__in=user_being_followed)
    ).order_by('-date_posted')

    paginator = Paginator(posts, 2)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Getting suggested users
    suggested_users = User.objects.exclude(pk=logged_in_user.pk).exclude(followers__follower=logged_in_user)
    suggested_users = list(suggested_users) 
    random.shuffle(suggested_users) 
    suggested_users = suggested_users[:2]
    suggested_users_profiles = Profile.objects.filter(user__in=suggested_users)

    context = {
        'page_obj': page_obj,
        'suggested_users': zip(suggested_users, suggested_users_profiles),
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
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already exists')
                return redirect('signin')
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.save()

                # Creating profile for a user
                new_user = User.objects.get(username=username)
                profile = Profile.objects.create(user=new_user)
                profile.save()
                messages.success(request, 'User created successfully, you can now login')
                return redirect('signin')
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
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('signin')
    context = {}
    return render(request, template, context)

def signout(request):
    logout(request)
    messages.info(request, 'You have Just Signed-out')
    return redirect('signin')

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
            return redirect('settings')
        else:
            image = request.FILES['image']
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.bio = bio
            user_profile.image = image
            user_profile.location = location
            user_profile.save()
            messages.success(request, 'Settings updated successfully')
            return redirect('settings')
    context = {
        'user_profile': user_profile
    }
    return render(request, template, context)

def uploadpost(request):
    template = 'core/uploadpost.html'
    user = request.user

    if request.method == 'POST':
        author = User.objects.get(username=user)
        file = request.FILES.get('image')
        caption = request.POST['caption']

        new_post = Post.objects.create(author=author, file=file, caption=caption)
        new_post.save()
        messages.success(request, 'You have posted successfully')
        return redirect('home')
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

def profile(request, username):
    template = 'core/profile.html'
    logged_in_user = request.user

    author = User.objects.get(username=username)
    posts = Post.objects.filter(author=author).order_by('-date_posted')
    posts_count = posts.count()
    user_profile = Profile.objects.get(user=author)

    paginator = Paginator(posts, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    following = FollowUnFollow.objects.filter(follower=logged_in_user, user_being_followed=author).first()
    followers_count = FollowUnFollow.objects.filter(user_being_followed=author).count()
    following_count = FollowUnFollow.objects.filter(follower=author).count()

    context = {
        'page_obj': page_obj,
        'user_profile': user_profile,
        'following': following,
        'followers_count': followers_count,
        'following_count': following_count,
        'posts_count': posts_count,
    }
    return render(request, template, context)

def followunfollow(request):
    logged_in_user = request.user
    if request.method == 'POST':
        follower_username = request.POST['follower']
        username_of_user_being_followed = request.POST['user_being_followed']

        if not follower_username or not username_of_user_being_followed:
            return HttpResponseBadRequest("Missing parameters")

        user_being_followed = User.objects.get(username=username_of_user_being_followed)
        followers_filter = FollowUnFollow.objects.filter(
            follower=logged_in_user, user_being_followed=user_being_followed).first()
        
        if followers_filter:
            followers_filter.delete()
        else:
            FollowUnFollow.objects.create(follower=logged_in_user, user_being_followed=user_being_followed)
    prev_url = request.META.get('HTTP_REFERER')
    return redirect(prev_url)

def search(request):
    template = 'core/search.html'
    search = request.GET.get('user') if request.GET.get('user') != None else ''

    user_profiles = None

    if search:
        users = User.objects.filter(username__icontains=search)
        user_profiles = Profile.objects.filter(user__in=users)

        if not users:
            messages.info(request, f'No result for the {search}')

    context = {
        'search': search,
        'user_profiles': user_profiles,
    }
    return render(request, template, context)

def comments(request, pk):
    template = 'core/comments.html'
    logged_in_user = request.user

    content=request.POST.get('content')

    post = Post.objects.get(id=pk)
    comments = post.comment_set.all()

    if request.method == 'POST':
        comment = Comment.objects.create(
            user=logged_in_user,
            post=post,
            content=content
        )
        return redirect('comment', pk=post.id)

    context = {
        'comments': comments,
    }
    return render(request, template, context)

def send_message(request, receiver_username):
    template = 'core/send_message.html'
    sender = request.user
    receiver = User.objects.get(username=receiver_username)

    received_messages = Message.objects.filter(
        Q(sender=sender) | Q(receiver=sender)).order_by('date_sent')

    if request.method == 'POST':
        content = request.POST.get('content')
        message = Message.objects.create(sender=sender, receiver=receiver, content=content)
        return redirect('message', receiver_username)

    context = {
        'receiver': receiver,
        'received_messages': received_messages
    }
    return render(request, template, context)

def inbox(request):
    template = 'core/inbox.html'
    logged_in_user = request.user

    distinct_senders = User.objects.filter(
        sent_messages__receiver=logged_in_user,
        sent_messages__is_deleted=False
    ).distinct()

    context = {
        'distinct_senders': distinct_senders,
    }
    return render(request, template, context)

def followers_list(request, username):
    template = 'core/followers_following_list.html'
    logged_in_user = request.user

    author = User.objects.get(username=username)
    user_profile = Profile.objects.get(user=author)

    followers = FollowUnFollow.objects.filter(user_being_followed=author)
    following = FollowUnFollow.objects.filter(follower=logged_in_user, user_being_followed=author).first()


    context = {
        'user_profile': user_profile,
        'followers': followers,
        'following': following,
    }
    return render(request, template, context)

def following_list(request, username):
    template = 'core/followers_following_list.html'
    logged_in_user = request.user

    author = User.objects.get(username=username)
    user_profile = Profile.objects.get(user=author)

    users_following = FollowUnFollow.objects.filter(follower=author)
    following = FollowUnFollow.objects.filter(follower=logged_in_user, user_being_followed=author).first()


    context = {
        'user_profile': user_profile,
        'users_following': users_following,
        'following': following,
    }
    return render(request, template, context)

def deletepost(request, pk):
    template = 'core/delete.html'
    post = Post.objects.get(id=pk)

    if request.user != post.author:
        return HttpResponse('You are not allowd to delete this post')
    
    if request.method == 'POST':
        post.delete()
        return redirect('home')

    context = {
        'obj': post,
    }
    return render(request, template, context)

def deletecomment(request, pk):
    template = 'core/delete.html'

    comment = get_object_or_404(Comment, pk=pk)

    if request.user != comment.user:
        return HttpResponse('You are not allowed to delete this comment.')

    if request.method == 'POST':
        post_id = comment.post.id
        comment.delete()
        return redirect('comment', pk=post_id)

    context = {
        'obj': comment,
    }
    return render(request, template, context)

def deletemessage(request, pk):
    template = 'core/delete.html'

    message = get_object_or_404(Message, pk=pk)

    if request.method == 'POST':
        message.delete()
        return redirect('message', message.receiver)

    context = {
        'obj': message,
    }
    return render(request, template, context)

def deleteinbox(request, message_id):
    message = Message.objects.get(id=message_id)

    message.is_deleted = True
    message.save()

    return redirect('inbox')