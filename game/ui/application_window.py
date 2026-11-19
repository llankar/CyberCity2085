"""Application-owned combat runtime, initialized before the title screen."""
import arcade
from game.combat.persistent_runtime import CombatRuntime
from .music_window import MusicTransitionMixin


class GameWindow(MusicTransitionMixin, arcade.Window):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        # An unstarted runtime fails explicitly: a mission can never launch it late.
        self.combat_runtime=CombatRuntime()
        self._runtime_tick_scheduled=False

    def start_combat_runtime(self):
        started=self.combat_runtime.start((self.width,self.height))
        if not self._runtime_tick_scheduled:
            arcade.schedule(self.combat_runtime.tick,.25)
            self._runtime_tick_scheduled=True
        return started

    def _stop_combat_runtime(self):
        if getattr(self,'_runtime_tick_scheduled',False):
            arcade.unschedule(self.combat_runtime.tick)
            self._runtime_tick_scheduled=False
        if hasattr(self,'combat_runtime'):self.combat_runtime.close()

    def on_close(self):
        self._stop_combat_runtime()
        super().on_close()

    def close(self):
        self._stop_combat_runtime()
        super().close()
