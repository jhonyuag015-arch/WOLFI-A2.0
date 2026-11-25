// PROYECTO: TLAHUACBOT
// Navegacion entre las pestañas de la pagina (inicio, carreras, chat).

const navButtons = document.querySelectorAll(".nav-btn");
const viewPanels = document.querySelectorAll(".view-panel");
const btnIniciarChat = document.getElementById("btn-iniciar-chat");
const btnVerCarreras = document.getElementById("btn-ver-carreras");

function cambiarVista(destino) {
    navButtons.forEach(function (btn) {
        btn.classList.toggle("active", btn.dataset.target === destino);
    });
    viewPanels.forEach(function (panel) {
        panel.classList.toggle("active", panel.id === "view-" + destino);
    });

    const campo = document.getElementById("entrada");
    if (destino === "chat" && campo) {
        setTimeout(function () { campo.focus(); }, 100);
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
