from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Usuario
from banda.academia.models import MaterialMultimedia

User = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        return redirect('banda_usuarios:home')

    if request.method == 'POST':
        usuario_nom = request.POST.get('username')
        clave = request.POST.get('password')
        user = authenticate(request, username=usuario_nom, password=clave)
        
        if user is not None:
            login(request, user)
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
    """
    Controlador central: Dirige al usuario a su dashboard correspondiente.
    """
    if request.user.rol == 'profesor':
        # Dashboard Profesor
        conteo_material = MaterialMultimedia.objects.count()
        ultimos_materiales = MaterialMultimedia.objects.all().order_by('-fecha_subida')[:5]
        total_estudiantes = Usuario.objects.filter(rol='estudiante').count()
        mis_alumnos = Usuario.objects.filter(creado_por=request.user)

        context = {
            'conteo_material': conteo_material,
            'ultimos_materiales': ultimos_materiales,
            'total_estudiantes': total_estudiantes,
            'mis_alumnos': mis_alumnos,
        }
        return render(request, 'usuarios/profesor/home.html', context)
        
    else:
        # Dashboard Estudiante
        context = {
            'perfil_incompleto': not request.user.perfil_completo
        }
        return render(request, 'usuarios/estudiante/home.html', context)

@login_required
def completar_perfil(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('nombre')
        user.last_name = request.POST.get('apellido')
        
        if user.rol == 'estudiante':
            user.semestre = request.POST.get('semestre')
            user.carrera = request.POST.get('carrera')
            
        user.rango_militar = request.POST.get('rango_militar')
        
        password = request.POST.get('password')
        if password and password.strip():
            user.set_password(password)
            update_session_auth_hash(request, user) 
            
        user.perfil_completo = True
        user.save()
        
        messages.success(request, "¡Perfil actualizado con éxito!")
        return redirect('banda_usuarios:home')
        
    return render(request, 'usuarios/completar_perfil.html')

@login_required
def registrar_estudiante(request):
    if request.user.rol != 'profesor':
        return redirect('banda_usuarios:home')
    
    if request.method == 'POST':
        cedula = request.POST.get('cedula')
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        password = request.POST.get('password')

        if User.objects.filter(username=cedula).exists():
            messages.error(request, "Esta cédula ya está registrada.")
        else:
            User.objects.create_user(
                username=cedula,
                first_name=nombre,
                last_name=apellido,
                password=password,
                rol='estudiante',
                creado_por=request.user 
            )
            messages.success(request, f"Estudiante {nombre} registrado con éxito.")
            return redirect('banda_usuarios:lista_estudiantes')

    return render(request, 'usuarios/registrar_estudiante.html')

@login_required
def lista_estudiantes(request):
    if request.user.rol != 'profesor':
        return redirect('banda_usuarios:home')
    
    # Filtramos los alumnos que fueron creados por este profesor
    mis_alumnos = Usuario.objects.filter(creado_por=request.user)
    return render(request, 'usuarios/profesor/lista_estudiantes.html', {'alumnos': mis_alumnos})

@login_required
def eliminar_estudiante(request, estudiante_id):
    if request.user.rol != 'profesor':
        return redirect('banda_usuarios:home')
    
    # Aseguramos que el profesor solo borre a SUS estudiantes
    estudiante = get_object_or_404(Usuario, id=estudiante_id, creado_por=request.user)
    
    if request.method == 'POST':
        nombre = estudiante.first_name
        estudiante.delete()
        messages.success(request, f"Estudiante {nombre} eliminado correctamente.")
        return redirect('banda_usuarios:lista_estudiantes')
    
    return redirect('banda_usuarios:lista_estudiantes')