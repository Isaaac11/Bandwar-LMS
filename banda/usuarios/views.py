from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Usuario
from banda.academia.models import MaterialMultimedia, Examen, ResultadoExamen, Instrumento
from django.utils import timezone
from .forms import RegistroEstudianteForm

User = get_user_model()

def login_view(request):
    # Si el usuario ya está logueado, lo mandamos al home
    if request.user.is_authenticated:
        return redirect('usuarios:home')

    if request.method == 'POST':
        # 'username' y 'password' vienen del 'name' de tus <input> en el HTML
        usuario = request.POST.get('username')
        clave = request.POST.get('password')

        # Intentamos autenticar con la cédula (que es el username) y la clave
        user = authenticate(request, username=usuario, password=clave)

        if user is not None:
            login(request, user)
            if user.rol == 'profesor':
                messages.success(request, f"Panel de Instructor: Hola, {user.first_name}")
            else:
                messages.success(request, f"¡Hola {user.first_name}! Bienvenido a Bandwar.")
            
            return redirect('usuarios:home')
        else:
            messages.error(request, "Cédula o contraseña incorrecta. Inténtalo de nuevo.")

    return render(request, 'usuarios/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('usuarios:login')


@login_required
def home(request):
    # 1. Definición de tiempo base para evitar UnboundLocalError
    ahora = timezone.now()
    
    # 2. Datos generales (Estadísticas)
    total_materiales = MaterialMultimedia.objects.count()
    total_estudiantes = User.objects.filter(rol='estudiante').count()
    instrumento_user = Instrumento.objects.filter(estudiante_asignado=request.user).first()
    
    # 3. Inicialización de variables de control
    tareas_pendientes = 0
    instructor = User.objects.filter(rol='profesor').first() # Instructor por defecto
    nota_ultimo_examen = None
    respondidos = []
    
    # Buscamos exámenes que estén en fecha vigente
    examenes_activos = Examen.objects.filter(
        fecha_inicio__lte=ahora, 
        fecha_fin__gte=ahora
    )

    # 4. Lógica específica para ESTUDIANTES
    if request.user.rol == 'estudiante':
        # Buscamos qué exámenes ha respondido ya
        respondidos = ResultadoExamen.objects.filter(
            estudiante=request.user
        ).values_list('examen_id', flat=True)
        
        # Exámenes activos que NO ha respondido
        pendientes_qs = examenes_activos.exclude(id__in=respondidos)
        tareas_pendientes = pendientes_qs.count()

        # Si hay tareas, el instructor es quien creó la tarea pendiente
        if pendientes_qs.exists():
            instructor = pendientes_qs.first().creado_por
        else:
            # Si no hay pendientes, mostrar el instructor del último examen general
            ultimo_ex = Examen.objects.order_by('-fecha_inicio').first()
            if ultimo_ex:
                instructor = ultimo_ex.creado_por

        # Limpieza de rango militar para la vista
        if instructor and instructor.rango_militar == "No poseo":
            instructor.rango_militar = None

    # 5. Obtener nota del último examen realizado (General)
    ultimo_examen = Examen.objects.order_by('-fecha_inicio').first()
    if ultimo_examen and request.user.rol == 'estudiante':
        resultado = ResultadoExamen.objects.filter(
            examen=ultimo_examen, 
            estudiante=request.user
        ).first()
        if resultado:
            nota_ultimo_examen = resultado.nota

    # 6. Contexto unificado
    context = {
        'instrumento': instrumento_user,
        'total_materiales': total_materiales,
        'total_estudiantes': total_estudiantes,
        'instructor': instructor, 
        'tareas_pendientes': tareas_pendientes,
        'ultimo_examen': ultimo_examen,
        'nota_ultimo_examen': nota_ultimo_examen,
        'respondidos': respondidos,
        'ahora': ahora,
    }
    
    # Renderizado dinámico según rol
    if request.user.rol == 'profesor':
        return render(request, 'usuarios/profesor/home.html', context)
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
        return redirect('usuarios:home')
        
    return render(request, 'usuarios/completar_perfil.html')

@login_required
def registrar_estudiante(request):
    # Seguridad: solo profesores pueden registrar
    if request.user.rol != 'profesor':
        return redirect('usuarios:home')
    
    if request.method == 'POST':
        # Obtenemos los datos del formulario
        cedula = request.POST.get('cedula')
        nombre = request.POST.get('first_name')
        apellido = request.POST.get('last_name')
        
        # Validación básica: que la cédula no esté vacía
        if not cedula:
            messages.error(request, "La cédula es obligatoria.")
            return render(request, 'usuarios/registrar_estudiante.html')

        if User.objects.filter(username=cedula).exists():
            messages.error(request, "Esta cédula ya está registrada.")
        else:
            User.objects.create_user(
                username=cedula,     
                password=cedula,     
                first_name=nombre,
                last_name=apellido,
                rol='estudiante',
                creado_por=request.user 
            )
            
            messages.success(request, f"Estudiante {nombre} registrado. Usuario y clave: {cedula}")
            return redirect('usuarios:lista_estudiantes')

    return render(request, 'usuarios/registrar_estudiante.html')

@login_required
def lista_estudiantes(request):
    if request.user.rol != 'profesor':
        return redirect('usuarios:home')
    
    # Obtenemos los alumnos creados por este profesor
    mis_alumnos = Usuario.objects.filter(creado_por=request.user)
    
    # Obtenemos instrumentos para los modales
    instrumentos_libres = Instrumento.objects.filter(
        estado='activo', 
        estudiante_asignado__isnull=True
    )
    
    return render(request, 'usuarios/profesor/lista_estudiantes.html', {
        'alumnos': mis_alumnos,
        'instrumentos_libres': instrumentos_libres
    })


@login_required
def editar_estudiante(request, alumno_id):
    alumno = get_object_or_404(Usuario, id=alumno_id)
    
    if request.method == 'POST':
        # Pasamos instance=alumno para que Django sepa que estamos EDITANDO, no creando
        form = RegistroEstudianteForm(request.POST, instance=alumno)
        if form.is_valid():
            form.save()
            messages.success(request, f"Datos de {alumno.first_name} actualizados.")
            return redirect('usuarios:lista_estudiantes')
    else:
        form = RegistroEstudianteForm(instance=alumno)
    
    return render(request, 'usuarios/registrar_estudiante.html', {
        'form': form,
        'editando': True,
        'alumno': alumno
    })

@login_required
def eliminar_estudiante(request, alumno_id):
    if request.user.rol != 'profesor':
        return redirect('usuarios:home')
        
    alumno = get_object_or_404(Usuario, id=alumno_id)
    nombre = alumno.get_full_name()
    alumno.delete()
    messages.warning(request, f"El estudiante {nombre} ha sido eliminado del sistema.")
    return redirect('usuarios:lista_estudiantes')


#INSTRUMENTOS 


@login_required
def asignar_instrumento(request, alumno_id):
    if request.user.rol != 'profesor':
        return redirect('usuarios:home')
        
    alumno = get_object_or_404(User, id=alumno_id)
    
    if request.method == "POST":
        instrumento_id = request.POST.get('instrumento_id')
        
        # 1. Liberar cualquier instrumento que el alumno tuviera antes
        Instrumento.objects.filter(estudiante_asignado=alumno).update(estudiante_asignado=None)
        
        # 2. Si se seleccionó uno nuevo (y no es "desasignar")
        if instrumento_id and instrumento_id != "desasignar":
            nuevo_inst = get_object_or_404(Instrumento, id=instrumento_id)
            nuevo_inst.estudiante_asignado = alumno
            nuevo_inst.save()
            messages.success(request, f"Instrumento asignado a {alumno.first_name}")
        else:
            messages.info(request, "Instrumento liberado.")
            
    return redirect('usuarios:lista_estudiantes')