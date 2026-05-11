// --- SPRITES DE ESTADO ---

let spriteOverrideTimeout = null;
let spriteOverrideInterval = null;

function mostrarSpriteTemp(codepet, frame, duracion = 2000) {
    if (spriteOverrideTimeout)  clearTimeout(spriteOverrideTimeout);
    if (spriteOverrideInterval) clearInterval(spriteOverrideInterval);
    detenerCaminata();

    const sprite = document.getElementById("pet-sprite");
    let toggle = false;
    sprite.src = `/static/assets/sprites/${codepet}/${frame}.png`;

    spriteOverrideInterval = setInterval(() => {
        toggle = !toggle;
        sprite.src = `/static/assets/sprites/${codepet}/${toggle ? "idle" : frame}.png`;
    }, 400);

    spriteOverrideTimeout = setTimeout(() => {
        clearInterval(spriteOverrideInterval);
        spriteOverrideInterval = null;
        spriteOverrideTimeout  = null;
        reanudarSpriteSegunEstado(codepet);
    }, duracion);
}

function reanudarSpriteSegunEstado(codepet) {
    if (spriteOverrideTimeout) return;
    if (spriteOverrideInterval) { clearInterval(spriteOverrideInterval); spriteOverrideInterval = null; }
    if ((currentState?.hunger ?? 1) === 0) {
        detenerCaminata();
        document.getElementById("pet-sprite").src =
            `/static/assets/sprites/${codepet}/tired.png`;
    } else {
        document.getElementById("pet-sprite").src =
            `/static/assets/sprites/${codepet}/walk1.png`;
        iniciarCaminata(codepet);
    }
}

// --- CAMINAR ---
let isWalking = false;
let walkFrameInterval = null;
let walkFrame = 1;
let walkCycleCount = 0;

function iniciarCaminata(codepet) {
    if (isWalking) return;
    isWalking = true;
    walkFrame = 1;
    walkCycleCount = 0;

    const sprite = document.getElementById("pet-sprite");

    // Reiniciar la animación CSS
    sprite.classList.remove("flipped");
    sprite.style.animation = "none";
    sprite.offsetHeight; 
    sprite.style.animation = "";

    // Alterna walk1 / walk2
    walkFrameInterval = setInterval(() => {
        walkFrame = walkFrame === 1 ? 2 : 1;
        sprite.src = `/static/assets/sprites/${codepet}/walk${walkFrame}.png`;
    }, 300);

    sprite.addEventListener("animationiteration", onWalkCycle);
}

function detenerCaminata() {
    if (!isWalking) return;
    isWalking = false;

    clearInterval(walkFrameInterval);
    walkFrameInterval = null;

    const sprite = document.getElementById("pet-sprite");
    sprite.removeEventListener("animationiteration", onWalkCycle);
    sprite.classList.remove("flipped");
}

function onWalkCycle() {
    walkCycleCount++;
    const sprite = document.getElementById("pet-sprite");
    // Impar → va hacia la izquierda (flipped), Par → va hacia la derecha
    if (walkCycleCount % 2 === 1) {
        sprite.classList.add("flipped");
    } else {
        sprite.classList.remove("flipped");
    }
}

// --- HELPERS DE UI ---

function desactivarBotones(disabled) {
    document.querySelectorAll(".terminal-actions .action-btn").forEach(btn => btn.disabled = disabled);
}

function updatePips(id, value, max = null) {
    const container = document.getElementById(id);
    if (!container) return;
    // Reconstruir pips si el máximo cambió (ej: evolución cambia max_level)
    if (max !== null && container.querySelectorAll(".pip").length !== max) {
        container.innerHTML = Array.from({length: max}, () =>
            `<span class="pip"></span>`).join("");
    }
    const pips = container.querySelectorAll(".pip");
    pips.forEach((pip, i) => pip.classList.toggle("pip-on", i < value));
    const valueEl = container.closest(".stat-row")?.querySelector(".stat-value");
    if (valueEl) valueEl.innerText = `${value}/${max ?? pips.length}`;
}

