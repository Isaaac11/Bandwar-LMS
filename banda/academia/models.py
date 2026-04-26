from django.db import models
from banda.usuarios.models import Usuario
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class MaterialMultimedia(models.Model):
    TIPO_CHOICES = [
        ('pdf', 'Partitura / PDF'),
        ('video', 'Video de Práctica'),
        ('link', 'Enlace Externo (YouTube/Drive)'),
    ]

    titulo = models.CharField(max_length=200, verbose_name="Título del Material")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    archivo = models.FileField(upload_to='multimedia/', blank=True, null=True, verbose_name="Archivo Físico")
    link_externo = models.URLField(blank=True, null=True, verbose_name="URL / Enlace")
    fecha_subida = models.DateTimeField(auto_now_add=True)
    profesor = models.ForeignKey(
        'banda_usuarios.Usuario', 
        on_delete=models.CASCADE, 
        limit_choices_to={'rol': 'profesor'}
    )
    def __str__(self):
        return f"{self.titulo} ({self.get_tipo_display()})"
    
    
class Examen(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'rol': 'profesor'})
    
    # Control de tiempo solicitado
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField()
    duracion_minutos = models.PositiveIntegerField(help_text="Duración máxima para responder una vez iniciado")
    
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo

    @property
    def esta_disponible(self):
        ahora = timezone.now()
        return self.fecha_inicio <= ahora <= self.fecha_fin

class Pregunta(models.Model):
    examen = models.ForeignKey(Examen, related_name='preguntas', on_delete=models.CASCADE)
    texto = models.TextField()
    puntos = models.DecimalField(max_digits=4, decimal_places=2, default=5.0) # Para llegar al 20

    def __str__(self):
        return f"{self.examen.titulo} - {self.texto[:50]}"

class Opcion(models.Model):
    pregunta = models.ForeignKey(Pregunta, related_name='opciones', on_delete=models.CASCADE)
    texto = models.CharField(max_length=255)
    es_correcta = models.BooleanField(default=False) # Esto servirá para la comparativa del estudiante

    def __str__(self):
        return self.texto

class Resultado(models.Model):
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Escala 01-20 y soporte para NP (No Participó)
    nota = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)]
    )
    no_participo = models.BooleanField(default=False) # El "NP" que mencionaste
    fecha_completado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        estado = "NP" if self.no_participo else self.nota
        return f"{self.estudiante.username} - {self.examen.titulo}: {estado}"