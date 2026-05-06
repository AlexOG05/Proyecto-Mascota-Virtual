
function actualizarInterfaz(state) {
    const terminalScreen = document.getElementById("terminal-screen");

    // 1. Comprobar muerto
    if (state.hp <= 0) {
        terminalScreen.classList.add("dead");
        detenerCaminata(); // Si estaba caminando, lo paramos
        desactivarBotones(true);
        return; // Salimos para no actualizar nada más
    } else {
        terminalScreen.classList.remove("dead");
        desactivarBotones(false);
    }

    // 2. Actualizar estadísticas
    updatePips("stat-hp", state.hp);
    updatePips("stat-hunger", state.hunger);
    updatePips("stat-waste", state.waste);
    updatePips("stat-stage", state.stage);

    // 3. ACTUALIZAR BARRAS (Porcentajes)
    updateBar("stat-energy", state.energy);
    updateBar("stat-combat-hp", state.combat_hp);
    updateBar("stat-strength", state.strength);
    updateBar("stat-speed", state.speed);

    // 4. ACTUALIZAR TEXTOS
    document.getElementById("stat-xp").innerText = state.xp;
    
    // 5. ACTUALIZAR SPRITE (Por si evolucionó)
    const petSprite = document.getElementById("pet-sprite");
    petSprite.setAttribute("data-pet", state.codepet); 
    if (!isWalking) {
        petSprite.src = `/static/assets/sprites/${state.pet_type}/idle.png`;
    }
}

function muerteCodepet(state) {
    const terminalScreen = document.getElementById("terminal-screen");

    // Si la vida vital llega a 0, activamos la clase "dead"
    if (state.hp <= 0) {
        terminalScreen.classList.add("dead");
        
        // Desactivamos los botones de acción para que el jugador no pueda hacer nada más
        document.querySelectorAll(".game-actions button").forEach(btn => btn.disabled = true);
        
        return; // Salimos de la función para no actualizar nada más
    } 
    
    // Si la mascota está viva (por si implementas un reinicio), quitamos la clase
    terminalScreen.classList.remove("dead");
    document.querySelectorAll(".game-actions button").forEach(btn => btn.disabled = false);

    // ... (Aquí iría el resto de tu código para actualizar las barras de vida, hambre, etc.)
}