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
    path('examen/editar/<int:examen_id>/', views.editar_examen, name='editar_examen'),
    path('examen/eliminar/<int:examen_id>/', views.eliminar_examen, name='eliminar_examen'),
    path('examen/<int:examen_id>/preguntas/', views.gestionar_preguntas, name='gestionar_preguntas'),
    path('pregunta/<int:pregunta_id>/eliminar/', views.eliminar_pregunta, name='eliminar_pregunta'),
    path('pregunta/<int:pregunta_id>/editar/', views.editar_pregunta, name='editar_pregunta'),
    path('pregunta/<int:pregunta_id>/opcion/agregar/', views.agregar_opcion, name='agregar_opcion'),
    path('opcion/<int:opcion_id>/eliminar/', views.eliminar_opcion, name='eliminar_opcion'),
    path('examen/<int:examen_id>/tomar/', views.tomar_examen, name='tomar_examen'),
    path('examen/<int:examen_id>/revision/', views.revisar_examen, name='revisar_examen'),
    path('examen/<int:examen_id>/ver-notas/', views.ver_notas_estudiantes, name='ver_notas_estudiantes'),
    path('historia/', views.historia_banda, name='historia_banda'),
    path('asignar-instrumento/<int:alumno_id>/', views.asignar_instrumento, name='asignar_instrumento'),
    path('inventario/', views.gestionar_inventario, name='gestionar_inventario'),
    path('inventario/cambiar-estado/<int:inst_id>/', views.cambiar_estado_instrumento, name='cambiar_estado_instrumento'),
    path('inventario/eliminar/<int:instrumento_id>/', views.eliminar_instrumento, name='eliminar_instrumento'),
]