function updateBar(id, value, max = 100) {
    const bar = document.getElementById(id);
    if (!bar) return;
    const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0;
    bar.querySelector(".stat-bar-fill").style.width = `${pct}%`;
    const valueEl = bar.closest(".stat-row")?.querySelector(".stat-value");
    if (valueEl) valueEl.innerText = `${value}/${max}`;
}

// --- ACTUALIZAR INTERFAZ ---

function actualizarInterfaz(state) {
    const terminalScreen = document.getElementById("terminal-screen");

    if (state.hp <= 0) {
        terminalScreen.classList.add("dead");
        detenerCaminata();
        desactivarBotones(true);
        return;
    }

    currentState = state;
    terminalScreen.classList.remove("dead");
    desactivarBotones(false);

    // Stats vitales
    updatePips("stat-hp", state.hp);
    updatePips("stat-hunger", state.hunger);
    updatePips("stat-waste", state.waste);
    updatePips("stat-stage", state.stage);

    // Barras
    const caps = state.stat_caps || {};
    updateBar("stat-energy",    state.energy,     100);
    updateBar("stat-combat-hp", state.combat_hp,  caps.combat_hp  ?? 100);
    updateBar("stat-strength",  state.strength,   caps.strength   ?? 100);
    updateBar("stat-speed",     state.speed,      caps.speed      ?? 100);
    updatePips("stat-level", state.level, caps.max_level ?? 10);

    // Textos
    document.getElementById("terminal-title").innerText = `${state.name}@codepets:~$`;
    document.getElementById("stat-xp").innerText = state.xp;

    // Basura
    renderBasura(state.waste);

    // Alertas de botones
    document.querySelector("[data-action='feed']").classList.toggle("btn-alert", state.hunger === 0);
    document.querySelector("[data-action='heal']").classList.toggle("btn-alert", state.hp <= 1);

    // Evoluciones
    renderEvoluciones(state.evolutions || []);

    // Sprite — reiniciar si evolucionó o si no estaba caminando
    const sprite = document.getElementById("pet-sprite");
    const prevCodepet = sprite.getAttribute("data-pet");
    sprite.setAttribute("data-pet", state.codepet);

    if (!isWalking || prevCodepet !== state.codepet) {
        detenerCaminata();
        reanudarSpriteSegunEstado(state.codepet);
    } else if (!spriteOverrideTimeout) {
        // Actualizar tired/walk según hunger sin reiniciar si ya está bien
        if (state.hunger === 0) {
            detenerCaminata();
            sprite.src = `/static/assets/sprites/${state.codepet}/tired.png`;
        } else if (!isWalking) {
            reanudarSpriteSegunEstado(state.codepet);
        }
    }

    if (prevCodepet && prevCodepet !== state.codepet) {
        const esFinal = state.evolutions.length === 0;
        mostrarModalEvolucion(state, esFinal);
    }
}

// --- MINIJUEGO (compartido) ---

let minigameRunning = false;
let minigameRaf = null;
let cursorPos = 0;
let cursorDir = 1;
let lastMinigameTime = null;
let zoneStart = 0;
let _cursorEl = null;
const CURSOR_SPEED = 55;
const ZONE_WIDTH = 20;

function iniciarMinijuego(zoneId, cursorId) {
    zoneStart = 10 + Math.random() * 60;
    const zoneEl = document.getElementById(zoneId);
    _cursorEl = document.getElementById(cursorId);
    zoneEl.style.left = `${zoneStart}%`;
    zoneEl.style.width = `${ZONE_WIDTH}%`;

    cursorPos = 0;
    cursorDir = 1;
    minigameRunning = true;
    lastMinigameTime = null;
    minigameRaf = requestAnimationFrame(animarCursor);
}

