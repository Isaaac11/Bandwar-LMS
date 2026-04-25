from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import MaterialMultimedia
from .forms import MaterialMultimediaForm
from django.contrib.auth import get_user_model

def es_profesor(user):
    return user.rol == 'profesor'

User = get_user_model()

@login_required
def home(request):
    # Asegúrate de usar estos nombres de variables exactos
    total_materiales = MaterialMultimedia.objects.count()
    total_estudiantes = User.objects.filter(rol='estudiante').count()
    ultimos_materiales = MaterialMultimedia.objects.all().order_by('-fecha_subida')[:5]

    context = {
        'total_materiales': total_materiales,
        'total_estudiantes': total_estudiantes,
        'ultimos_materiales': ultimos_materiales,
    }
    return render(request, 'usuarios/home.html', context)
@login_required
def lista_multimedia(request):
    materiales = MaterialMultimedia.objects.all().order_by('-fecha_subida')
    return render(request, 'lms/multimedia_list.html', {'materiales': materiales})

@login_required
@user_passes_test(es_profesor, login_url='banda_usuarios:home')
def subir_material(request):
    # Seguridad: Solo el profesor puede entrar aquí
    if request.user.rol != 'profesor':
        messages.error(request, "No tienes permiso para subir material.")
        return redirect('academia:lista_multimedia')

    if request.method == 'POST':
        form = MaterialMultimediaForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.profesor = request.user  # Asignamos al profesor actual
            material.save()
            messages.success(request, "¡Material cargado exitosamente!")
            return redirect('banda_academia:lista_multimedia')
    else:
        form = MaterialMultimediaForm()
    
    return render(request, 'lms/subir_material.html', {'form': form})

@login_required
@user_passes_test(es_profesor, login_url='banda_usuarios:home')
def eliminar_material(request, material_id):
    material = get_object_or_404(MaterialMultimedia, id=material_id)
    if request.method == 'POST':
        material.delete()
    return redirect('banda_academia:lista_multimedia')

