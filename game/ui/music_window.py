"""Pause transport during view loading; reuse it after the destination is ready."""
from game.audio import SoundManager


class MusicTransitionMixin:
    def show_view(self, view):
        music = SoundManager.get()
        music.begin_view_transition()
        try:
            return super().show_view(view)
        finally:
            music.end_view_transition()
