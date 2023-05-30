from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

from .models import Profile


def home(request):
    template = 'core/index.html'
    
    context = {}
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
