// PROYECTO: TLAHUACBOT
// Voz del bot: lee sus respuestas en voz alta (Web Speech API del navegador).


// ----------------------------------------------------------------------
// CONFIGURACION DE LA VOZ (aqui puedes cambiar como suena el bot)
// ----------------------------------------------------------------------

const CONFIG_VOZ = {
    activada: true,
    nombre: "Google",
    idioma: "es-MX",
    velocidad: 1.2,
    tono: 1
};


const sintesis = window.speechSynthesis;
const puedeHablar = Boolean(sintesis);
let vozElegida = null;

const PRONUNCIACION = [
    [/\bITIC\b/g, "I T I C"],
    [/\bTI\b/g, "T I"],
    [/\bTIC\b/g, "T I C"],
    [/\bTecNM\b/g, "Tec N M"]
];

function elegirVoz() {
    if (!puedeHablar) {
        return;
    }

    const voces = sintesis.getVoices();
    const enEspanol = voces.filter(function (voz) {
        return voz.lang.toLowerCase().startsWith("es");
    });

    if (enEspanol.length > 0) {
        console.log(
            "Voces en espanol disponibles:\n" +
            enEspanol.map(function (voz) {
                return " - " + voz.name + " (" + voz.lang + ")";
            }).join("\n")
        );
    }

    if (CONFIG_VOZ.nombre !== "") {
        const buscada = CONFIG_VOZ.nombre.toLowerCase();
        vozElegida = enEspanol.find(function (voz) {
            return voz.name.toLowerCase().includes(buscada);
        }) || null;
    }

    if (!vozElegida) {
        const idioma = CONFIG_VOZ.idioma.toLowerCase().replace("_", "-");
        vozElegida = enEspanol.find(function (voz) {
            return voz.lang.toLowerCase().replace("_", "-") === idioma;
        }) || null;
    }

    if (!vozElegida) {
        vozElegida = enEspanol[0] || null;
    }
}

if (puedeHablar) {
    elegirVoz();
    sintesis.onvoiceschanged = elegirVoz;
}

function hablar(texto) {
    if (!puedeHablar || !CONFIG_VOZ.activada) {
        return;
    }

    if (!vozElegida) {
        elegirVoz();
    }

    sintesis.cancel();

    let limpio = texto;
    PRONUNCIACION.forEach(function (par) {
        limpio = limpio.replace(par[0], par[1]);
    });

    const frases = limpio
        .split(/\n+|(?<=[.!?])\s+/)
        .map(function (frase) { return frase.trim(); })
        .filter(function (frase) { return frase.length > 0; });

    frases.forEach(function (frase) {
        const lectura = new SpeechSynthesisUtterance(frase);
        lectura.lang = CONFIG_VOZ.idioma;
        lectura.rate = CONFIG_VOZ.velocidad;
        lectura.pitch = CONFIG_VOZ.tono;

        if (vozElegida) {
            lectura.voice = vozElegida;
            lectura.lang = vozElegida.lang;
        }

        sintesis.speak(lectura);
    });
}

function detenerVoz() {
    if (puedeHablar) {
        sintesis.cancel();
    }
}

window.addEventListener("beforeunload", detenerVoz);
