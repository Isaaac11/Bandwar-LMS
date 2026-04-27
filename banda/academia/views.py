from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import MaterialMultimedia, Examen, Pregunta, Opcion, ResultadoExamen, RespuestaEstudiante, Instrumento
from .forms import MaterialMultimediaForm, ExamenForm
from django.http import HttpResponse
from banda.usuarios.models import Usuario

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

@login_required
def lista_examenes(request):
    ahora = timezone.now()
    # Para el profesor: Ve todos los que creó
    if request.user.rol == 'profesor':
        examenes = Examen.objects.filter(creado_por=request.user).order_by('-fecha_inicio')
        return render(request, 'academia/profesor/lista_examenes.html', {'examenes': examenes})
    
    # Para el estudiante: Solo ve los que están en fecha
    else:
        examenes = Examen.objects.filter(
            fecha_inicio__lte=ahora,
            fecha_fin__gte=ahora
        ).order_by('fecha_fin')
        
        # También buscamos si el estudiante ya respondió algún examen
        resultados = ResultadoExamen.objects.filter(estudiante=request.user).values_list('examen_id', flat=True)
        
        return render(request, 'academia/estudiante/lista_examenes.html', {
            'examenes': examenes,
            'resultados_ids': resultados
        })

@login_required
def crear_examen(request):
    # Seguridad: Solo el profesor puede crear exámenes
    if request.user.rol != 'profesor':
        messages.error(request, "No tienes permiso para crear evaluaciones.")
        return redirect('banda_usuarios:home')
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        
        # Recogemos los pedazos del nuevo calendario limpio
        f_inicio = request.POST.get('fecha_inicio_d')
        h_inicio = request.POST.get('hora_inicio_t')
        f_fin = request.POST.get('fecha_fin_d')
        h_fin = request.POST.get('hora_fin_t')

        if f_inicio and h_inicio and f_fin and h_fin:
            # Unimos los campos para que la base de datos no reciba un "null"
            Examen.objects.create(
            titulo=request.POST.get('titulo'),
            fecha_inicio=f"{f_inicio} {h_inicio}",
            fecha_fin=f"{f_fin} {h_fin}",
            duracion_minutos=0, 
            creado_por=request.user
            )
            return redirect('banda_academia:lista_examenes')
            
    return render(request, 'academia/profesor/crear_examen.html')

def editar_examen(request, examen_id):
    # Seguridad: Solo el profesor puede editar exámenes
    if request.user.rol != 'profesor':
        messages.error(request, "No tienes permiso para editar evaluaciones.")
        return redirect('banda_usuarios:home')
    
    examen = get_object_or_404(Examen, id=examen_id)
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        f_inicio = request.POST.get('fecha_inicio_d')
        h_inicio = request.POST.get('hora_inicio_t')
        f_fin = request.POST.get('fecha_fin_d')
        h_fin = request.POST.get('hora_fin_t')

        if titulo:
            examen.titulo = titulo
        
        if f_inicio and h_inicio:
            examen.fecha_inicio = f"{f_inicio} {h_inicio}"
        
        if f_fin and h_fin:
            examen.fecha_fin = f"{f_fin} {h_fin}"
        
        examen.save()
        return redirect('banda_academia:lista_examenes')
    
    return render(request, 'academia/profesor/editar_examen.html', {'examen': examen})

# ESTA ES LA VERSIÓN QUE DEBE QUEDAR (Sin el if POST)
def eliminar_examen(request, examen_id):
    # Seguridad: Solo el profesor puede eliminar exámenes
    if request.user.rol != 'profesor':
        messages.error(request, "No tienes permiso para eliminar evaluaciones.")
        return redirect('banda_usuarios:home')
    
    examen = get_object_or_404(Examen, id=examen_id)
    examen.delete()
    messages.success(request, "Evaluación eliminada correctamente.") # Opcional: añade un mensaje
    return redirect('banda_academia:lista_examenes')

