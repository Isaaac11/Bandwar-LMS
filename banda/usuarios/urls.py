from django.urls import path
from . import views

app_name = 'banda_usuarios' 

urlpatterns = [
    # Autenticación y perfil común
    path('login/', views.login_view, name='login'), 
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),         
    path('completar-perfil/', views.completar_perfil, name='completar_perfil'),
    
    # Rutas exclusivas del Profesor
    path('profesor/registrar-estudiante/', views.registrar_estudiante, name='registrar_estudiante'),
    path('profesor/lista-estudiantes/', views.lista_estudiantes, name='lista_estudiantes'),
    path('profesor/eliminar-estudiante/<int:estudiante_id>/', views.eliminar_estudiante, name='eliminar_estudiante'),
]