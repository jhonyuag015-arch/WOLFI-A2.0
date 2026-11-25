// PROYECTO: TLAHUACBOT
// Chat: conexion entre la pagina y Python (Ollama).
// La respuesta llega por partes (streaming) y se va escribiendo en pantalla.
// Necesita voz.js y navegacion.js cargados antes.

const formulario = document.getElementById("formulario-chat");
const entrada = document.getElementById("entrada");
const mensajes = document.getElementById("mensajes");
const btnLimpiarChat = document.getElementById("btn-limpiar-chat");
const promptChips = document.querySelectorAll(".prompt-chip");
const carreraCards = document.querySelectorAll(".carrera-card");

// Mensajes anteriores de la conversacion (el bot los usa como memoria).
const MAX_HISTORIAL = 4;
let historial = [];

// Mientras el bot contesta no se aceptan mas preguntas (Ollama atiende una a la vez).
let enviando = false;


// ----------------------------------------------------------------------
// MENSAJES EN PANTALLA
// ----------------------------------------------------------------------

function obtenerHora() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function bajarChat() {
    mensajes.scrollTop = mensajes.scrollHeight;
}

function crearFila(tipo) {
    const esUsuario = (tipo === "usuario");
    const fila = document.createElement("div");

    fila.className = esUsuario
        ? "message user-message mensaje-fila fila-usuario"
        : "message bot-message mensaje-fila fila-bot";

    if (!esUsuario) {
        const avatar = document.createElement("img");
        avatar.src = "/static/img/lobito.png";
        avatar.alt = "TláhuacBot";
        avatar.className = "msg-avatar avatar-mensaje";
        fila.appendChild(avatar);
    }

    return fila;
}

// Muestra un mensaje. Devuelve el parrafo para poder seguir escribiendo en el.
function mostrarMensaje(texto, tipo) {
    const fila = crearFila(tipo);

    const burbuja = document.createElement("div");
    burbuja.className = "msg-bubble " + tipo;

    const parrafo = document.createElement("p");
    parrafo.textContent = texto;
    burbuja.appendChild(parrafo);

    const hora = document.createElement("span");
    hora.className = "msg-time";
    hora.textContent = obtenerHora();
    burbuja.appendChild(hora);

    fila.appendChild(burbuja);
    mensajes.appendChild(fila);
    bajarChat();

    return parrafo;
}

// Burbuja de "mmm..." mientras llega el primer texto.
function mostrarPensando() {
    const fila = crearFila("bot");

    const burbuja = document.createElement("div");
    burbuja.className = "thinking-bubble";
    burbuja.innerHTML = '<span class="thinking-pulse"></span><span>mmm...</span>';
    fila.appendChild(burbuja);

    mensajes.appendChild(fila);
    bajarChat();

    return fila;
}


// ----------------------------------------------------------------------
// RESPUESTA POR PARTES
// ----------------------------------------------------------------------

// Lee la respuesta del servidor (una linea JSON por evento) y avisa de cada una.
async function leerEventos(respuesta, alEvento) {
    const lector = respuesta.body.getReader();
    const decodificador = new TextDecoder();
    let pendiente = "";

    while (true) {
        const { done, value } = await lector.read();
        if (done) {
            break;
        }

        pendiente += decodificador.decode(value, { stream: true });
        const lineas = pendiente.split("\n");
        pendiente = lineas.pop();

        lineas.forEach(function (linea) {
            if (linea.trim() !== "") {
                alEvento(JSON.parse(linea));
            }
        });
    }

    if (pendiente.trim() !== "") {
        alEvento(JSON.parse(pendiente));
    }
}

async function enviarPregunta(textoPregunta) {
    const pregunta = textoPregunta.trim();

    if (pregunta === "" || enviando) {
        return;
    }

    enviando = true;
    detenerVoz();
    mostrarMensaje(pregunta, "usuario");

    if (entrada) {
        entrada.value = "";
    }

    const pensando = mostrarPensando();
    let parrafoBot = null;
    let texto = "";
    let terminado = false;

    // Escribe el texto del bot (crea la burbuja la primera vez).
    function escribir(nuevoTexto) {
        if (!parrafoBot) {
            pensando.remove();
            parrafoBot = mostrarMensaje("", "bot");
        }
        parrafoBot.textContent = nuevoTexto;
        bajarChat();
    }

    try {
        const respuesta = await fetch("/chat/stream", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                mensaje: pregunta,
                historial: historial.slice(-MAX_HISTORIAL)
            })
        });

        // Pregunta rechazada por el servidor (muy larga, no valida...).
        if (!respuesta.ok) {
            const datos = await respuesta.json();
            escribir(datos.respuesta);
            return;
        }

        await leerEventos(respuesta, function (evento) {
            if (evento.fin) {
                terminado = true;
                escribir(evento.respuesta);

                historial.push({ role: "user", content: pregunta });
                historial.push({ role: "assistant", content: evento.respuesta });
                historial = historial.slice(-10);

                hablar(evento.respuesta);
            } else {
                texto += evento.t;
                escribir(texto);
            }
        });

        if (!terminado && !parrafoBot) {
            escribir("No pude obtener respuesta del servidor.");
        }

    } catch (error) {
        if (!parrafoBot) {
            escribir("No pude conectar con el servidor.");
        }
    } finally {
        enviando = false;
    }
}


// ----------------------------------------------------------------------
// EVENTOS DE LA PAGINA
// ----------------------------------------------------------------------

if (formulario) {
    formulario.addEventListener("submit", function (evento) {
        evento.preventDefault();
        enviarPregunta(entrada.value);
    });
}

promptChips.forEach(function (chip) {
    chip.addEventListener("click", function () {
        enviarPregunta(chip.dataset.text);
    });
});

carreraCards.forEach(function (card) {
    card.addEventListener("click", function () {
        cambiarVista("chat");
        enviarPregunta(card.dataset.pregunta);
    });
});

if (btnLimpiarChat) {
    btnLimpiarChat.addEventListener("click", function () {
        detenerVoz();
        historial = [];
        mensajes.innerHTML = "";
        mostrarMensaje("Conversación reiniciada. ¿En qué más te puedo ayudar sobre el Tecnológico de Tláhuac II?", "bot");
    });
}