@login_required
def gestionar_preguntas(request, examen_id):
    # Seguridad: Solo el profesor puede gestionar preguntas
    if request.user.rol != 'profesor':
        messages.error(request, "No tienes permiso para gestionar preguntas.")
        return redirect('banda_usuarios:home')
    
    examen = get_object_or_404(Examen, id=examen_id)
    
    # CAMBIA ESTO: Usa minúscula y plural para la variable
    lista_preguntas = examen.preguntas.all() 

    if request.method == 'POST':
        texto = request.POST.get('texto')
        tipo = request.POST.get('tipo')
        puntos_raw = request.POST.get('puntos', 1)
        puntos = int(puntos_raw) if puntos_raw else 1

        # Validación para la UNEFA
        if puntos > 20:
            messages.error(request, "El puntaje máximo es 20.")
            return redirect('banda_academia:gestionar_preguntas', examen_id=examen.id)

        if texto:
            # Ahora 'Pregunta' (con P mayúscula) se refiere al MODELO
            Pregunta.objects.create(
                examen=examen,
                texto=texto,
                tipo=tipo,
                puntos=puntos
            )
            messages.success(request, "Pregunta añadida.")
            return redirect('banda_academia:gestionar_preguntas', examen_id=examen.id)

    return render(request, 'academia/profesor/gestionar_preguntas.html', {
        'examen': examen,
        'preguntas': lista_preguntas # Asegúrate de pasar la nueva variable aquí
    })

@login_required
def eliminar_pregunta(request, pregunta_id):
    # Seguridad: Solo el profesor puede eliminar preguntas
    if request.user.rol != 'profesor':
        messages.error(request, "No tienes permiso para eliminar preguntas.")
        return redirect('banda_usuarios:home')
    
    pregunta = get_object_or_404(Pregunta, id=pregunta_id)
    examen_id = pregunta.examen.id
    pregunta.delete()
    messages.success(request, "Pregunta eliminada correctamente.")
    return redirect('banda_academia:gestionar_preguntas', examen_id=examen_id)

@login_required
def editar_pregunta(request, pregunta_id):
    # Seguridad: Solo el profesor puede editar preguntas
    if request.user.rol != 'profesor':
        messages.error(request, "No tienes permiso para editar preguntas.")
        return redirect('banda_usuarios:home')
    
    pregunta = get_object_or_404(Pregunta, id=pregunta_id)
    if request.method == 'POST':
        pregunta.texto = request.POST.get('texto')
        pregunta.tipo = request.POST.get('tipo')
        puntos = int(request.POST.get('puntos', 1))
        
        if puntos <= 20:
            pregunta.puntos = puntos
            pregunta.save()
            messages.success(request, "Pregunta actualizada.")
            return redirect('banda_academia:gestionar_preguntas', examen_id=pregunta.examen.id)
        else:
            messages.error(request, "El puntaje no puede ser mayor a 20.")
            
    return render(request, 'academia/profesor/editar_pregunta.html', {'pregunta': pregunta})

@login_required
def agregar_opcion(request, pregunta_id):
    # Seguridad: Solo el profesor puede agregar opciones
    if request.user.rol != 'profesor':
        messages.error(request, "No tienes permiso para agregar opciones.")
        return redirect('banda_usuarios:home')
    
    pregunta = get_object_or_404(Pregunta, id=pregunta_id)
    if request.method == 'POST':
        texto = request.POST.get('texto')
        es_correcta = request.POST.get('es_correcta') == 'on' # Checkbox de HTML
        
        if texto:
            Opcion.objects.create(
                pregunta=pregunta,
                texto=texto,
                es_correcta=es_correcta
            )
            messages.success(request, "Opción añadida.")
    return redirect('banda_academia:gestionar_preguntas', examen_id=pregunta.examen.id)

@login_required
def eliminar_opcion(request, opcion_id):
    # Seguridad: Solo el profesor puede eliminar opciones
    if request.user.rol != 'profesor':
        messages.error(request, "No tienes permiso para eliminar opciones.")
        return redirect('banda_usuarios:home')
    
    opcion = get_object_or_404(Opcion, id=opcion_id)
    examen_id = opcion.pregunta.examen.id
    opcion.delete()
    messages.success(request, "Opción eliminada.")
    return redirect('banda_academia:gestionar_preguntas', examen_id=examen_id)

@login_required
def tomar_examen(request, examen_id):
    # Seguridad: Solo los estudiantes pueden tomar exámenes
    if request.user.rol != 'estudiante':
        messages.error(request, "No tienes permiso para tomar evaluaciones.")
        return redirect('banda_usuarios:home')
    
    examen = get_object_or_404(Examen, id=examen_id)
    preguntas = examen.preguntas.all()

    if request.method == 'POST':
        # 1. Creamos el registro del resultado primero
        resultado = ResultadoExamen.objects.create(
            examen=examen,
            estudiante=request.user,
            nota=0
        )

        puntos_obtenidos = 0
        total_puntos_examen = sum(p.puntos for p in preguntas) # Suma del valor real de las preguntas
        
        for pregunta in preguntas:
            opcion_id = request.POST.get(f'pregunta_{pregunta.id}')
            if opcion_id:
                opcion = get_object_or_404(Opcion, id=opcion_id)
                
                # Guardar la respuesta del estudiante
                RespuestaEstudiante.objects.create(
                    resultado=resultado,
                    pregunta=pregunta,
                    opcion_seleccionada=opcion
                )
                
                # Si es correcta, sumamos el valor de ESA pregunta
                if opcion.es_correcta:
                    puntos_obtenidos += pregunta.puntos

        # 2. Cálculo de nota final sobre 20
        if total_puntos_examen > 0:
            # Regla de tres: (puntos_obtenidos * 20) / total_puntos_examen
            nota_final = (puntos_obtenidos * 20) / total_puntos_examen
            resultado.nota = round(nota_final, 2)
            resultado.save()

        messages.success(request, f"Evaluación enviada. Nota: {resultado.nota}/20")
        return redirect('banda_academia:lista_examenes')

    return render(request, 'academia/estudiante/tomar_examen.html', {
        'examen': examen,
        'preguntas': preguntas,
    })

