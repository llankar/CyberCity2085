"""Battle-owned, phase-stable enemy targets and visible interruption reasons."""

from dataclasses import dataclass, replace

from .battlefield import trace_sight_line
from .tactical_identity import EnemyIntent, predict_enemy_intent
from .command_network import CORPORATE_DOCTRINES, command_link_active, linked_commander
from .tactical_identity import profile_for_theme, tactical_target_score, _target_name
from .pack_maneuvers import BUDDY_DISTANCE, buddy_distance, isolated_target, neighbors, bounded
from .mutant_control import can_project, reserve_projection
from .precision_orders import lock_valid, reserve_precision
from .pack_maneuvers import approach_step, route_step


@dataclass
class ReservedOrder:
    intent: EnemyIntent
    interrupted: str = ""
    target_position: tuple[int, int] | None = None
    ap_penalty: int = 0


class EnemyOrders:
    """One book per battle; no cross-battle globals or campaign mutation.

    Orders reserve a target and movement priority, not a guaranteed hit. A phase
    refresh is explicit; ordinary health/position/score changes do not retarget.
    """

    def __init__(self):
        self.orders: dict[int, ReservedOrder] = {}
        self._next_targets: dict[int, object] = {}

    def _stage_defensive_breaches(self, enemies, objective):
        """Keep a defended-zone push readable instead of rushing the full roster."""
        if objective is None or getattr(objective, "kind", "") != "defend":
            return
        living_orders = [enemy for enemy in enemies if enemy.health > 0 and id(enemy) in self.orders]
        breachers = [enemy for enemy in living_orders
                     if self.orders[id(enemy)].intent.action == "BREACH"
                     and self.orders[id(enemy)].intent.target is None]
        danger = lambda enemy: (enemy.distance_to(objective), enemy.position)
        limit = min(2, max(1, (len(living_orders) + 2) // 3))
        if len(breachers) <= limit:
            return
        active = {id(enemy) for enemy in sorted(breachers, key=danger)[:limit]}
        for enemy in breachers:
            if id(enemy) not in active:
                order = self.orders[id(enemy)]
                order.intent = replace(
                    order.intent, action="HOLD", target=None, target_name="breach reserve",
                    rationale="BREACH WAVE: screen the active push; advance when a lane opens",
                )
                order.target_position = None

    def reserve(self, enemies, allies, objective, cover_nodes, *, refresh=False, can_enter=None, terrain_profile=None):
        if refresh:
            self.orders.clear()
            alive = {id(enemy) for enemy in enemies if enemy.health > 0}
            self._next_targets = {key: target for key, target in self._next_targets.items() if key in alive}
        added = []
        for enemy in enemies:
            if enemy.health <= 0 or id(enemy) in self.orders:
                continue
            deferred = self._next_targets.pop(id(enemy), None) if refresh else None
            valid_deferred = deferred is not None and deferred.health > 0 and any(unit is deferred for unit in allies)
            intent = predict_enemy_intent(enemy, [deferred] if valid_deferred else allies, objective=objective)
            if valid_deferred:
                if intent.action == "BREACH" and intent.target is None:
                    intent = replace(intent, action="HUNT", target=deferred, target_name=_target_name(deferred),
                                     rationale="Clear a reachable threat before returning to the blocked objective")
                intent = replace(intent, rationale=f"REORIENTED after blocked approach: {intent.rationale}")
            if profile_for_theme(enemy.enemy_theme).key == "raider" and intent.target is not None and not valid_deferred:
                isolated = isolated_target(enemy, allies, tactical_target_score)
                target = isolated or intent.target
                intent = replace(intent, action="ISOLATE" if isolated is not None else "SKIRMISH",
                                 target=target, target_name=_target_name(target),
                                 rationale="Hunt isolation; fire and reposition with remaining AP")
            if intent.action in {"FIRE", "STRIKE"} and intent.target is not None:
                if not trace_sight_line(enemy.position, intent.target.position, cover_nodes).clear:
                    intent = replace(intent, action="HUNT", rationale="Find a clear firing lane")
            intent = reserve_projection(enemy, intent, objective, cover_nodes)
            self.orders[id(enemy)] = ReservedOrder(intent, target_position=intent.target.position if intent.target is not None else None)
            added.append(enemy)
        claimed = {order.intent.destination for order in self.orders.values() if order.intent.destination is not None}
        occupied = {unit.position for unit in [*enemies, *allies] if unit.health > 0}
        width = getattr(terrain_profile, "width", max(1280, max((cell[0]+64 for cell in occupied), default=1280)))
        height = getattr(terrain_profile, "height", max(720, max((cell[1]+64 for cell in occupied), default=720)))
        blocked = {(node.world_x, node.world_y) for node in cover_nodes or () if not node.passable}
        for enemy in added:
            intent = self.orders[id(enemy)].intent
            if profile_for_theme(enemy.enemy_theme).key != "starver" or intent.target is None:
                continue
            if enemy.distance_to(intent.target) <= 32:
                continue
            candidates = [cell for cell in neighbors(intent.target.position)
                          if bounded(cell, width, height) and cell not in claimed
                          and (cell == enemy.position or cell not in occupied)
                          and (cell == enemy.position or can_enter is None or can_enter(*cell))
                          and not any(not node.passable and (node.world_x, node.world_y) == cell for node in cover_nodes or ())]
            def legal(x, y):
                cell = (x, y)
                return (cell not in blocked and (cell == enemy.position or cell not in occupied)
                        and (can_enter is None or can_enter(x, y)))
            candidates.sort(key=lambda cell: (abs(cell[0]-enemy.position[0])+abs(cell[1]-enemy.position[1]), cell))
            goal = next((cell for cell in candidates if cell == enemy.position or
                         route_step(enemy.position, cell, legal, width=width, height=height,
                                    max_visits=min(4096, (width//32+1)*(height//32+1))) is not None), None)
            if goal is not None:
                claimed.add(goal)
                self.orders[id(enemy)].intent = replace(intent, action="SWARM", destination=goal,
                                                       rationale="Reserve a distinct melee approach; no free movement")
        # Reserve all leaders before assigning followers, independent of list order.
        for enemy in added:
            if profile_for_theme(enemy.enemy_theme).key not in CORPORATE_DOCTRINES:
                continue
            commander = linked_commander(enemy, enemies, cover_nodes)
            if commander is None or id(commander) not in self.orders:
                continue
            lead = self.orders[id(commander)].intent
            if lead.action == "HOLD":
                continue
            action = "FOCUS" if lead.target is not None else lead.action
            if (enemy.enemy_subtype == "heavy" and lead.target is not None
                    and enemy.attack_range > 1
                    and 32 < enemy.distance_to(lead.target) <= enemy.attack_range * 32
                    and trace_sight_line(enemy.position, lead.target.position, cover_nodes).clear):
                action = "SUPPRESS"
            self.orders[id(enemy)].intent = replace(
                self.orders[id(enemy)].intent, action=action, target=lead.target,
                target_name=lead.target_name, coordinator=commander,
                rationale=f"COMMAND LINK: {action} {lead.target_name}; heavy suppression costs 2 AP",
            )

        # Preserve corporate shared targets before adding specialist windups.
        for enemy in added:
            order = self.orders[id(enemy)]
            order.intent = reserve_precision(enemy, order.intent, cover_nodes)
            order.target_position = order.intent.target.position if order.intent.target is not None else None
        self._stage_defensive_breaches(enemies, objective)

    def interrupt(self, enemy, reason, allies, objective, cover_nodes, logs, *, can_enter=None, terrain_profile=None):
        order = self.orders.get(id(enemy))
        if order is None or (order.interrupted == reason and reason in {"status_impaired", "movement_blocked"}):
            return
        # Re-evaluate only on a named invalidation, never on ordinary score changes.
        self.orders.pop(id(enemy))
        self.reserve([enemy], allies, objective, cover_nodes, can_enter=can_enter, terrain_profile=terrain_profile)
        replacement = self.orders.get(id(enemy))
        if replacement is not None:
            if reason in {"status_impaired", "movement_blocked"}:
                replacement.intent = replace(replacement.intent, action="HOLD", target=None, target_name="position")
            elif reason == "line_blocked":
                replacement.intent = replace(replacement.intent, action="HUNT")
            elif reason in {"prey_moved", "approach_blocked"}:
                replacement.intent = replace(replacement.intent, action="RUSH", destination=None)
            elif reason == "cast_blocked":
                replacement.intent = replace(replacement.intent, action="HOLD", target=None,
                                             target_name="spoiled projection", destination=None)
            if order.intent.action == "LOCK" and reason not in {"status_impaired", "movement_blocked"}:
                replacement.intent = replace(replacement.intent, action="HUNT", destination=None,
                                             coordinator=None)
                replacement.ap_penalty = 1
            replacement.interrupted = reason
            replacement.intent = replace(
                replacement.intent,
                rationale=f"INTERRUPTED ({reason}): {replacement.intent.rationale}",
            )
        logs.append(f"Enemy plan interrupted: {enemy.enemy_theme} / {reason}")
        if reason == "movement_blocked" and (order.intent.target is not None or order.intent.action == "BREACH"):
            blocked = {(node.world_x, node.world_y) for node in cover_nodes or () if not node.passable}
            def legal(x, y):
                return (x, y) not in blocked and (can_enter is None or can_enter(x, y))
            candidates = sorted((unit for unit in allies if unit.health > 0 and unit is not order.intent.target),
                                key=lambda unit: tactical_target_score(enemy, unit), reverse=True)
            width = getattr(terrain_profile, "width", max(1280, enemy.position[0]+64, *(unit.position[0]+64 for unit in allies)))
            height = getattr(terrain_profile, "height", max(720, enemy.position[1]+64, *(unit.position[1]+64 for unit in allies)))
            for candidate in candidates:
                if enemy.distance_to(candidate) <= 32 or approach_step(enemy, candidate, legal, width=width, height=height) is not None:
                    self._next_targets[id(enemy)] = candidate
                    logs.append("Enemy approach blocked: alternate target will be announced next player phase")
                    break

    def reconcile(self, enemies, allies, objective, cover_nodes, logs, *, can_enter=None, terrain_profile=None):
        self.reserve(enemies, allies, objective, cover_nodes, can_enter=can_enter, terrain_profile=terrain_profile)
        alive = {id(enemy) for enemy in enemies if enemy.health > 0}
        for key in list(self.orders):
            if key not in alive:
                self.orders.pop(key)
        for enemy in enemies:
            order = self.orders.get(id(enemy))
            if order is None:
                continue
            intent = order.intent
            reason = ""
            if any(status in enemy.status_effects for status in ("suppressed", "stunned", "panicked")):
                reason = "status_impaired"
            elif intent.coordinator is not None and not command_link_active(enemy, intent.coordinator, enemies, cover_nodes):
                reason = "command_lost"
            elif intent.target is not None and (
                intent.target.health <= 0 or not any(unit is intent.target for unit in allies)
            ):
                reason = "target_lost"
            elif intent.action == "ISOLATE" and intent.target is not None and buddy_distance(intent.target, allies) <= BUDDY_DISTANCE:
                reason = "squad_regrouped"
            elif intent.action == "TOXIN" and not can_project(enemy, intent.destination, cover_nodes):
                reason = "cast_blocked"
            elif intent.action == "LOCK" and not lock_valid(enemy, intent.target, intent.destination, cover_nodes):
                reason = "lock_broken"
            elif intent.action == "SWARM" and intent.destination is not None and intent.target is not None and intent.target.position != order.target_position:
                reason = "prey_moved"
            elif intent.action == "SWARM" and intent.destination is not None and intent.destination != enemy.position and can_enter is not None and not can_enter(*intent.destination):
                reason = "approach_blocked"
            elif intent.action == "BREACH" and intent.target is None and bool(getattr(objective, "completed", False)):
                reason = "objective_completed"
            elif intent.action == "SUPPRESS" and intent.target is not None and enemy.distance_to(intent.target) > enemy.attack_range * 32:
                reason = "target_repositioned"
            elif intent.action in {"FIRE", "STRIKE", "FOCUS", "SUPPRESS"} and intent.target is not None:
                if not trace_sight_line(enemy.position, intent.target.position, cover_nodes).clear:
                    reason = "line_blocked"
            if reason:
                self.interrupt(enemy, reason, allies, objective, cover_nodes, logs, can_enter=can_enter, terrain_profile=terrain_profile)

    def intents(self, enemies):
        return [self.orders[id(enemy)].intent for enemy in enemies
                if id(enemy) in self.orders and enemy.health > 0 and getattr(enemy, "visible", True)]
