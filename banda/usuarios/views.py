from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Usuario
from banda.academia.models import MaterialMultimedia
from django.contrib.auth import get_user_model
def login_view(request):
    # Si el usuario ya está logueado, lo mandamos directo al home
    if request.user.is_authenticated:
        return redirect('banda_usuarios:home')

    if request.method == 'POST':
        usuario_nom = request.POST.get('username')
        clave = request.POST.get('password')
        
        user = authenticate(request, username=usuario_nom, password=clave)
        
        if user is not None:
            login(request, user)
            # Redirigimos a nuestra vista home personalizada, no al admin
            return redirect('banda_usuarios:home') 
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
            
    return render(request, 'usuarios/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('banda_usuarios:login')

@login_required
def home(request):
    # Consultas a la base de datos
    ultimos_materiales = MaterialMultimedia.objects.all().order_by('-fecha_subida')[:5]
    total_materiales = MaterialMultimedia.objects.count()
    total_estudiantes = Usuario.objects.filter(rol='estudiante').count()

    # Preparamos el contexto con los nombres exactos que usa tu HTML
    context = {
        'ultimos_materiales': ultimos_materiales,
        'total_materiales': total_materiales,
        'total_estudiantes': total_estudiantes,
    }

    # Si es profesor, podrías agregar lógica extra aquí si fuera necesario
    if request.user.rol == 'profesor':
        context['mis_alumnos'] = Usuario.objects.filter(creado_por=request.user)

    return render(request, 'usuarios/home.html', context)

def registrar_estudiante(request):
    if request.method == 'POST':
        # Capturamos los datos del formulario manual
        nom_usuario = request.POST.get('username')
        clave = request.POST.get('password')
        nombre = request.POST.get('first_name')
        apellido = request.POST.get('last_name')
        
        # Creamos el usuario con el rol de estudiante
        nuevo_alumno = Usuario.objects.create_user(
            username=nom_usuario,
            password=clave,
            first_name=nombre,
            last_name=apellido,
            rol=Usuario.ES_ESTUDIANTE,
            creado_por=request.user # Aquí queda vinculado al profesor actual
        )
        messages.success(request, f"Estudiante {nom_usuario} registrado con éxito.")
        return redirect('banda_usuarios:home')
        
    return render(request, 'usuarios/registrar_estudiante.html')

@login_required
def dashboard_profesor(request):
    # Verificamos que sea profesor
    if request.user.rol != 'profesor':
        return redirect('banda_usuarios:dashboard_estudiante')

    # Obtenemos estadísticas simples para las tarjetas del dashboard
    conteo_material = MaterialMultimedia.objects.filter(profesor=request.user).count()
    ultimos_materiales = MaterialMultimedia.objects.filter(profesor=request.user).order_by('-fecha_subida')[:5]

    context = {
        'conteo_material': conteo_material,
        'ultimos_materiales': ultimos_materiales,
    }
    return render(request, 'usuarios/dashboard_profesor.html', context)
