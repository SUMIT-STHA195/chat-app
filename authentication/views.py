# Create your views here.
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.

# from django.contrib.auth.models import User
from authentication.models import CustomUser
from django.contrib import messages


def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        user = CustomUser.objects.filter(username=username)
        if user.exists():
            messages.warning(request, 'Username already exists!!!')
            redirect('register')
        elif not password1 == password2:
            messages.warning(request, 'Password doesnot match!!!')
            redirect('register')
        else:
            user = CustomUser.objects.create_user(
                username=username,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
            )
            user.save()
            messages.info(request, 'Registration Successful')
            return redirect(reverse('authentication:login'))
    return render(request, 'authentication/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'User doesnot exist!!!')
            return redirect(reverse('login'))
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'login successful')
            return redirect('chat:index')
        else:
            messages.error(request, 'Wrong username or password')
            return redirect('authentication:login')
    return render(request, 'authentication/login.html')


def logout_page(request):
    logout(request)
    return redirect('authentication:login')


@login_required
def change_password(request):
    user = request.user
    print(user.username)
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 == password2:
            user.set_password(password1)
            user.save()
            logout(request)
            return redirect('login')
        else:
            messages.warning(request, 'Password must be same')
            return redirect('authentication:change-password')
    return render(request, 'authentication/change-password.html')
