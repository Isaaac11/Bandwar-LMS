from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

#MULTIMEDIA


class MaterialMultimedia(models.Model):
    TIPO_CHOICES = [
        ('pdf', 'imagen / PDF'),
        ('video', 'Video de Práctica'),
        ('link', 'Enlace Externo (YouTube/Drive)'),
    ]

    titulo = models.CharField(max_length=200, verbose_name="Título del Material")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    archivo = models.FileField(upload_to='multimedia/', blank=True, null=True, verbose_name="Archivo Físico")
    link_externo = models.URLField(blank=True, null=True, verbose_name="URL / Enlace")
    fecha_subida = models.DateTimeField(auto_now_add=True)
    profesor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        limit_choices_to={'rol': 'profesor'}
    )
    def __str__(self):
        return f"{self.titulo} ({self.get_tipo_display()})"


#EXAMENES

class Examen(models.Model):
    titulo = models.CharField(max_length=200)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    duracion_minutos = models.PositiveIntegerField(null=True, blank=True, default=0)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )

    @property
    def esta_disponible(self):
        ahora = timezone.now()
        return self.fecha_inicio <= ahora <= self.fecha_fin

    def __str__(self):
        return self.titulo

class Pregunta(models.Model):
    TIPOS_PREGUNTA = [
        ('multiple', 'Selección Múltiple'),
        ('vf', 'Verdadero o Falso'),
    ]

    examen = models.ForeignKey(Examen, on_delete=models.CASCADE, related_name='preguntas')
    texto = models.TextField(verbose_name="Enunciado de la pregunta")
    tipo = models.CharField(max_length=20, choices=TIPOS_PREGUNTA, default='multiple')
    puntos = models.PositiveIntegerField(
        default=1, 
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text="Puntaje entre 1 y 20"
    )

    def __str__(self):
        return f"{self.examen.titulo} - {self.texto[:50]}"

class Opcion(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='opciones')
    texto = models.CharField(max_length=200)
    es_correcta = models.BooleanField(default=False)

    def __str__(self):
        return f"Pregunta {self.pregunta.id} - {self.texto}"

class ResultadoExamen(models.Model):
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nota = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)]
    )
    no_participo = models.BooleanField(default=False) 
    fecha_completado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        estado = "NP" if self.no_participo else f"{self.nota}/20"
        return f"{self.estudiante.username} - {self.examen.titulo}: {estado}"


class RespuestaEstudiante(models.Model):
    resultado = models.ForeignKey(ResultadoExamen, on_delete=models.CASCADE, related_name='respuestas')
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    opcion_seleccionada = models.ForeignKey(Opcion, on_delete=models.CASCADE)

    def __str__(self):
        return f"Respuesta de {self.resultado.estudiante.username} a {self.pregunta.id}"
    


#INSTRUMENTOS 

class Instrumento(models.Model):
    TIPOS = [
        ('trompeta', 'Trompeta'),
        ('redoblante', 'Redoblante'),
        ('bombo', 'Bombo'),
        ('lira', 'Lira'),
        ('granaderos', 'Granaderos'), 
        ('tambormayor', 'Tambor Mayor'), 
        ('platillos', 'Platillos'), 
    ]
    ESTADOS = [
        ('activo', 'Activo'),
        ('mantenimiento', 'En Mantenimiento'),
    ]

    nombre = models.CharField(max_length=50, choices=TIPOS)
    codigo_interno = models.CharField(max_length=20, unique=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='activo')
    
    # La relación se define aquí para que el alumno tenga el atributo .instrumento_propio
    estudiante_asignado = models.OneToOneField(
        settings.AUTH_USER_MODEL, # Apunta al modelo de usuario configurado
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='instrumento_propio'
    )

    def __str__(self):
        return f"{self.get_nombre_display()} ({self.codigo_interno})"