"""Live mission pane for Squad Command; dispatches existing management actions."""

import arcade
from hashlib import sha1
from pathlib import Path
from game.deployment import build_tactical_briefing, selected_deployable_agents
from game.management.downtime import DOWNTIME_ACTIVITIES
from game.missions.flow import selected_mission
from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.typography import scale_font_size
from game.ui.screens.world_map import infer_world_map_site, mission_site_name
from .squad_style import CYAN, GOLD, MINT, RED, TEXT, MUTED


def mission_art_path(mission):
    """Use actual existing scene art, deterministically matched to mission context."""
    explicit = getattr(mission, "background_path", None)
    if isinstance(explicit, str) and Path(explicit).is_file():
        return explicit
    environment = str(getattr(mission, "battle_environment", "")).lower()
    district = str(getattr(mission, "district", "")).lower()
    folder = (
        "wasteland"
        if environment == "wasteland"
        or any(word in district for word in ("waste", "badland", "frontier"))
        else "city"
    )
    paths = sorted(Path("assets/missions/backgrounds", folder).glob("*.jpg"))
    if not paths:
        return None
    title = str(getattr(mission, "title", "")).lower()
    keywords = {
        "data": "data_vault",
        "extract": "rooftop",
        "medical": "clinic",
        "market": "market",
        "relay": "comms",
        "rescue": "safehouse",
    }
    for word, scene in keywords.items():
        matches = [p for p in paths if scene in p.stem]
        if word in title and matches:
            return str(matches[0])
    index = int(
        sha1(str(getattr(mission, "id", title)).encode()).hexdigest()[:8], 16
    ) % len(paths)
    return str(paths[index])


def draw_mission(self, r):
    u = self.u
    gs = self.gs
    mission = selected_mission(gs)
    self.panel(r, self.tr("active_mission"), "target")
    top = r.top - 58 * u
    left = r.left + 16 * u
    right = r.right - 16 * u
    width = right - left
    # Reserve every downtime row and the primary button before allocating art.
    dt_h = 90 * u
    cta_h = 47 * u
    dt = Rect(left, r.bottom + 12 * u, right, r.bottom + 12 * u + dt_h)
    cta = Rect(left, dt.top + 12 * u, right, dt.top + 12 * u + cta_h)
    if mission:
        title_label = self.text(
            mission.title.upper(),
            left,
            top + 3 * u,
            scale_font_size(24 * u),
            GOLD,
            bold=True,
            width=int(width),
            multiline=True,
            anchor_y="top",
            accessibility=False,
        )
        meta_y = top - title_label.content_height - 15 * u
        risk = (
            self.tr("risk." + str(mission.risk_level))
            if str(mission.risk_level) in ("1", "2", "3", "4", "5")
            else str(mission.risk_level)
        )
        self.label(
            self.tr("risk") + " " + risk,
            left,
            meta_y,
            13,
            RED,
            bold=True,
            width=width * 0.35,
        )
        self.label(
            f"¥ {mission.fund_reward:,}",
            left + width * 0.38,
            meta_y,
            15,
            CYAN,
            bold=True,
            width=width * 0.29,
        )
        self.label(
            self.tr("days", count=mission.duration_days),
            right,
            meta_y,
            13,
            TEXT,
            anchor_x="right",
        )
        objective_label = self.text(
            mission.objective_text,
            left,
            meta_y - 20 * u,
            scale_font_size(max(13, 13 * u)),
            TEXT,
            width=int(width),
            multiline=True,
            anchor_y="top",
            accessibility=False,
        )
        intel_line_height = max(20 * u, scale_font_size(max(13, 12 * u)) * 1.1)
        info_h = max(155 * u, 6 * intel_line_height + 26 * u)
        art_top = meta_y - 20 * u - objective_label.content_height - 12 * u
        art_bottom = cta.top + info_h + 17 * u
        art = Rect(left, art_bottom, right, max(art_bottom + 30 * u, art_top))
        self.image(mission_art_path(mission), art)
        arcade.draw_lrbt_rectangle_outline(
            art.left, art.right, art.bottom, art.top, (*CYAN, 190), 1.5
        )
        self.paint.glow(left + 30 * u, art.bottom + 18 * u, 100 * u, 24 * u, CYAN, 60)
        arcade.draw_lrbt_rectangle_filled(
            left + 4 * u,
            left + min(width * 0.6, 180 * u),
            art.bottom + 4 * u,
            art.bottom + 33 * u,
            (0, 13, 20, 220),
        )
        self.label(
            mission_site_name(infer_world_map_site(mission)),
            left + 12 * u,
            art.bottom + 18 * u,
            16,
            TEXT,
            bold=True,
            width=width * 0.65,
        )
        self.regions["mission_art"] = art
        y = art.bottom - 23 * u
        self.label(self.tr("tactical_intel"), left, y, 15, CYAN, bold=True, width=width)
        tactical = build_tactical_briefing(
            mission,
            selected_deployable_agents(gs.characters, gs.selected_agent_names),
        )
        lines = [
            (self.tr("enemy") + " " + tactical.enemy_label, GOLD),
            (self.tr("doctrine") + " " + tactical.doctrine, TEXT),
            (
                self.tr(
                    "assigned",
                    count=tactical.squad_count,
                    armed=tactical.armed_count,
                ),
                TEXT,
            ),
            (self.tr("kit") + " " + tactical.loadout_summary, TEXT),
            (
                self.tr("roles")
                + " "
                + tactical.capability_summary
                + " · "
                + tactical.tactical_gap,
                TEXT,
            ),
            (
                self.tr("recovery")
                + " "
                + self.tr("recovery." + tactical.recovery_load),
                GOLD,
            ),
        ]
        for line, color in lines:
            y -= intel_line_height
            self.label("• " + line, left + 3 * u, y, 12, color, width=width - 6 * u)
        self.hit(
            Rect(left, cta.top + 8 * u, right, art.bottom - 7 * u),
            "squad_intel",
            tooltip="\n".join(line for line, _ in lines),
        )
    else:
        self.label(self.tr("no_mission"), left, top - 35 * u, 18, MUTED, width=width)
    self.button(
        cta,
        self.tr("select_mission"),
        "open_mission_map",
        color=MINT,
        icon="right",
        primary=True,
    )
    arcade.draw_line(dt.left, dt.top, dt.right, dt.top, (*CYAN, 150), 1)
    self.label(self.tr("downtime"), dt.left, dt.top - 13 * u, 13, CYAN, bold=True)
    for i, activity in enumerate(DOWNTIME_ACTIVITIES):
        row_top = dt.top - (28 + i * 21) * u
        rect = Rect(dt.left, row_top - 20 * u, dt.right, row_top)
        label = self.tr("activity." + activity.key)
        detail = (
            self.tr("short_days", count=activity.days_cost)
            + f" -{activity.resource_cost} "
            + self.tr("resource_short." + activity.resource_key)
            + f"  M{activity.morale_delta:+} S{activity.stress_delta:+}"
        )
        self.label(
            f"{i+7}. {label}",
            rect.left + 3 * u,
            rect.center[1],
            12,
            TEXT,
            width=width * 0.47,
            bold=True,
        )
        self.label(
            detail,
            rect.right - 3 * u,
            rect.center[1],
            10.5,
            MUTED,
            width=width * 0.51,
            anchor_x="right",
        )
        self.hit(
            rect,
            "downtime_activity",
            i,
            f"{label} · {activity.days_cost}d · {activity.resource_cost} {activity.resource_key} · morale {activity.morale_delta:+} · stress {activity.stress_delta:+}",
        )
    self.regions["downtime"] = dt