function animarCursor(timestamp) {
    if (!minigameRunning) return;
    if (!lastMinigameTime) lastMinigameTime = timestamp;
    const delta = (timestamp - lastMinigameTime) / 1000;
    lastMinigameTime = timestamp;

    cursorPos += cursorDir * CURSOR_SPEED * delta;
    if (cursorPos >= 100) { cursorPos = 100; cursorDir = -1; }
    if (cursorPos <= 0)   { cursorPos = 0;   cursorDir =  1; }

    _cursorEl.style.left = `${cursorPos}%`;
    minigameRaf = requestAnimationFrame(animarCursor);
}

function detenerMinijuego() {
    minigameRunning = false;
    if (minigameRaf) cancelAnimationFrame(minigameRaf);
    minigameRaf = null;
}

// --- ENTRENAMIENTO ---

let selectedStat = null;
let currentState = null;

function abrirModalEntrenamiento() {
    selectedStat = null;
    document.getElementById("train-step-select").classList.remove("hidden");
    document.getElementById("train-step-game").classList.add("hidden");
    document.getElementById("train-result").innerText = "";

    // Deshabilitar stats al máximo
    const caps = currentState?.stat_caps || {};
    const state = currentState || {};
    document.querySelector("[data-stat='strength']").disabled = state.strength >= caps.strength;
    document.querySelector("[data-stat='speed']").disabled    = state.speed    >= caps.speed;
    document.querySelector("[data-stat='hp']").disabled       = state.combat_hp >= caps.combat_hp;

    document.getElementById("train-modal").classList.remove("hidden");
}

function cerrarModalEntrenamiento() {
    document.getElementById("train-modal").classList.add("hidden");
    detenerMinijuego();
}

async function resolverMinijuego() {
    if (!minigameRunning) return;
    detenerMinijuego();

    const won = cursorPos >= zoneStart && cursorPos <= zoneStart + ZONE_WIDTH;
    const resultEl = document.getElementById("train-result");
    resultEl.innerText = won ? "> ¡Acierto! Entrenamiento exitoso." : "> Fallaste. Sin ganancia.";
    resultEl.style.color = won ? "var(--accent)" : "#ff4444";

    try {
        const res = await fetch("/api/train", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ stat_type: selectedStat, won_minigame: won })
        });
        const data = await res.json();
        if (!data.success) {
            resultEl.innerText = `> ${data.message}`;
            resultEl.style.color = "#ff4444";
        }
    } catch (e) {}

    setTimeout(async () => {
        cerrarModalEntrenamiento();
        const res   = await fetch("/api/state");
        const state = await res.json();
        const sprite      = document.getElementById("pet-sprite");
        const prevCodepet = sprite.getAttribute("data-pet");
        if (state.codepet && state.codepet !== prevCodepet) {
            if (spriteOverrideTimeout)  { clearTimeout(spriteOverrideTimeout);   spriteOverrideTimeout  = null; }
            if (spriteOverrideInterval) { clearInterval(spriteOverrideInterval); spriteOverrideInterval = null; }
            detenerCaminata();
            sprite.setAttribute("data-pet", state.codepet);
            sprite.src = `/static/assets/sprites/${state.codepet}/walk1.png`;
            iniciarCaminata(state.codepet);
            mostrarModalEvolucion(state, (state.evolutions || []).length === 0);
        }
        actualizarInterfaz(state);
    }, 1500);
}

// --- COMBATE ---

let selectedZoneIndex = null;

async function abrirModalCombate() {
    selectedZoneIndex = null;
    document.getElementById("fight-step-select").classList.remove("hidden");
    document.getElementById("fight-step-game").classList.add("hidden");
    document.getElementById("fight-step-anim").classList.add("hidden");
    document.getElementById("fight-result").innerText = "";

    const zonesContainer = document.getElementById("fight-zone-btns");
    zonesContainer.innerHTML = "";

    try {
        const res = await fetch("/api/zones");
        const zones = await res.json();

        if (zones.length === 0) {
            zonesContainer.innerHTML = "<p class='train-label'>> Sin zonas disponibles.</p>";
        } else {
            zones.forEach(zone => {
                const btn = document.createElement("button");
                btn.className = "action-btn";
                btn.textContent = zone.name;
                btn.addEventListener("click", () => {
                    selectedZoneIndex = zone.index;
                    document.getElementById("fight-step-select").classList.add("hidden");
                    document.getElementById("fight-step-game").classList.remove("hidden");
                    iniciarMinijuego("fight-minigame-zone", "fight-minigame-cursor");
                });
                zonesContainer.appendChild(btn);
            });
        }
    } catch (e) {
        zonesContainer.innerHTML = "<p class='train-label'>> Error cargando zonas.</p>";
    }

    document.getElementById("fight-modal").classList.remove("hidden");
}

