from django.urls import path
from . import views

app_name = 'banda_usuarios' 

urlpatterns = [
    path('login/', views.login_view, name='login'), 
    path('home/', views.home, name='home'),         
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_profesor, name='dashboard_profesor'),
    path('completar-perfil/', views.completar_perfil, name='completar_perfil'),
    path('profesor/registrar-estudiante/', views.registrar_estudiante, name='registrar_estudiante'),
    path('profesor/lista-estudiantes/', views.lista_estudiantes, name='lista_estudiantes'),
]