import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// --- CONFIGURACIÓN ESTRUCTURAL ---
const INFO_INSTRUMENTOS = {
    "lira": { titulo: "Lira (Glockenspiel)", descripcion: "Instrumento de percusión melódica.", mantenimiento: "Limpiar las láminas con un paño seco.", dato_unefa: "Posición: Espalda recta para equilibrar el peso." },
    "bombo": { titulo: "Bombo", descripcion: "Marca el pulso rítmico fundamental.", mantenimiento: "Revisar tensión de los parches.", dato_unefa: "Uso: Golpear cerca del centro." },
    "trompeta": { titulo: "Trompeta", descripcion: "Instrumento de viento-metal potencia sonora.", mantenimiento: "Lubricar los pistones.", dato_unefa: "Formación: Fila delantera por alcance sonoro." },
    "tambormayor": { titulo: "Tambor Mayor", descripcion: "Líder de la banda, dirección y disciplina.", mantenimiento: "Limpiar y pulir el bastón.", dato_unefa: "Señalización: Movimientos precisos." },
    "redoblante": { titulo: "Redoblante (Caja)", descripcion: "Instrumento de percusión agudo.", mantenimiento: "Ajustar el bordonero.", dato_unefa: "Técnica: Precisión en el redoble." },
    "platillos": { titulo: "Platillos", descripcion: "Brillo e impacto rítmico.", mantenimiento: "Eliminar huellas dactilares.", dato_unefa: "Visual: Choque coordinado con el paso." },
    "granaderos": { titulo: "Granaderos", descripcion: "Cuerpos de tambores de tono medio.", mantenimiento: "Asegurar tornillos y arneses.", dato_unefa: "Armonía: Trabajo en conjunto con redoblantes." }
};

let scene, camera, renderer, controls, modeloActual;

// --- MOTOR VISUAL 3D (Fase 3: Simulación Integrada) ---
function init3D() {
    const container = document.getElementById('container-3d');
    if (!container) return;

    // 1. Escena
    scene = new THREE.Scene();

    // 2. Fondo con Efecto de Atenuación (Vignette/Oscurecimiento)
    const textureLoader = new THREE.TextureLoader();
    textureLoader.load('/static/img/unefa_patio.jpg', (texture) => {
        texture.colorSpace = THREE.SRGBColorSpace;
        
        // Reducimos la intensidad de la textura para que se vea más oscura
        // Esto crea el efecto de que el fondo está en segundo plano
        scene.background = texture;
        scene.backgroundIntensity = 0.4; // Ajusta este valor (0.1 a 1.0) para más o menos oscuridad
    });

    // 3. Cámara
    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(2, 2, 3);

    // 4. Renderizador
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    
    // Mejoramos el mapeo de color para que los colores del avatar resalten
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    
    container.appendChild(renderer.domElement);

    // 5. Controles
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    // 6. Iluminación Estilo "Foco" (Spotlight Effect)
    // Luz ambiental muy baja para que el fondo no brille por sí solo
    scene.add(new THREE.AmbientLight(0xffffff, 0.2)); 

    // Luz direccional fuerte sobre el avatar (esto hace que sus colores sobresalgan)
    const dirLight = new THREE.DirectionalLight(0xffffff, 2.0); 
    dirLight.position.set(5, 10, 7.5);
    scene.add(dirLight);

    // Luz de relleno opcional para suavizar sombras del uniforme
    const fillLight = new THREE.PointLight(0xffffff, 1.0);
    fillLight.position.set(-5, 2, -5);
    scene.add(fillLight);

    // 7. Carga del modelo
    const nombreInstrumento = typeof INSTRUMENTO_ASIGNADO !== 'undefined' ? INSTRUMENTO_ASIGNADO : 'bombo';
    cargarInstrumento(nombreInstrumento);

    animate();
}

// Carga dinámica de modelos .glb (Fase 2: Gestión)
function cargarInstrumento(nombre) {
    const loader = new GLTFLoader();
    const ruta = `/static/assets/models/${nombre}.glb`;

    document.getElementById('loader').style.display = 'block';

    loader.load(ruta, (gltf) => {
        if (modeloActual) scene.remove(modeloActual);
        modeloActual = gltf.scene;
        scene.add(modeloActual);
        document.getElementById('loader').style.display = 'none';
    }, undefined, (error) => {
        console.error("Error cargando el modelo:", error);
        // Fallback de seguridad
        if (nombre !== 'bombo') cargarInstrumento('bombo');
    });
}

// Bucle de animación (Interacción)
function animate() {
    requestAnimationFrame(animate);
    if (modeloActual) modeloActual.rotation.y += 0.003; // Rotación automática suave
    controls.update(); // Necesario para el damping
    renderer.render(scene, camera);
}

// --- UTILIDADES ---

// Redimensionamiento Responsivo
window.addEventListener('resize', () => {
    const container = document.getElementById('container-3d');
    if (!container) return;
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
});

// Conexión Dinámica view -> DOM (Fase 2)
function conectarInformacion(nombreInstrumento) {
    const data = INFO_INSTRUMENTOS[nombreInstrumento.toLowerCase()];

    if (data) {
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
                el.style.opacity = 0;
                setTimeout(() => { el.style.opacity = 1; el.style.transition = "opacity 0.5s"; }, 50);
            }
        }
    }
}

// --- EJECUCIÓN ---
init3D();

document.addEventListener('DOMContentLoaded', () => {
    if (typeof INSTRUMENTO_ASIGNADO !== 'undefined') {
        conectarInformacion(INSTRUMENTO_ASIGNADO);
    }
});