function cerrarModalCombate() {
    document.getElementById("fight-modal").classList.add("hidden");
    detenerMinijuego();
}

function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
}

async function animarBatalla(petCodepet, enemySprite, petWon) {
    const petEl   = document.getElementById("battle-pet");
    const enemyEl = document.getElementById("battle-enemy");

    const spr = (codepet, frame) => `/static/assets/sprites/${codepet}/${frame}.png`;

    petEl.src   = spr(petCodepet,  "idle");
    enemyEl.src = spr(enemySprite, "idle");
    await sleep(400);

    // Ataque del pet
    petEl.src = spr(petCodepet, "attack");
    await sleep(500);

    if (petWon) {
        enemyEl.src = spr(enemySprite, "hurt");
        await sleep(600);
    } else {
        // Contraataque enemigo
        petEl.src   = spr(petCodepet,  "idle");
        enemyEl.src = spr(enemySprite, "attack");
        await sleep(500);
        petEl.src = spr(petCodepet, "hurt");
        await sleep(600);
    }

    petEl.src   = spr(petCodepet,  "idle");
    enemyEl.src = spr(enemySprite, "idle");
}

async function resolverCombate() {
    if (!minigameRunning) return;
    detenerMinijuego();

    const minigameWon  = cursorPos >= zoneStart && cursorPos <= zoneStart + ZONE_WIDTH;
    const codepetAntes = document.getElementById("pet-sprite").getAttribute("data-pet");

    // Pasar a fase de animación
    document.getElementById("fight-step-game").classList.add("hidden");
    document.getElementById("fight-step-anim").classList.remove("hidden");

    const resultEl   = document.getElementById("fight-result");
    const petCodepet = codepetAntes;
    resultEl.innerText = "";

    let data = null;
    try {
        const res = await fetch("/api/fight", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ zone_index: selectedZoneIndex, won_minigame: minigameWon })
        });
        data = await res.json();
    } catch (e) {}

    if (data) {
        await animarBatalla(petCodepet, data.enemy_sprite, data.won);
        resultEl.innerText = `> ${data.message}`;
        resultEl.style.color = data.won ? "var(--accent)" : "#ff4444";
    }

    await sleep(1800);
    cerrarModalCombate();

    if (data) {
        const sprite = document.getElementById("pet-sprite");

        if (data.codepet && data.codepet !== codepetAntes) {
            if (spriteOverrideTimeout)  { clearTimeout(spriteOverrideTimeout);   spriteOverrideTimeout  = null; }
            if (spriteOverrideInterval) { clearInterval(spriteOverrideInterval); spriteOverrideInterval = null; }
            detenerCaminata();
            sprite.setAttribute("data-pet", data.codepet);
            sprite.src = `/static/assets/sprites/${data.codepet}/walk1.png`;
            iniciarCaminata(data.codepet);
            mostrarModalEvolucion(data, (data.evolutions || []).length === 0);
        }

        actualizarInterfaz(data);
    }

    await tick();
    actualizarHistorial();
}

// --- HISTORIAL DE BATALLAS ---

