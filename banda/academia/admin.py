# banda/academia/admin.py
from django.contrib import admin
from .models import Examen, Pregunta, Opcion, Resultado

class OpcionInline(admin.TabularInline):
    model = Opcion
    extra = 3

class PreguntaAdmin(admin.ModelAdmin):
    inlines = [OpcionInline]

admin.site.register(Examen)
admin.site.register(Pregunta, PreguntaAdmin)
admin.site.register(Resultado)