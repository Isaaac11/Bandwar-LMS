from django import forms
from .models import MaterialMultimedia
from .models import Examen, Pregunta, Opcion

class MaterialMultimediaForm(forms.ModelForm):
    class Meta:
        model = MaterialMultimedia
        fields = ['titulo', 'tipo', 'archivo', 'link_externo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Partitura de Himno Nacional'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
            'link_externo': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://youtube.com/...'}),
        }

class ExamenForm(forms.ModelForm):
    class Meta:
        model = Examen
        fields = ['titulo', 'descripcion', 'fecha_inicio', 'fecha_fin', 'duracion_minutos']
        widgets = {
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Teoría de Marcha I'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duracion_minutos': forms.NumberInput(attrs={'class': 'form-control'}),
        }