async function actualizarHistorial() {
    try {
        const res = await fetch("/api/battle-history");
        const batallas = await res.json();
        const list = document.getElementById("battle-history-list");

        if (!batallas.length) {
            list.innerHTML = "<p class='evo-req'>Sin batallas aún.</p>";
            return;
        }

        list.innerHTML = batallas.map(b => {
            const fecha = new Date(b.timestamp * 1000);
            const hora  = fecha.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
            return `
                <div class="history-entry">
                    <span class="history-result ${b.won ? 'win' : 'loss'}">${b.won ? "▲ VIC" : "▼ DER"}</span>
                    <span class="history-meta">${b.enemy}</span>
                    <span class="history-meta">${b.zone}</span>
                    <span class="history-meta">${b.won ? "+" + b.xp_gained + " XP" : "-1 HP"} · ${hora}</span>
                </div>`;
        }).join("");
    } catch (e) {}
}

// --- BASURA ---

let prevWaste = 0;

function renderBasura(waste) {
    const container = document.getElementById("waste-container");
    const prev = parseInt(container.dataset.waste || "0");
    container.dataset.waste = waste;

    // Notificar si aparece basura nueva
    if (waste > prev) {
        setLog("¡Hay archivos basura! Usa clean.", "#ff4444");
    }

    // Reconstruir iconos solo si cambió
    if (prev === waste) return;
    container.innerHTML = Array.from({ length: waste }, () =>
        `<img class="waste-icon" src="/static/assets/sprites/ui/waste.png" alt="waste">`
    ).join("");

    // Destacar botón clean cuando hay basura
    const btnClean = document.querySelector("[data-action='clean']");
    if (btnClean) btnClean.classList.toggle("btn-alert", waste > 0);
}

// --- EVOLUCIONES ---

function req(ok, label) {
    return `<span class="evo-req ${ok ? 'req-ok' : ''}">${label}: ${ok ? '✓' : '✗'}</span>`;
}

function renderEvoluciones(evolutions) {
    const list = document.getElementById("evo-list");
    if (!list) return;

    if (evolutions.length === 0) {
        list.innerHTML = "<p class='evo-req'>Sin evoluciones disponibles.</p>";
        return;
    }

    list.innerHTML = evolutions.map(evo => `
        <div class="evo-card ${evo.can_evolve ? 'evo-ready' : ''}">
            <img class="evo-sprite" src="/static/assets/sprites/${evo.target}/idle.png" alt="${evo.target}">
            <div class="evo-info">
                <span class="evo-name">${evo.target}</span>
                ${req(evo.level_ok, 'lvl max')}
                ${evo.min_strength > 0 ? req(evo.strength_ok, `str ≥ ${evo.min_strength}`) : ''}
                ${evo.min_speed    > 0 ? req(evo.speed_ok,    `spd ≥ ${evo.min_speed}`)    : ''}
            </div>
        </div>
    `).join('');
}

// --- MODAL EVOLUCIÓN ---

function mostrarModalEvolucion(state, esFinal) {
    document.getElementById("evo-modal-sprite").src =
        `/static/assets/sprites/${state.codepet}/idle.png`;
    document.getElementById("evo-modal-name").innerText = state.codepet;

    if (esFinal) {
        document.getElementById("evo-modal-title").innerText = "> ¡FORMA FINAL ALCANZADA!";
        document.getElementById("evo-modal-msg").innerText =
            `${state.name} ha alcanzado su evolución definitiva.\n¡Enhorabuena!`;
    } else {
        document.getElementById("evo-modal-title").innerText = "> ¡evolución!";
        document.getElementById("evo-modal-msg").innerText =
            `${state.name} ha evolucionado.\n¡Sigue entrenando!`;
    }

    document.getElementById("evo-modal").classList.remove("hidden");
}

// --- ACCIONES SIMPLES ---

function setLog(msg, color = "var(--accent)") {
    const el = document.getElementById("log-output");
    el.style.color = color;
    el.innerText = `> ${msg}`;
}

async function accionSimple(endpoint) {
    try {
        const res = await fetch(endpoint, { method: "POST" });
        const data = await res.json();
        setLog(data.message, data.success ? "var(--accent)" : "#ff4444");
        if (data.success && (endpoint === "/api/feed" || endpoint === "/api/heal")) {
            const codepet = document.getElementById("pet-sprite").getAttribute("data-pet");
            mostrarSpriteTemp(codepet, "happy");
        }
        actualizarInterfaz(data);
    } catch (e) {
        setLog("Error de conexión.", "#ff4444");
    }
}

