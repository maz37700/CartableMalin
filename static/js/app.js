// ============================================================
// CartableMalin — JavaScript principal
// ============================================================

/**
 * Coche ou décoche un item de matériel.
 * Met à jour visuellement la case + envoie au serveur.
 */
async function toggleItem(el) {
    const nom = el.dataset.nom;
    const wasDone = el.classList.contains('done');
    const newDone = !wasDone;

    // Mise à jour visuelle immédiate (optimiste)
    el.classList.toggle('done');
    el.classList.add('pop');
    setTimeout(() => el.classList.remove('pop'), 300);

    const checkbox = el.querySelector('.checkbox');
    checkbox.textContent = newDone ? '✓' : '';

    // Envoi au serveur
    try {
        const r = await fetch('/sac/cocher', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ nom, coche: newDone })
        });
        const data = await r.json();

        if (data.ok && data.progression !== undefined) {
            updateProgression(data.progression);
        }
    } catch (e) {
        // En cas d'erreur, on revient à l'état précédent
        el.classList.toggle('done');
        checkbox.textContent = wasDone ? '✓' : '';
        console.error('Erreur lors de la mise à jour :', e);
    }
}

/**
 * Met à jour visuellement la barre de progression et le compteur.
 */
function updateProgression(pourcent) {
    const items = document.querySelectorAll('.item');
    const total = items.length;
    const coches = document.querySelectorAll('.item.done').length;

    const numEl = document.getElementById('prog-num');
    const percentEl = document.getElementById('prog-percent');
    const fillEl = document.getElementById('prog-fill');

    if (numEl) numEl.textContent = `${coches} / ${total}`;
    if (percentEl) percentEl.textContent = `${pourcent}% prêt`;
    if (fillEl) fillEl.style.width = pourcent + '%';

    // Si tout est coché, on affiche le message de félicitations
    const allDone = document.getElementById('all-done');
    if (allDone) {
        if (total > 0 && coches === total) {
            allDone.style.display = 'block';
            // Petite animation de fête
            celebrate();
        } else {
            allDone.style.display = 'none';
        }
    }
}

/**
 * Petite animation de fête (confettis simples) quand tout est prêt.
 */
function celebrate() {
    if (document.querySelector('.confetti-active')) return;

    const colors = ['#FF5C5C', '#F4B860', '#6BBE8C', '#2E3192'];
    const container = document.createElement('div');
    container.className = 'confetti-active';
    container.style.cssText = 'position:fixed; inset:0; pointer-events:none; z-index:1000; overflow:hidden;';
    document.body.appendChild(container);

    for (let i = 0; i < 30; i++) {
        const c = document.createElement('div');
        const color = colors[Math.floor(Math.random() * colors.length)];
        const left = Math.random() * 100;
        const delay = Math.random() * 0.5;
        const duration = 1.5 + Math.random() * 1.5;

        c.style.cssText = `
            position:absolute;
            top:-20px;
            left:${left}%;
            width:8px; height:14px;
            background:${color};
            opacity:0.8;
            border-radius:2px;
            animation: confetti-fall ${duration}s ${delay}s linear forwards;
        `;
        container.appendChild(c);
    }

    setTimeout(() => container.remove(), 4000);
}

// Ajout de l'animation CSS pour les confettis
const confettiStyle = document.createElement('style');
confettiStyle.textContent = `
@keyframes confetti-fall {
    0% { transform: translateY(0) rotate(0deg); opacity: 0.8; }
    100% { transform: translateY(110vh) rotate(720deg); opacity: 0; }
}
`;
document.head.appendChild(confettiStyle);