@login_required
def revisar_examen(request, examen_id):
    # Buscamos el resultado del estudiante para este examen
    resultado = get_object_or_404(ResultadoExamen, examen_id=examen_id, estudiante=request.user)
    
    # Obtenemos las respuestas que dio el estudiante
    # Usamos prefetch_related para que sea más rápido cargar las opciones
    respuestas = resultado.respuestas.select_related('pregunta', 'opcion_seleccionada').all()

    return render(request, 'academia/estudiante/revisar_examen.html', {
        'resultado': resultado,
        'respuestas': respuestas,
    })

def historia_banda(request):
    return render(request, 'academia/historia_banda.html')


@login_required
def gestionar_inventario(request):
    if request.user.rol != 'profesor':
        return redirect('banda_usuarios:home')

    if request.method == 'POST':
        # Lógica para registrar un nuevo instrumento
        nombre = request.POST.get('nombre')
        codigo = request.POST.get('codigo_interno')
        
        if nombre and codigo:
            Instrumento.objects.create(
                nombre=nombre,
                codigo_interno=codigo.upper(),
                estado='activo'
            )
            return redirect('banda_academia:gestionar_inventario')

    # Estadísticas para los cuadritos superiores
    stats = {
        'total': Instrumento.objects.count(),
        'libres': Instrumento.objects.filter(estado='activo', estudiante_asignado__isnull=True).count(),
        'mantenimiento': Instrumento.objects.filter(estado='mantenimiento').count(),
        'asignados': Instrumento.objects.filter(estudiante_asignado__isnull=False).count(),
    }

    instrumentos = Instrumento.objects.all().order_by('nombre', 'codigo_interno')
    
    return render(request, 'academia/profesor/inventario.html', {
        'instrumentos': instrumentos,
        'stats': stats,
        'tipos': Instrumento.TIPOS # Para el select del formulario
    })

@login_required
def asignar_instrumento(request, alumno_id):
    alumno = get_object_or_404(Usuario, id=alumno_id)
    
    if request.method == "POST":
        instrumento_id = request.POST.get('instrumento_id')
        
        if instrumento_id == "desasignar":
            # Si tiene un instrumento, lo liberamos
            if hasattr(alumno, 'instrumento_propio'):
                inst = alumno.instrumento_propio
                inst.estudiante_asignado = None
                inst.save()
        else:
            # Asignamos el nuevo instrumento
            nuevo_inst = get_object_or_404(Instrumento, id=instrumento_id)
            nuevo_inst.estudiante_asignado = alumno
            nuevo_inst.save()
            
    return redirect('banda_usuarios:lista_estudiantes')

@login_required
def cambiar_estado_instrumento(request, inst_id):
    instrumento = get_object_or_404(Instrumento, id=inst_id)
    if instrumento.estado == 'activo':
        instrumento.estado = 'mantenimiento'
        instrumento.estudiante_asignado = None # Se libera automáticamente si va a reparación
    else:
        instrumento.estado = 'activo'
    instrumento.save()
    return redirect('banda_academia:gestionar_inventario')

@login_required
def cambiar_estado_instrumento(request, inst_id):
    # Buscamos el instrumento o lanzamos un 404 si no existe
    instrumento = get_object_or_404(Instrumento, id=inst_id)
    
    if instrumento.estado == 'activo':
        instrumento.estado = 'mantenimiento'
        messages.warning(request, f"El instrumento {instrumento.codigo_interno} ha sido enviado a mantenimiento.")
    else:
        instrumento.estado = 'activo'
        messages.success(request, f"El instrumento {instrumento.codigo_interno} ya está operativo.")
    
    instrumento.save()
    return redirect('banda_academia:gestionar_inventario')