// --- TIEMPO ---

async function tick() {
    const res = await fetch("/api/tick", { method: "POST" });
    const state = await res.json();
    actualizarInterfaz(state);
}

// --- INICIO ---

document.addEventListener("DOMContentLoaded", () => {
    const sprite = document.getElementById("pet-sprite");
    const codepet = sprite.getAttribute("data-pet");

    if (codepet && codepet !== "dead") {
        sprite.src = `/static/assets/sprites/${codepet}/walk1.png`;
        iniciarCaminata(codepet);
    }

    tick();
    setInterval(tick, 5000);
    actualizarHistorial();

    // Nombre inicial
    const btnName = document.getElementById("btn-confirm-name");
    if (btnName) {
        const confirmarNombre = async () => {
            const nombre = document.getElementById("name-input").value.trim();
            if (!nombre) return;
            const res = await fetch("/api/set-name", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: nombre })
            });
            const data = await res.json();
            if (data.success) {
                document.getElementById("name-modal").classList.add("hidden");
                actualizarInterfaz(data);
            }
        };
        btnName.addEventListener("click", confirmarNombre);
        document.getElementById("name-input").addEventListener("keydown", e => {
            if (e.key === "Enter") confirmarNombre();
        });
        // Foco automático si el modal está visible
        if (!document.getElementById("name-modal").classList.contains("hidden")) {
            document.getElementById("name-input").focus();
        }
    }

    document.getElementById("btn-close-evo").addEventListener("click", () => {
        document.getElementById("evo-modal").classList.add("hidden");
    });

    // Nueva partida al morir
    const terminalScreen = document.getElementById("terminal-screen");

    const iniciarNuevaPartida = async () => {
        if (!terminalScreen.classList.contains("dead")) return;
        const res = await fetch("/api/new-game", { method: "POST" });
        const state = await res.json();
        actualizarInterfaz(state);
        document.getElementById("name-modal").classList.remove("hidden");
        document.getElementById("name-input").value = "";
        document.getElementById("name-input").focus();
    };

    terminalScreen.addEventListener("click", iniciarNuevaPartida);

    document.addEventListener("keydown", (e) => {
        if (e.code === "Space" && minigameRunning) {
            e.preventDefault();
            if (!document.getElementById("fight-modal").classList.contains("hidden")) {
                resolverCombate();
            } else {
                resolverMinijuego();
            }
        } else if (e.code === "Space" && terminalScreen.classList.contains("dead")) {
            e.preventDefault();
            iniciarNuevaPartida();
        }
    });

    // Botones simples
    document.querySelector("[data-action='feed']").addEventListener("click",  () => accionSimple("/api/feed"));
    document.querySelector("[data-action='clean']").addEventListener("click", () => accionSimple("/api/clean"));
    document.querySelector("[data-action='heal']").addEventListener("click",  () => accionSimple("/api/heal"));

    // Botón train
    document.querySelector("[data-action='train']").addEventListener("click", abrirModalEntrenamiento);

    // Elegir stat → iniciar minijuego de entrenamiento
    document.querySelectorAll("[data-stat]").forEach(btn => {
        btn.addEventListener("click", () => {
            selectedStat = btn.getAttribute("data-stat");
            document.getElementById("train-step-select").classList.add("hidden");
            document.getElementById("train-step-game").classList.remove("hidden");
            iniciarMinijuego("train-minigame-zone", "train-minigame-cursor");
        });
    });

    document.getElementById("btn-cancel-train").addEventListener("click", cerrarModalEntrenamiento);

    // Botón fight
    document.querySelector("[data-action='fight']").addEventListener("click", abrirModalCombate);
    document.getElementById("btn-cancel-fight").addEventListener("click", cerrarModalCombate);

});
