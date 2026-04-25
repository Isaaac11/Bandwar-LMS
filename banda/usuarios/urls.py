from django.urls import path
from . import views

app_name = 'banda_usuarios' 

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('registrar-estudiante/', views.registrar_estudiante, name='registrar_estudiante'),
    path('logout/', views.logout_view, name='logout'),
    # ¡No olvides añadir la ruta del dashboard que creamos antes!
    path('dashboard/', views.dashboard_profesor, name='dashboard_profesor'),
    path('home/', views.home, name='home'),
]