"""Local command exchange for a single experimental combat session."""
import json
from pathlib import Path

from game.combat.session_protocol import atomic_json
from tactical_preview import TacticalPreview


class TacticalMailbox:
    """Run one command per sequence and publish an atomic Python snapshot."""

    def __init__(self, directory: Path, preview: TacticalPreview) -> None:
        self.directory = directory
        self.preview = preview
        self.sequence = 0
        self.reply_path = directory / "reply.json"
        self.reply = {"sequence": 0, "state": preview.snapshot()}
        atomic_json(self.reply_path, self.reply)

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
        result = self.preview.action(action, actor, target_id=target,
                                     destination=command.get("destination"))
        self.sequence += 1
        self.reply = {"sequence": self.sequence, **result}
        atomic_json(self.reply_path, self.reply)
        return True
