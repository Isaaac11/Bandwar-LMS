import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
const INFO_INSTRUMENTOS = {
    "lira": {
        titulo: "Lira (Glockenspiel)",
        descripcion: "Instrumento de percusión melódica. Es el encargado de llevar la melodía principal en las marchas militares.",
        mantenimiento: "Limpiar las láminas con un paño seco después de cada práctica para evitar la corrosión por sudor.",
        dato_unefa: "Posición: El portador debe mantener la espalda recta para equilibrar el peso del arnés."
    },
    "bombo": {
        titulo: "Bombo",
        descripcion: "Marca el pulso rítmico fundamental (el tiempo fuerte) de la formación.",
        mantenimiento: "Revisar la tensión de los parches y lubricar los tensores mensualmente para evitar grietas.",
        dato_unefa: "Uso: El mazo debe golpear cerca del centro para obtener un sonido profundo y seco."
    },
    "trompeta": {
        titulo: "Trompeta",
        descripcion: "Instrumento de viento-metal que aporta brillo y potencia sonora a la banda.",
        mantenimiento: "Lubricar los pistones con aceite específico y lavar la boquilla semanalmente con agua tibia.",
        dato_unefa: "Formación: Se ubican generalmente en la fila delantera por su gran alcance sonoro."
    },
    "tambormayor": {
        titulo: "Tambor Mayor",
        descripcion: "Líder de la banda encargado de la dirección, disciplina y señales durante los desplazamientos.",
        mantenimiento: "Limpiar y pulir el bastón de mando (mando) regularmente para mantener su brillo institucional.",
        dato_unefa: "Señalización: Los movimientos del bastón deben ser precisos y visibles para toda la formación."
    },
    "redoblante": {
        titulo: "Redoblante (Caja)",
        descripcion: "Instrumento de percusión de sonido agudo y seco, esencial para la ornamentación rítmica.",
        mantenimiento: "Ajustar el bordonero para evitar sonidos parásitos y revisar la tensión del parche superior.",
        dato_unefa: "Técnica: Se requiere precisión en el redoble para mantener la uniformidad sonora de la sección."
    },
    "platillos": {
        titulo: "Platillos",
        descripcion: "Aportan brillo y acentúan los momentos de mayor impacto en las marchas y desfiles.",
        mantenimiento: "Eliminar huellas dactilares y grasa después de cada uso con productos no abrasivos para metales.",
        dato_unefa: "Visual: El choque de platillos debe ser tanto sonoro como visualmente coordinado con el paso."
    },
    "granaderos": {
        titulo: "Granaderos",
        descripcion: "Cuerpos de tambores de tono medio que complementan la base rítmica entre el bombo y el redoblante.",
        mantenimiento: "Asegurar los tornillos de las bases y verificar que los arneses estén en condiciones óptimas.",
        dato_unefa: "Armonía: Trabajan en conjunto con los redoblantes para crear texturas rítmicas densas."
    }
};
let scene, camera, renderer, controls, modeloActual;

function init3D() {
    const container = document.getElementById('container-3d');
    if (!container) return;

    // 1. Escena
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);

    // 2. Cámara
    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(2, 2, 3);

    // 3. Renderizador
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    // 4. Controles (Ahora sí funcionará el constructor)
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    // 5. Iluminación
    scene.add(new THREE.AmbientLight(0xffffff, 0.8));
    const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
    dirLight.position.set(5, 10, 7.5);
    scene.add(dirLight);

    // 6. Carga inicial
    const nombreInstrumento = typeof INSTRUMENTO_ASIGNADO !== 'undefined' ? INSTRUMENTO_ASIGNADO : 'bombo';
    cargarInstrumento(nombreInstrumento);

    animate();
}

function cargarInstrumento(nombre) {
    const loader = new GLTFLoader(); // Usamos el loader importado
    const ruta = `/static/assets/models/${nombre}.glb`;

    document.getElementById('loader').style.display = 'block';

    loader.load(ruta, (gltf) => {
        if (modeloActual) scene.remove(modeloActual);
        modeloActual = gltf.scene;
        scene.add(modeloActual);
        document.getElementById('loader').style.display = 'none';
    }, undefined, (error) => {
        console.error("Error cargando el modelo:", error);
        // Si falla la trompeta, intentamos cargar el bombo por defecto
        if (nombre !== 'bombo') cargarInstrumento('bombo');
    });
}

function animate() {
    requestAnimationFrame(animate);
    if (modeloActual) modeloActual.rotation.y += 0.003;
    controls.update();
    renderer.render(scene, camera);
}

// Iniciar
init3D();

// Redimensionar
window.addEventListener('resize', () => {
    const container = document.getElementById('container-3d');
    if (!container) return;
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
});

function actualizarTextos(nombre) {
    const info = INFO_INSTRUMENTOS[nombre.toLowerCase()] || {
        titulo: "Instrumento",
        descripcion: "Información no disponible.",
        mantenimiento: "Consulte al instructor.",
        dato_unefa: "N/A"
    };

    document.getElementById('info-titulo').innerText = info.titulo;
    document.getElementById('info-texto').innerText = info.descripcion;
    document.getElementById('info-mant').innerText = info.mantenimiento;
    
    // Si decides agregar un párrafo extra para datos específicos de la UNEFA:
    if(document.getElementById('info-unefa')) {
        document.getElementById('info-unefa').innerText = info.dato_unefa;
    }
}

function conectarInformacion(nombreInstrumento) {
    // 1. Buscamos la data (convertimos a minúsculas por seguridad)
    const data = INFO_INSTRUMENTOS[nombreInstrumento.toLowerCase()];

    if (data) {
        // 2. Actualizamos los elementos del DOM por su ID
        const elementos = {
            'info-titulo': data.titulo,
            'info-texto': data.descripcion,
            'info-mant': data.mantenimiento,
            'info-unefa': data.dato_unefa
        };

        for (const [id, valor] of Object.entries(elementos)) {
            const el = document.getElementById(id);
            if (el) {
                el.innerText = valor;
                // Pequeño efecto visual de entrada
                el.style.opacity = 0;
                setTimeout(() => { el.style.opacity = 1; el.style.transition = "opacity 0.5s"; }, 50);
            }
        }
    } else {
        console.warn(`Instrumento "${nombreInstrumento}" no encontrado en INFO_INSTRUMENTOS.`);
    }
}

// 3. Ejecución automática al cargar
document.addEventListener('DOMContentLoaded', () => {
    // Usamos la variable global definida en el template
    if (typeof INSTRUMENTO_ASIGNADO !== 'undefined') {
        conectarInformacion(INSTRUMENTO_ASIGNADO);
    }
});