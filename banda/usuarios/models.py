from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    # Definimos los roles
    ES_PROFESOR = 'profesor'
    ES_ESTUDIANTE = 'estudiante'
    
    TIPOS_USUARIO = [
        (ES_PROFESOR, 'Profesor'),
        (ES_ESTUDIANTE, 'Estudiante'),
    ]

    rol = models.CharField(max_length=20, choices=TIPOS_USUARIO, default=ES_ESTUDIANTE)
    
    # --- Nuevos campos académicos y militares ---
    cedula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    carrera = models.CharField(max_length=100, null=True, blank=True)
    semestre = models.IntegerField(null=True, blank=True)
    rango_militar = models.CharField(max_length=50, null=True, blank=True)
    
    # Campo para biografía y foto (útil para el perfil del encargado)
    biografia = models.TextField(null=True, blank=True)
    foto_perfil = models.ImageField(upload_to='perfiles/', null=True, blank=True)
    
    # Control de flujo: ¿Ya el estudiante llenó sus datos obligatorios?
    perfil_completo = models.BooleanField(default=False)
    
    # Relación jerárquica
    creado_por = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='alumnos'
    )

    class Meta:
        db_table = 'banda_usuarios_usuario'  # Tabla actual - protege de migraciones destructivas
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
