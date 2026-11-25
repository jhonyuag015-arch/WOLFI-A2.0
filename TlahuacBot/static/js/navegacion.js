// PROYECTO: TLAHUACBOT / WOLFI-A
// Navegación entre las pestañas de la página (inicio, oferta, chat).

const navButtons = document.querySelectorAll(".nav-btn");
const viewPanels = document.querySelectorAll(".view-panel");
const btnIniciarChat = document.getElementById("btn-iniciar-chat");
const btnVerCarreras = document.getElementById("btn-ver-carreras");

function cambiarVista(destino) {
    navButtons.forEach(function (btn) {
        btn.classList.toggle("active", btn.dataset.target === destino);
    });

    viewPanels.forEach(function (panel) {
        const esActiva = panel.id === "view-" + destino;
        panel.classList.toggle("active", esActiva);
        if (esActiva) {
            panel.scrollTop = 0;
        }
    });

    if (destino === "chat") {
        const contenedorMensajes = document.getElementById("mensajes");
        if (contenedorMensajes) {
            contenedorMensajes.scrollTop = contenedorMensajes.scrollHeight;
        }
        const campo = document.getElementById("entrada");
        // Solo auto-enfocar en pantallas grandes para no abrir el teclado de golpe en celular
        if (campo && window.innerWidth > 768) {
            setTimeout(function () { campo.focus(); }, 100);
        }
    }
}

navButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
        cambiarVista(btn.dataset.target);
    });
});

if (btnIniciarChat) {
    btnIniciarChat.addEventListener("click", function () {
        cambiarVista("chat");
    });
}

if (btnVerCarreras) {
    btnVerCarreras.addEventListener("click", function () {
        cambiarVista("oferta");
    });
}
