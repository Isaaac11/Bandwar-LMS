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
    
    # Este campo permite que sepamos qué profesor inscribió a qué estudiante
    creado_por = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='alumnos'
    )

    def __str__(self):
        return f"{self.username} ({self.rol})"
