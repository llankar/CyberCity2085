"""Local command exchange for a single experimental combat session."""
import json
from pathlib import Path
from time import perf_counter

from game.combat.session_protocol import atomic_json
from tactical_preview import TacticalPreview


class TacticalMailbox:
    """Run one command per sequence and publish an atomic Python snapshot."""

    def __init__(self, directory: Path, preview: TacticalPreview, *, trace_timing: bool = False) -> None:
        self.directory = directory
        self.preview = preview
        self.trace_timing = trace_timing
        self.sequence = 0
        self.reply = {"sequence": 0, "state": preview.snapshot()}
        self._publish_reply()

    def _publish_reply(self) -> None:
        # Windows can deny replacement while Godot has the old reply open.
        # Each reply has a new filename and remains immutable after publishing.
        atomic_json(self.directory / f"reply-{self.sequence}.json", self.reply)

    def poll(self) -> bool:
        path = self.directory / f"command-{self.sequence + 1}.json"
        try:
            command = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return False
        if not isinstance(command, dict):
            return False
        action, actor = command.get("action"), command.get("actor")
        target = command.get("target")
        if not isinstance(action, str) or not isinstance(actor, str) or (
            target is not None and not isinstance(target, str)
        ):
            return False
        started = perf_counter() if self.trace_timing else 0.0
        result = self.preview.action(action, actor, target_id=target,
                                     destination=command.get("destination"))
        resolved = perf_counter() if self.trace_timing else 0.0
        self.sequence += 1
        self.reply = {"sequence": self.sequence, **result}
        self._publish_reply()
        if self.trace_timing:
            print(f"TACTICAL_ENGINE action={action} sequence={self.sequence} "
                  f"resolve_ms={(resolved-started)*1000:.2f} "
                  f"publish_ms={(perf_counter()-resolved)*1000:.2f}", flush=True)
        return True
