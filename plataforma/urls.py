from django.urls import path
from plataforma import views


urlpatterns = [
    path('pacientes/', views.pacientes, name='pacientes')
]