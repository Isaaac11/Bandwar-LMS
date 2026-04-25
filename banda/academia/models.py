from django.db import models
from banda.usuarios.models import Usuario

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