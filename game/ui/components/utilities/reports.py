"""Campaign outcome presentations. All facts come from the existing view models."""

from game.ui.components.utilities.shell import UtilityDeck
from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.visual import CYAN, GOLD, MINT, RED, TEXT, MUTED


def report_lines(value, level=0):
    """Readable recursive document; retain nested campaign details without repr blobs."""
    lines = []
    if isinstance(value, dict):
        for key, item in value.items():
            if item is None or item == [] or item == {} or item == "":
                continue
            title = str(key).replace("_", " ").upper()
            if isinstance(item, (dict, list, tuple)):
                lines.append(title)
                lines.extend(report_lines(item, level + 1))
                lines.append("")
            else:
                lines.append(f"{title}: {item}")
    elif isinstance(value, (list, tuple)):
        for item in value:
            lines.extend(report_lines(item, level))
    else:
        lines.append(str(value))
    return lines


class ReportDeck(UtilityDeck):
    def promotion(self, v):
        if v._index >= len(v.promotions):
            v._advance()
            return
        self.gs = v.game_state
        rec = v.promotions[v._index]
        c = rec.character
        self.start(
            v,
            "PROMOTION / OPERATIVE DOSSIER",
            f"{v._index+1} / {len(v.promotions)}",
            fractions=(0.42, 0.58),
        )
        u = self.u
        left, right = self.layout.columns
        self.paint.panel(left, GOLD, selected=True)
        from game.ui.portraits import portrait_path_for_character

        self.image(
            rec.portrait_path or portrait_path_for_character(c),
            Rect(
                left.left + 8 * u,
                left.bottom + 8 * u,
                left.right - 8 * u,
                left.top - 8 * u,
            ),
        )
        self.badge(
            c.name.upper(),
            Rect(
                left.left + 18 * u,
                left.bottom + 20 * u,
                left.right - 18 * u,
                left.bottom + 75 * u,
            ),
            GOLD,
        )
        self.panel(
            right, "AGENT PROGRESSION", "squad"
        )
        r = self.body(right)
        self.label(
            c.name.upper(), r.left, r.top - 30 * u, 44, TEXT, bold=True, width=r.width
        )
        self.label(
            f'{getattr(c,"role","")}'.upper(),
            r.left,
            r.top - 79 * u,
            23,
            CYAN,
            width=r.width,
        )
        self.badge(
            f"LVL {rec.old_level}  >>  LVL {rec.new_level}",
            Rect(r.left, r.top - 167 * u, r.right, r.top - 110 * u),
            GOLD,
        )
        stats = c.stats
        items = [
            ("HP", stats.max_hp),
            ("STR", stats.str),
            ("AGI", stats.agi),
            ("PSI", stats.psi),
        ]
        width = (r.width - 30 * u) / 4
        for i, (key, value) in enumerate(items):
            self.stat(
                Rect(
                    r.left + i * (width + 10 * u),
                    r.top - 307 * u,
                    r.left + i * (width + 10 * u) + width,
                    r.top - 202 * u,
                ),
                key,
                value,
                "chip",
                color=CYAN,
            )
        points = getattr(c, "pending_stat_points", getattr(c, "pending_points", 0))
        talent = getattr(c, "talent_points", 0)
        self.document(
            "promotion",
            "AVAILABLE POINTS"
            + f"\n{points}\n\n"
            + "TALENT POINTS"
            + f"\n{talent}",
            Rect(r.left, r.bottom, r.right, r.top - 340 * u),
            22,
        )
        self.footer("CONTINUE [ENTER]", hint="TAB / ARROWS · SPACE TO SELECT")
        self.end()
        last = v._hits[-1]
        v._continue_rect = (last.left, last.bottom, last.right, last.top)

    def ending(self, v):
        self.gs = v.game_state
        self.start(
            v,
            "CAMPAIGN COMPLETE",
            str(v.summary.get("resolved_day", "")),
            fractions=(0.34, 0.33, 0.33),
        )
        left, center, right = self.layout.columns
        u = self.u
        self.panel(
            left, "THE CITY REMEMBERS", "target"
        )
        r = self.body(left)
        self.image(
            "assets/ui/title_background.png",
            Rect(r.left, r.top - r.height * 0.42, r.right, r.top),
        )
        self.document(
            "ending_summary",
            str(v.summary.get("title", ""))
            + "\n\n"
            + str(v.summary.get("summary", "")),
            Rect(r.left, r.bottom, r.right, r.top - r.height * 0.45),
            20,
        )
        for name, title, rect, lines in [
            (
                "world",
                "THE WORLD",
                center,
                v.summary.get("world_lines", []),
            ),
            (
                "agents",
                "THE AGENTS",
                right,
                v.summary.get("agent_epilogues", []),
            ),
        ]:
            self.panel(rect, title, "journal" if name == "world" else "squad")
            self.document(name, "\n\n".join(map(str, lines)), self.body(rect), 19)
        self.footer("RETURN TO TITLE [ENTER]", hint="TAB / ARROWS · SPACE TO SELECT")
        self.end()

    def debrief(self, v):
        from game.ui.screens.battle_debrief_view import (
            build_battle_debrief_summary,
            build_consequence_summary_lines,
        )

        self.gs = v.game_state
        summary = build_battle_debrief_summary(
            v.game_state, v.victory, v.mission, v.agent_stats, v.triggered_complication
        )
        title = (
            "MISSION COMPLETE"
            if v.victory
            else "MISSION FAILED"
        )
        if summary.get("outcome")=="retreat":title="TACTICAL RETREAT"
        self.start(
            v, title, getattr(v.mission, "title", ""), fractions=(0.37, 0.30, 0.33)
        )
        left, center, right = self.layout.columns
        u = self.u
        self.panel(
            left, "SQUAD / PERFORMANCE", "squad"
        )
        r = self.body(left)
        for i, stat, card in self.page("debrief_agents", v.agent_stats, r, 151):
            self.paint.panel(card, RED if stat.kia else CYAN)
            self.image(
                stat.portrait_path,
                Rect(
                    card.left + 8 * u,
                    card.bottom + 8 * u,
                    card.left + 102 * u,
                    card.top - 8 * u,
                ),
            )
            x = card.left + 115 * u
            self.label(
                stat.name.upper(),
                x,
                card.top - 22 * u,
                23,
                TEXT,
                bold=True,
                width=card.right - x - 12 * u,
            )
            self.label(
                stat.role.upper() + (" / KIA" if stat.kia else "") + (f" / HP {stat.hp_remaining}/{stat.max_hp_at_extraction}" if stat.hp_remaining is not None else ""),
                x,
                card.top - 50 * u,
                15,
                RED if stat.kia else CYAN,
                width=card.right - x - 12 * u,
            )
            self.label(
                f"DMG {stat.damage_dealt if stat.damage_dealt is not None else '—'} / −{stat.damage_taken if stat.damage_taken is not None else '—'} · KILLS {stat.kills if stat.kills is not None else '—'}",
                x,
                card.top - 77 * u,
                16,
                TEXT,
                width=card.right - x - 12 * u,
            )
            self.label(
                f"AP {stat.actions_used if stat.actions_used is not None else '—'} · XP +{stat.xp_gained} · STRESS {stat.stress_delta:+}",
                x,
                card.top - 105 * u,
                15,
                GOLD,
                width=card.right - x - 12 * u,
            )
            self.hit(card, "report_agent", i, " / ".join(stat.injuries))
        self.panel(
            center,
            "OBJECTIVES / CONSEQUENCES",
            "target",
        )
        body = self.body(center)
        status = Rect(body.left, body.top - 42 * u, body.right, body.top)
        accent = MINT if v.victory else GOLD
        self.paint.panel(status, accent)
        self.label(summary["objective_result"], status.left + 12 * u,
                   status.center[1], 17, accent, bold=True, width=status.width - 24 * u)
        lines = build_consequence_summary_lines(
            v.game_state, v.victory, v.mission, v.agent_stats, v.triggered_complication
        )
        self.document("outcome", "\n".join(lines),
                      Rect(body.left, body.bottom, body.right, status.bottom - 12 * u), 17,
                      headings={line for line in lines if line.isupper()})
        self.panel(
            right,
            "REPORT / AGENT STATUS",
            "journal",
        )
        r = self.body(right)
        selected = self.selection.get("report_agent")
        if selected is not None and 0 <= selected < len(summary["agent_rows"]):
            agent = summary["agent_rows"][selected]
            details = [agent["name"], f'{agent["role"].title()} · {agent["status"].title()}']
            for field, label in (("hp_remaining", "Health"), ("kills", "Kills"),
                                 ("damage_dealt", "Damage dealt"), ("damage_taken", "Damage taken"),
                                 ("xp_gained", "XP gained"), ("stress_delta", "Stress change")):
                if agent[field] is not None:
                    value = agent[field]
                    if field == "hp_remaining" and agent["max_hp_at_extraction"] is not None:
                        value = f'{value}/{agent["max_hp_at_extraction"]}'
                    details.append(f"{label}  {value}")
            details.extend(agent["injuries"])
            details.extend(tag.replace("_", " ").title() for tag in agent["reputation"])
            self.document(
                "agent_report",
                "\n".join(details),
                Rect(r.left, r.bottom + 65 * u, r.right, r.top),
                18,
            )
            self.action(
                Rect(r.left, r.bottom, r.right, r.bottom + 44 * u),
                "MISSION REPORT",
                "report_mission",
            )
        else:
            from game.ui.components.squad_mission import mission_art_path

            self.image(
                mission_art_path(v.mission),
                Rect(r.left, r.top - 185 * u, r.right, r.top),
            )
            report = list(dict.fromkeys([
                *summary["narrative_consequences"],
                *getattr(v.game_state, "latest_agent_aftermath", []),
            ]))
            self.document(
                "after_report",
                "\n\n".join(report)
                or "No additional report. Select an operative to inspect their performance.",
                Rect(r.left, r.bottom, r.right, r.top - 205 * u),
                18,
            )
        self.footer("RETURN TO BASE [ENTER]", hint="TAB / ARROWS · SPACE TO SELECT")
        self.end()
        last = v._hits[-1]
        v._continue_rect = (last.left, last.bottom, last.right, last.top)
