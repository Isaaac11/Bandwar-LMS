from django import forms
from .models import MaterialMultimedia, Examen, Pregunta, Opcion

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
        fields = ['titulo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Examen de Solfeo I'}),
        }