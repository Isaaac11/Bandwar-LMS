# banda/academia/urls.py
from django.urls import path
from . import views

app_name = 'banda_academia' 

urlpatterns = [
    path('multimedia/', views.lista_multimedia, name='lista_multimedia'),
    path('subir/', views.subir_material, name='subir_material'),
    path('eliminar/<int:material_id>/', views.eliminar_material, name='eliminar_material'),
    path('profesor/examenes/nuevo/', views.crear_examen, name='crear_examen'),
    path('profesor/examenes/', views.lista_examenes, name='lista_examenes'),
]