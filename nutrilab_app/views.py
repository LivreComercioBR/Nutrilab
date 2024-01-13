from django.shortcuts import HttpResponse, redirect, get_object_or_404, render
from django.contrib import messages
from django.contrib.messages import constants
import re
from .utils import password_is_valid, enviar_email, send_mail
from django.contrib.auth.models import User
from django.contrib import auth
import os
from django.conf import settings
from .models import Ativacao
from hashlib import sha256



def cadastro(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/")
        return render(request, 'cadastro.html')
    elif request.method == "POST":
        usuario = request.POST.get("usuario")
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        confirmar_senha = request.POST.get("confirmar_senha")

        # if usuario.exists():
        #     messages.add_message(request, constants.ERROR, 'Já existe um usuário com este nome no sistema!')
        #     return redirect('/nutrilab/cadastro')

        if not usuario:
            messages.add_message(request, constants.WARNING, 'Favor informar um nome de usuário!')
            return redirect('/nutrilab/cadastro')
        if not email:
            messages.add_message(request, constants.WARNING, 'O campo email é obrigatório!')
            return redirect('/nutrilab/cadastro')
        if not password_is_valid(request, senha, confirmar_senha):
            return redirect('/nutrilab/cadastro')
                
        try:
            user = User.objects.create_user(
                username=usuario,
                email=email,
                password=senha,
                is_active=False,
            )
            user.save()

            token = sha256(f'{usuario}{email}'.encode()).hexdigest()
            ativacao = Ativacao(token=token, user=user)
            ativacao.save()
            # path_template = os.path.join(settings.BASE_DIR, 'nutrilab_app/templates/enviar_email/confirmar_cadastro.html')
            # enviar_email(path_template, 'Cadastro confirmado', [email,], username=usuario)
            link_ativacao=f"http://127.0.0.1:8000/nutrilab/ativar_conta/{token}"

            send_mail(request, usuario, link_ativacao, email)
            

            messages.add_message(request, constants.SUCCESS, 'Usuário cadastrado com sucesso!')
            return redirect('/nutrilab/logar')
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema')
            return redirect('/nutrilab/cadastro')


def logar(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/")
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST.get('usuario')
        password = request.POST.get('senha')

        usuario = auth.authenticate(username=username, password=password)

        if not usuario:
            messages.add_message(request, constants.ERROR, 'Usuário ou senha incorretos!')
            return redirect('/nutrilab/logar') 
        else:
            auth.login(request, usuario)
            return HttpResponse("Você está logado no sistema")   


def sair(request):
    auth.logout(request)
    return redirect('/nutrilab/logar')


def ativar_conta(request, token):
    token = get_object_or_404(Ativacao, token=token)
    if token.ativo:
        messages.add_message(request, constants.WARNING, 'Esse token já foi usado')
        return redirect('/nutrilab/logar')
    user = User.objects.get(username=token.user.username)
    user.is_active = True
    user.save()
    token.ativo = True
    token.save()
    messages.add_message(request, constants.SUCCESS, 'Conta ativa com sucesso')
    return redirect('/nutrilab/logar')
