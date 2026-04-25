from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http.response import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from users.forms import LoginForm, SignupForm, RevisionForm

from users.models import User


def user_index(request):
    return render(request, 'base.html')

def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('/')
    else:
        return redirect('/')


# Create your views here.

def user_signup(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            form = SignupForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Username already exists')
                    return render(request, 'users/signup.html', {'form': form})

                password1 = form.cleaned_data['password1']
                password2 = form.cleaned_data['password2']
                if password1 != password2:
                    messages.error(request, 'Passwords do not match')
                    return render(request, 'users/signup.html', {'form': form})

                user = User.objects.create_user(username=username,password=password1)
                user = authenticate(username=username, password=password1)
                messages.success(request, 'User created successfully')

                login(request, user)
                return redirect('/')
        else:
            form = SignupForm()
    context = {'form' : form}
    return render(request, 'users/signup.html', context)

def user_info(request):
    return render(request, 'users/userInfo.html')
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                next_url = request.GET.get('next') or request.POST.get('next') or '/'
                return redirect(next_url)
            else:
                messages.error(request, 'Username OR password is incorrect')
                #form.add_error(None, 'Not a valid username or password.')
    else:
        form = LoginForm()
    context = {
        'form' : form,
        'next' : request.GET.get('next', '/') # 이게 없으면 안되네
    }
    return render(request, 'users/login.html', context)

@login_required
def user_edit(request):
    if request.method == "POST":
        user = request.user
        form = RevisionForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            # profile_image가 User모델의 필드면 .save()가 자동으로 처리
            # print("file: ", request.FILES.get("profile_image"))
            form.save()
            messages.success(request, 'Revision successfully updated')
            return redirect("/users/userinfo/")
        else:
            messages.error(request, 'Something went wrong')
            return HttpResponseForbidden(f"error occured : {form.errors}")
    else: return render(request, "users/userInfo.html")

'''
<ul class="errorlist"><li>first_name<ul class="errorlist" id="id_first_name_error"><li>This field is required.</li></ul></li><li>last_name<ul class="errorlist" id="id_last_name_error"><li>This field is required.</li></ul></li></ul>
'''