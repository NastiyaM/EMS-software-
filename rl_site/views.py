from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from .data_work import data_send
import pandas as pd
import datetime


def start_page(request):
    if '_auth_user_id' not in request.session.keys():
        log = False
    else:
        log = User.objects.get(id=request.session['_auth_user_id'])
    data = {}
    data['log'] = log
    return render(request, 'rl_site/start_page.html', data)


def log(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['user'], password=request.POST['pass'])
        if user and user.is_active == True:
            login(request, user)
            return redirect('/new_system')
        else:
            return render(request, 'rl_site/log.html', {'message': 'Неверный логин или пароль'})
    return render(request, 'rl_site/log.html')


def sign(request):
    if request.method == 'POST':
        try:
            user = User.objects.create_user(username=request.POST['user'], password=request.POST['pass'])
            user.save()
        except:
            return render(request, 'rl_site/sign.html', {'message': 'Данный пользователь уже зарегистрирован'})
        return redirect('/login')
    return render(request, 'rl_site/sign.html')

def new_system(request):
    if '_auth_user_id' not in request.session.keys():
        log = False
    else:
        log = User.objects.get(id=request.session['_auth_user_id'])
    data = {}
    data['log'] = log
    if request.method == 'POST':
        return redirect('/new_system_learn')
    return render(request, 'rl_site/new_system_page.html', data)


def new_system_learn(request):
    if '_auth_user_id' not in request.session.keys():
        log = False
    else:
        log = User.objects.get(id=request.session['_auth_user_id'])
    data = {}
    data['log'] = log

    return render(request, 'rl_site/new_system_learn_page.html', data)

def out(request):
    logout(request)
    return redirect('/')