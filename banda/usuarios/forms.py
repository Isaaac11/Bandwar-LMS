from django import forms
from .models import Usuario
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator

class RegistroEstudianteForm(forms.ModelForm):
    # Cédula como CharField para evitar flechitas y comportamientos matemáticos
    cedula = forms.CharField(
        max_length=8,
        validators=[
            RegexValidator(
                regex=r'^\d{1,8}$',
                message="La cédula debe contener solo números (máximo 8)."
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '28123456',
            'inputmode': 'numeric',
            'oninput': "this.value = this.value.replace(/[^0-9]/g, '');"
        })
    )

    # Semestre con límites de la UNEFA
    semestre = forms.IntegerField(
        min_value=0,
        max_value=8,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': '7',
            'min': '0',
            'max': '8'
        })
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'cedula', 'carrera', 'semestre', 'rango_militar']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
        }