from django.urls import path
from . import views
from .views import login_view, registrar_estudiante


app_name = 'banda_usuarios' 

urlpatterns = [
    # Autenticación y perfil común
    path('login/', login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),         
    path('completar-perfil/', views.completar_perfil, name='completar_perfil'),
    # Rutas exclusivas del Profesor
    path('profesor/registrar-estudiante/', views.registrar_estudiante, name='registrar_estudiante'),
    path('profesor/lista-estudiantes/', views.lista_estudiantes, name='lista_estudiantes'),
    path('estudiante/editar/<int:alumno_id>/', views.editar_estudiante, name='editar_estudiante'),
    path('estudiante/eliminar/<int:alumno_id>/', views.eliminar_estudiante, name='eliminar_estudiante'),
]