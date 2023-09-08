from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBadRequest, JsonResponse, FileResponse
from django.db.models import Q
from django.core.mail import send_mail
from django.utils import timezone
from socialHub.settings import EMAIL_HOST_USER

from django.core.paginator import Paginator
from django.contrib.auth.views import PasswordChangeView

from .models import Profile, Post, LikePost, FollowUnFollow, Comment, Message, EmailVerification

import random

@login_required(login_url='signin')
def home(request):
    template = 'core/index.html'
    logged_in_user = request.user

    is_verified = EmailVerification.objects.filter(user=logged_in_user, is_verified=True).exists()

    # Getting posts of the logged in user and their followers
    followers = FollowUnFollow.objects.filter(follower=logged_in_user)
    user_being_followed = [f.user_being_followed for f in followers]
    posts = Post.objects.filter(
        Q(author=logged_in_user) | Q(author__in=user_being_followed)
    ).order_by('-date_posted')

    page_obj = list(posts)
    random.shuffle(page_obj)


    # Getting suggested users
    suggested_users = User.objects.exclude(pk=logged_in_user.pk).exclude(followers__follower=logged_in_user)
    suggested_users = list(suggested_users) 
    random.shuffle(suggested_users) 
    suggested_users = suggested_users[:5]
    suggested_users_profiles = Profile.objects.filter(user__in=suggested_users)

    liked_posts = [like.post_id.id for like in request.user.likepost_set.all()]

    # This is for notifications...
    distinct_senders_count = User.objects.filter(
        sent_messages__receiver=logged_in_user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')

    distinct_senders = User.objects.filter(
        sent_messages__receiver=logged_in_user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')[:3]
    
    author_followers_count = {}
    for post in page_obj:
        author_followers_count[post.author.username] = FollowUnFollow.objects.filter(user_being_followed=post.author).count()

    context = {
        'author_followers_count': author_followers_count,
        'distinct_senders_count': distinct_senders_count,
        'distinct_senders': distinct_senders,
        'liked_posts': liked_posts,
        'is_verified': is_verified,
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
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.save()

                # Generate verification code
                code = str(random.randint(100000, 999999))

                # Saving the verification code to the EmailVerification model
                verification = EmailVerification.objects.create(user=user, email=email, code=code)
                verification.save()

                # Send verification email
                subject = 'SocialHub Account Verification'
                message = f'Your SocialHub verification code is: {code}'
                from_email = EMAIL_HOST_USER
                recipient_list = [email]

                send_mail(subject, message, from_email, recipient_list)


                # Creating profile for a user
                new_user = User.objects.get(username=username)
                profile = Profile.objects.create(user=new_user)
                profile.save()

                # loggin the user
                user = authenticate(request, username=username, password=password1)
                if user is not None:
                    login(request, user)

                messages.success(request, 'Please check your email for the verification code.')
                return redirect('code_verification')
        else:
            messages.info(request, 'Password mismatch')

    context = {}
    return render(request, template, context)

def codeVerification(request):
    template = 'core/code_verification.html'
    logged_in_user = request.user
    is_verified = EmailVerification.objects.filter(user=logged_in_user, is_verified=True).exists()
    
    if request.method == 'POST':
        code = request.POST['code']
        try:
            verification = EmailVerification.objects.get(user=logged_in_user, code=code, is_verified=False)
            verification.is_verified = True
            verification.save()

            messages.success(request, "Your email is verified successfully")
            return redirect('home')
        except EmailVerification.DoesNotExist:
            messages.error(request, "Invalid verification code, try again!")
            return redirect('code_verification')

    context = {'is_verified': is_verified}
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

@login_required(login_url='signin')
def settings(request):
    template = 'core/settings.html'
    user = request.user
    is_verified = EmailVerification.objects.filter(user=user, is_verified=True).exists()

    location_options = [
        {'value': 'Algeria - Algiers', 'label': 'Algeria - Algiers'},
        {'value': 'Egypt - Cairo', 'label': 'Egypt - Cairo'},
        {'value': 'Ethiopia - Addis Ababa', 'label': 'Ethiopia - Addis Ababa'},
        {'value': 'Kenya - Nairobi', 'label': 'Kenya - Nairobi'},
        {'value': 'Nigeria - Abuja', 'label': 'Nigeria - Abuja'},
        {'value': 'South Africa - Pretoria', 'label': 'South Africa - Pretoria'},
        {'value': 'Sudan - Khartoum', 'label': 'Sudan - Khartoum'},
        {'value': 'Tanzania - Dodoma', 'label': 'Tanzania - Dodoma'},
        {'value': 'Uganda - Kampala', 'label': 'Uganda - Kampala'},
        {'value': 'Zimbabwe - Harare', 'label': 'Zimbabwe - Harare'},
        {'value': 'China - Beijing', 'label': 'China - Beijing'},
        {'value': 'India - New Delhi', 'label': 'India - New Delhi'},
        {'value': 'Indonesia - Jakarta', 'label': 'Indonesia - Jakarta'},
        {'value': 'Japan - Tokyo', 'label': 'Japan - Tokyo'},
        {'value': 'Kazakhstan - Nur-Sultan', 'label': 'Kazakhstan - Nur-Sultan'},
        {'value': 'Malaysia - Kuala Lumpur', 'label': 'Malaysia - Kuala Lumpur'},
        {'value': 'Pakistan - Islamabad', 'label': 'Pakistan - Islamabad'},
        {'value': 'Philippines - Manila', 'label': 'Philippines - Manila'},
    ]
    career_options = [
        {'value': 'Accountant', 'label': 'Accountant'},
        {'value': 'Marketing Manager', 'label': 'Marketing Manager'},
        {'value': 'Human Resources Specialist', 'label': 'Human Resources Specialist'},
        {'value': 'Financial Analyst', 'label': 'Financial Analyst'},
        {'value': 'Project Manager', 'label': 'Project Manager'},
        {'value': 'Sales Representative', 'label': 'Sales Representative'},
        {'value': 'Software Engineer', 'label': 'Software Engineer'},
        {'value': 'Data Scientist', 'label': 'Data Scientist'},
        {'value': 'Cybersecurity Analyst', 'label': 'Cybersecurity Analyst'},
        {'value': 'UX/UI Designer', 'label': 'UX/UI Designer'},
    ]
    user_profile = Profile.objects.get(user=user)
    if request.method == 'POST':
        if request.FILES.get('image') is None:
            career = request.POST['career']
            image = user_profile.image
            location = request.POST['location']
            website_link = request.POST['website_link']
            github_link = request.POST['github_link']
            x_link = request.POST['x_link']
            instagram_link = request.POST['instagram_link']
            linkedin_link = request.POST['linkedin_link']

            user_profile.image = image
            user_profile.career = career
            user_profile.location = location
            user_profile.website_link = website_link
            user_profile.github_link = github_link
            user_profile.x_link = x_link
            user_profile.instagram_link = instagram_link
            user_profile.linkedin_link = linkedin_link
            user_profile.save()
            messages.success(request, 'Settings updated successfully')
        else:
            image = request.FILES['image']
            career = request.POST['career']
            location = request.POST['location']
            location = request.POST['location']
            website_link = request.POST['website_link']
            github_link = request.POST['github_link']
            x_link = request.POST['x_link']
            instagram_link = request.POST['instagram_link']
            linkedin_link = request.POST['linkedin_link']

            user_profile.image = image
            user_profile.career = career
            user_profile.location = location
            user_profile.website_link = website_link
            user_profile.github_link = github_link
            user_profile.x_link = x_link
            user_profile.instagram_link = instagram_link
            user_profile.linkedin_link = linkedin_link
            user_profile.save()
            messages.success(request, 'Settings updated successfully')
    
    # This is for notifications...
    distinct_senders_count = User.objects.filter(
        sent_messages__receiver=user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')

    distinct_senders = User.objects.filter(
        sent_messages__receiver=user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')[:3]

    context = {
        'distinct_senders_count': distinct_senders_count,
        'distinct_senders': distinct_senders,
        'user_profile': user_profile,
        'is_verified': is_verified,
        'location_options': location_options,
        'career_options': career_options,
    }
    return render(request, template, context)

@login_required(login_url='signin')
def uploadpost(request):
    template = 'core/uploadpost.html'
    user = request.user
    is_verified = EmailVerification.objects.filter(user=user, is_verified=True).exists()

    # This is for notifications...
    distinct_senders = User.objects.filter(
        sent_messages__receiver=user,
        sent_messages__is_deleted=False
    ).distinct()

    if request.method == 'POST':
        author = User.objects.get(username=user)
        file = request.FILES.get('image')
        caption = request.POST['caption']

        new_post = Post.objects.create(author=author, file=file, caption=caption)
        new_post.save()
        messages.success(request, 'You have posted successfully')
        return redirect('home')
    # This is for notification
    distinct_senders_count = User.objects.filter(
        sent_messages__receiver=user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')

    distinct_senders = User.objects.filter(
        sent_messages__receiver=user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')[:3]

    context = {
        'distinct_senders_count': distinct_senders_count,
        'is_verified': is_verified,
        'distinct_senders': distinct_senders,
    }
    return render(request, template, context)

@login_required(login_url='signin')
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
    response_data = {'liked': filter_likes is None, 'post_id': post_id}
    return JsonResponse(response_data)

@login_required(login_url='signin')
def profile(request, username):
    template = 'core/profile.html'
    logged_in_user = request.user
    is_verified = EmailVerification.objects.filter(user=logged_in_user, is_verified=True).exists()

    author = User.objects.get(username=username)
    posts = Post.objects.filter(author=author).order_by('-date_posted')
    posts_count = posts.count()
    user_profile = Profile.objects.get(user=author)

    following = FollowUnFollow.objects.filter(follower=logged_in_user, user_being_followed=author).first()
    followers_count = FollowUnFollow.objects.filter(user_being_followed=author).count()
    following_count = FollowUnFollow.objects.filter(follower=author).count()
    prev_url = request.META.get('HTTP_REFERER')

    # This is for notifications...
    distinct_senders_count = User.objects.filter(
        sent_messages__receiver=logged_in_user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')

    distinct_senders = User.objects.filter(
        sent_messages__receiver=logged_in_user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')[:3]

    context = {
        'distinct_senders_count': distinct_senders_count,
        'distinct_senders': distinct_senders,
        'posts': posts,
        'prev_url': prev_url,
        'user_profile': user_profile,
        'following': following,
        'followers_count': followers_count,
        'following_count': following_count,
        'posts_count': posts_count,
        'is_verified': is_verified,
    }
    return render(request, template, context)

@login_required(login_url='signin')
def profile_posts(request, username, post_id):
    template = 'core/profileposts.html'
    logged_in_user = request.user
    is_verified = EmailVerification.objects.filter(user=logged_in_user, is_verified=True).exists()

    author = User.objects.get(username=username)
    post = get_object_or_404(Post, id=post_id, author=author)
    posts = Post.objects.filter(author=post.author).exclude(id=post_id).order_by('-date_posted')

    page_obj = list(posts)
    random.shuffle(page_obj)

    liked_posts = [like.post_id.id for like in request.user.likepost_set.all()]
    author_follower_count = FollowUnFollow.objects.filter(user_being_followed=author).count()

    # This is for notifications...
    distinct_senders_count = User.objects.filter(
        sent_messages__receiver=logged_in_user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')

    distinct_senders = User.objects.filter(
        sent_messages__receiver=logged_in_user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')[:3]

    context = {
        'author_follower_count': author_follower_count,
        'liked_posts': liked_posts,
        'distinct_senders_count': distinct_senders_count,
        'distinct_senders': distinct_senders,
        'posts': posts,
        'post': post,
        'page_obj': page_obj,
        'is_verified': is_verified,
    }
    return render(request, template, context)

@login_required(login_url='signin')
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

@login_required(login_url='signin')
def search(request):
    template = 'core/search.html'
    logged_in_user = request.user
    search = request.GET.get('user') if request.GET.get('user') != None else ''

    user_profiles = None

    if search:
        users = User.objects.filter(username__icontains=search)
        user_profiles = Profile.objects.filter(user__in=users)

        if not users:
            messages.info(request, f'No result for the {search}')
    
    # This is for notifications...
    distinct_senders_count = User.objects.filter(
        sent_messages__receiver=logged_in_user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')

    distinct_senders = User.objects.filter(
        sent_messages__receiver=logged_in_user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')[:3]

    context = {
        'distinct_senders_count': distinct_senders_count,
        'distinct_senders': distinct_senders,
        'search': search,
        'user_profiles': user_profiles,
    }
    return render(request, template, context)

@login_required(login_url='signin')
def comments(request, pk):
    template = 'core/comments.html'
    logged_in_user = request.user

    content=request.POST.get('content')

    post = Post.objects.get(id=pk)
    comments = post.comment_set.all().order_by('-date_posted')

    if request.method == 'POST':
        comment = Comment.objects.create(
            user=logged_in_user,
            post=post,
            content=content
        )
        return redirect('comment', pk=post.id)

    # This is for notifications...
    distinct_senders_count = User.objects.filter(
        sent_messages__receiver=logged_in_user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')

    distinct_senders = User.objects.filter(
        sent_messages__receiver=logged_in_user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')[:3]
    
    context = {
        'distinct_senders_count': distinct_senders_count,
        'distinct_senders': distinct_senders,
        'comments': comments,
    }
    return render(request, template, context)

@login_required(login_url='signin')
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

    # This is for notifications...
    distinct_senders_count = User.objects.filter(
        sent_messages__receiver=sender,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')

    distinct_senders = User.objects.filter(
        sent_messages__receiver=sender,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')[:3]

    context = {
        'distinct_senders_count': distinct_senders_count,
        'distinct_senders': distinct_senders,
        'receiver': receiver,
        'received_messages': received_messages
    }
    return render(request, template, context)

@login_required(login_url='signin')
def inbox(request):
    template = 'core/inbox.html'
    logged_in_user = request.user
    is_verified = EmailVerification.objects.filter(user=logged_in_user, is_verified=True).exists()

    # This is for notifications...
    distinct_senders_count = User.objects.filter(
        sent_messages__receiver=logged_in_user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')

    distinct_senders = User.objects.filter(
        sent_messages__receiver=logged_in_user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')[:3]

    context = {
        'distinct_senders_count': distinct_senders_count,
        'distinct_senders': distinct_senders,
        'is_verified': is_verified,
    }
    return render(request, template, context)

@login_required(login_url='signin')
def followers_list(request, username):
    template = 'core/followers_following_list.html'
    logged_in_user = request.user
    is_verified = EmailVerification.objects.filter(user=logged_in_user, is_verified=True).exists()

    author = User.objects.get(username=username)
    user_profile = Profile.objects.get(user=author)

    followers = FollowUnFollow.objects.filter(user_being_followed=author)
    following = FollowUnFollow.objects.filter(follower=logged_in_user, user_being_followed=author).first()

    # Create a dictionary to store follower counts for each user
    follower_counts = {}
    for follower in followers:
        follower_counts[follower.follower.username] = FollowUnFollow.objects.filter(user_being_followed=follower.follower).count()

    followers_count = len(follower_counts)
    following_count = FollowUnFollow.objects.filter(follower=author).count()

    # This is for notifications...
    distinct_senders_count = User.objects.filter(
        sent_messages__receiver=logged_in_user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')

    distinct_senders = User.objects.filter(
        sent_messages__receiver=logged_in_user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')[:3]

    context = {
        'follower_counts_dict': follower_counts,
        'distinct_senders_count': distinct_senders_count,
        'distinct_senders': distinct_senders,
        'user_profile': user_profile,
        'followers': followers,
        'following': following,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_verified': is_verified,
    }
    return render(request, template, context)

@login_required(login_url='signin')
def following_list(request, username):
    template = 'core/followers_following_list.html'
    logged_in_user = request.user
    is_verified = EmailVerification.objects.filter(user=logged_in_user, is_verified=True).exists()

    author = User.objects.get(username=username)
    user_profile = Profile.objects.get(user=author)

    users_following = FollowUnFollow.objects.filter(follower=author)
    following = FollowUnFollow.objects.filter(follower=logged_in_user, user_being_followed=author).first()

    followings_count = {}  # Initialize an empty dictionary

    followings_count = {}
    for user in users_following:
        followings_count[user.user_being_followed.username] = FollowUnFollow.objects.filter(user_being_followed=user.user_being_followed).count()

    following_count = len(followings_count)
    followers_count = FollowUnFollow.objects.filter(user_being_followed=author).count()

    # This is for notifications...
    distinct_senders_count = User.objects.filter(
        sent_messages__receiver=logged_in_user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')

    distinct_senders = User.objects.filter(
        sent_messages__receiver=logged_in_user,
        sent_messages__is_deleted=False
    ).distinct().order_by('-sent_messages__date_sent')[:3]

    context = {
        'followings_count': followings_count,
        'distinct_senders_count': distinct_senders_count,
        'distinct_senders': distinct_senders,
        'user_profile': user_profile,
        'users_following': users_following,
        'following': following,
        'is_verified': is_verified,
        'followers_count': followers_count,
        'following_count': following_count,
    }
    return render(request, template, context)

@login_required(login_url='signin')
def deletepost(request, pk):
    post = get_object_or_404(Post, id=pk)

    post.delete()
    messages.success(request, 'You have deleted the posted successfully')
    
    return redirect('profile', post.author.username)

@login_required(login_url='signin')
def deletecomment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    comment.delete()

    return redirect('comment', pk=comment.post.id)

@login_required(login_url='signin')
def deletemessage(request, pk):
    message = get_object_or_404(Message, pk=pk)

    message.delete()
    
    return redirect('message', message.receiver)

@login_required(login_url='signin')
def deleteinbox(request, message_id):
    message = Message.objects.get(id=message_id)

    message.is_deleted = True
    message.save()

    return redirect('inbox')

@login_required(login_url='signin')
def update_notification_count(request):
    if request.method == "POST" and request.is_ajax() and request.user.is_authenticated:
        # Mark all unread messages as read for the authenticated user
        Message.objects.filter(receiver=request.user, is_read=False).update(is_read=True)
        
        # Get the updated notification count (unread messages count)
        updated_notification_count = Message.objects.filter(receiver=request.user, is_read=False).count()
        
        # Return the updated count in the JSON response
        return JsonResponse({"success": True, "notification_count": updated_notification_count})
    else:
        return JsonResponse({"success": False})

@login_required(login_url='signin')    
def back_to_page(request):
    return_to = request.GET.get('return_to', None)
    if return_to:
        return redirect(return_to)
    else:
        return redirect('home')

@login_required(login_url='signin') 
def active_users_following(request):
    template = 'core/active_users.html'
    logged_in_user = request.user

    users_following = FollowUnFollow.objects.filter(follower=logged_in_user).values('user_being_followed__id')

    # Getting the list of active session IDs
    active_session_ids = []

    for session in Session.objects.filter(expire_date__gte=timezone.now()):
        data = session.get_decoded()
        if '_auth_user_id' in data:
            user_id = data['_auth_user_id']
            active_session_ids.append(user_id)

    # Get the active users that the logged-in user is following
    active_users_following = User.objects.filter(Q(id__in=active_session_ids) & Q(id__in=users_following))

    context = {
        'active_users_following': active_users_following,
    }

    return render(request, template, context)

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'core/password_change.html'

custom_password_change = login_required(CustomPasswordChangeView.as_view(), login_url="signin")

def download_file(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    file_path = post.file.path  
    
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{post.file.name}"'
    return response