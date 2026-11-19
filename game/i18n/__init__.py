from __future__ import annotations

from .en import STRINGS as EN_STRINGS
from .fr import STRINGS as FR_STRINGS

_DICTIONARIES = {"fr": FR_STRINGS, "en": EN_STRINGS}
DEFAULT_LANGUAGE = "en"


def normalize_language(language: str | None) -> str:
    # CyberCity 2085 currently ships with one player-facing language.  Always
    # normalize old saves as well, so a legacy ``fr`` value cannot leak French
    # copy back into the interface.
    return DEFAULT_LANGUAGE


def t(key: str, language: str | None = None, **kwargs) -> str:
    lang = normalize_language(language)
    table = _DICTIONARIES[lang]
    fallback_table = _DICTIONARIES[DEFAULT_LANGUAGE]
    template = table.get(key, fallback_table.get(key, key))
    return template.format(**kwargs) if kwargs else template
