from curses.ascii import HT
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse


# @login_required
def pacientes(request):
    return HttpResponse("Esta é a sua página de clientes")
