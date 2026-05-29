"""Generate roadmap documentation snippets from a prioritized backlog."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class BacklogTask:
    id: str
    title: str
    domain: str
    priority: int
    emotional_weight: int
    modularity_weight: int
    scope_weight: int


BACKLOG_TASKS: List[BacklogTask] = [
    BacklogTask("AGENT-01", "Créer des scènes de débrief narratif post-mission basées sur les conséquences.", "agent", 10, 10, 7, 8),
    BacklogTask("AGENT-02", "Ajouter des dialogues de soutien entre agents stressés dans la salle de récupération.", "agent", 10, 9, 8, 8),
    BacklogTask("MISSION-01", "Introduire des variantes d'objectifs multi-étapes avec embranchements lisibles.", "mission", 9, 7, 9, 7),
    BacklogTask("UI-01", "Afficher un fil narratif des événements récents dans le command center.", "ui", 8, 8, 8, 8),
    BacklogTask("TEST-01", "Couvrir la génération quotidienne de missions avec tests de régression supplémentaires.", "tests", 8, 6, 10, 9),
    BacklogTask("DOC-01", "Documenter les règles de conception centrées émotion et scope control.", "docs", 7, 6, 9, 10),
    BacklogTask("AGENT-03", "Ajouter un historique de liens mentor/protégé entre agents recrutés.", "agent", 9, 10, 8, 8),
    BacklogTask("MISSION-02", "Ajouter des complications dynamiques légères influencées par la pression district.", "mission", 8, 7, 8, 9),
    BacklogTask("UI-02", "Créer un panneau compact de moral d'escouade dans la vue RPG.", "ui", 8, 9, 8, 8),
    BacklogTask("TEST-02", "Valider la stabilité des seeds de mission par jour avec tests déterministes.", "tests", 7, 5, 10, 9),
    BacklogTask("DOC-02", "Ajouter des exemples de boucles émotionnelles agents dans la roadmap.", "docs", 7, 7, 8, 10),
    BacklogTask("AGENT-04", "Relier les blessures graves à des séquelles narratives temporaires.", "agent", 9, 10, 7, 8),
    BacklogTask("MISSION-03", "Créer une mission d'évacuation qui privilégie la survie des agents.", "mission", 8, 9, 8, 8),
    BacklogTask("UI-03", "Mettre en évidence les choix critiques affectant les relations d'équipe.", "ui", 8, 8, 8, 9),
    BacklogTask("TEST-03", "Ajouter des tests d'intégration sur stress/récupération/calendrier.", "tests", 8, 6, 10, 9),
    BacklogTask("DOC-03", "Décrire le pipeline backlog -> next steps -> roadmap dans docs.", "docs", 7, 5, 9, 10),
    BacklogTask("AGENT-05", "Ajouter des traits de personnalité qui modulent les logs de mission.", "agent", 9, 9, 8, 8),
    BacklogTask("MISSION-04", "Ajouter des récompenses narratives légères selon la faction ciblée.", "mission", 8, 8, 8, 9),
    BacklogTask("UI-04", "Afficher les tags de mission et l'impact émotionnel attendu au lancement.", "ui", 7, 8, 8, 9),
    BacklogTask("TEST-04", "Tester la cohérence des tags de domaine dans les exports markdown.", "tests", 7, 5, 10, 10),
    BacklogTask("DOC-04", "Créer une checklist de maintenabilité pour les nouvelles features.", "docs", 7, 5, 9, 10),
    # Mission View Professional Upgrade — Phase 1 (Visual Polish)
    BacklogTask("BATTLE-A01", "Créer un écran de briefing mission avant le lancement de la vue battle.", "battle", 10, 9, 8, 7),
    BacklogTask("BATTLE-P01", "Activer le pan caméra avec Shift+flèches et recentrage sur unité active.", "battle", 9, 6, 7, 6),
    BacklogTask("BATTLE-P02", "Ajouter des chiffres de dégâts flottants au-dessus des unités touchées.", "battle", 9, 8, 8, 7),
    BacklogTask("BATTLE-A02", "Ajouter une phase de déploiement pré-combat pour positionner les agents.", "battle", 9, 8, 8, 7),
    BacklogTask("BATTLE-A03", "Enrichir l'écran de débrief post-bataille avec stats par agent et récompenses.", "battle", 9, 9, 8, 7),
    BacklogTask("BATTLE-P03", "Passer la barre d'actions au format icône+label avec le design system.", "battle", 8, 7, 8, 7),
    BacklogTask("BATTLE-P04", "Ajouter un menu pause in-battle (Échap) avec résumé/paramètres/abandon.", "battle", 8, 6, 7, 7),
    BacklogTask("BATTLE-G01", "Câbler le pathfinding terrain à la walkability mask existante en combat.", "battle", 8, 5, 9, 8),
    BacklogTask("BATTLE-G02", "Améliorer l'IA ennemie avec recherche de couverture et flanquement.", "battle", 8, 6, 8, 8),
    BacklogTask("BATTLE-G03", "Activer des événements dynamiques mid-battle depuis complications.py.", "battle", 8, 8, 7, 8),
    BacklogTask("BATTLE-P05", "Promouvoir le panneau de log combat comme vue latérale accessible au joueur.", "battle", 7, 7, 8, 7),
    BacklogTask("BATTLE-G04", "Ajouter un système d'effets de statut (supprimé/saignement/étourdi) aux unités.", "battle", 7, 7, 8, 8),
]


def load_backlog() -> list[BacklogTask]:
    """Load backlog tasks from local constants."""
    return list(BACKLOG_TASKS)


def _task_score(task: BacklogTask) -> int:
    return (
        task.priority * 5
        + task.emotional_weight * 4
        + task.modularity_weight * 3
        + task.scope_weight * 2
    )


def compute_next_steps(limit: int = 20) -> list[BacklogTask]:
    """Compute the next most valuable coding steps with stable ordering."""
    ranked = sorted(
        load_backlog(),
        key=lambda task: (-_task_score(task), task.domain, task.id),
    )
    return ranked[:limit]


def render_markdown(steps: Iterable[BacklogTask]) -> str:
    """Render a stable markdown block for roadmap docs."""
    lines = ["## Next 20 Coding Steps", ""]
    for index, step in enumerate(steps, start=1):
        lines.append(f"{index}. [{step.domain}] {step.id} — {step.title}")
    lines.append("")
    return "\n".join(lines)


def write_docs(output_path: str = "docs/roadmap.md") -> Path:
    """Write generated markdown to the target roadmap file."""
    path = Path(output_path)
    generated = render_markdown(compute_next_steps(limit=20))
    path.write_text(generated, encoding="utf-8")
    return path


if __name__ == "__main__":
    output = write_docs()
    print(f"Generated next steps in {output}")
