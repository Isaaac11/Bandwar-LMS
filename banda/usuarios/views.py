from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Usuario
from banda.academia.models import MaterialMultimedia

# ESTA LÍNEA ES LA QUE FALTA PARA QUE 'User' FUNCIONE ABAJO
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
    ultimos_materiales = MaterialMultimedia.objects.all().order_by('-fecha_subida')[:5]
    total_materiales = MaterialMultimedia.objects.count()
    # Aquí usamos 'Usuario' porque ya lo importaste arriba desde .models
    total_estudiantes = Usuario.objects.filter(rol='estudiante').count()

    context = {
        'ultimos_materiales': ultimos_materiales,
        'total_materiales': total_materiales,
        'total_estudiantes': total_estudiantes,
        'perfil_incompleto': not request.user.perfil_completo if request.user.rol == 'estudiante' else False
    }

    if request.user.rol == 'profesor':
        context['mis_alumnos'] = Usuario.objects.filter(creado_por=request.user)

    return render(request, 'usuarios/home.html', context)

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
            # Creamos el estudiante y lo vinculamos al profesor actual
            nuevo_estudiante = User.objects.create_user(
                username=cedula,
                first_name=nombre,
                last_name=apellido,
                password=password,
                rol='estudiante',
                profesor_asignado=request.user # Clave para que aparezca en SU lista
            )
            messages.success(request, f"Estudiante {nombre} registrado con éxito.")
            return redirect('banda_usuarios:lista_estudiantes')

    return render(request, 'usuarios/registrar_estudiante.html')
# Nota: dashboard_profesor parece sobrar si ya usas 'home' para todo, 
# pero la mantengo como pediste.
@login_required
def dashboard_profesor(request):
    if request.user.rol != 'profesor':
        return redirect('banda_usuarios:home')

    conteo_material = MaterialMultimedia.objects.count()
    ultimos_materiales = MaterialMultimedia.objects.all().order_by('-fecha_subida')[:5]

    context = {
        'conteo_material': conteo_material,
        'ultimos_materiales': ultimos_materiales,
    }
    return render(request, 'usuarios/dashboard_profesor.html', context)

@login_required
def completar_perfil(request):
    user = request.user
    if request.method == 'POST':
        # Cambio de nombre y apellido (Para ambos)
        user.first_name = request.POST.get('nombre')
        user.last_name = request.POST.get('apellido')
        
        # Solo el estudiante actualiza esto
        if user.rol == 'estudiante':
            user.semestre = request.POST.get('semestre')
            user.carrera = request.POST.get('carrera')
            
        # Rango Militar (Ambos pueden, pero con su lógica)
        user.rango_militar = request.POST.get('rango_militar')
        
        # Cambio de contraseña (Opcional)
        password = request.POST.get('password')
        if password and password.strip():
            user.set_password(password)
            update_session_auth_hash(request, user) # Evita que se cierre la sesión
            
        user.perfil_completo = True
        user.save()
        
        messages.success(request, "¡Perfil actualizado con éxito!")
        return redirect('banda_usuarios:home')
        
    return render(request, 'usuarios/completar_perfil.html')

@login_required
def lista_estudiantes(request):
    # Solo el profesor puede ver esto
    if request.user.rol != 'profesor':
        return redirect('banda_usuarios:home')
    
    # Obtenemos los alumnos creados por este profesor
    mis_alumnos = request.user.alumnos.all()
    return render(request, 'usuarios/lista_estudiantes.html', {'alumnos': mis_alumnos})