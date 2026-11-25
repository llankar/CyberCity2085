"""No-network checks for bounded source acquisition and provenance guardrails."""
import importlib.util
import io
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).parents[1]/'experiments/2d_to_3d'


@pytest.fixture
def candidate(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT))
    spec = importlib.util.spec_from_file_location('cyborg_acquisition_test', ROOT/'acquire_grab3d_cyborg.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_download_bound_rejects_extra_byte(candidate, monkeypatch):
    monkeypatch.setattr(candidate, 'urlopen', lambda *a, **k: io.BytesIO(b'12345'))
    with pytest.raises(ValueError, match='size limit'):
        candidate.fetch('unused', 4)


def test_exact_bound_is_retained(candidate, monkeypatch):
    monkeypatch.setattr(candidate, 'urlopen', lambda *a, **k: io.BytesIO(b'1234'))
    assert candidate.fetch('unused', 4) == b'1234'


@pytest.mark.parametrize('license_text', [b'All rights reserved', b'CC0 1.0 Universal'])
def test_changed_grant_or_missing_origin_stops_before_model(candidate, monkeypatch, tmp_path, license_text):
    monkeypatch.setattr(candidate, 'ROOT', tmp_path)
    requests = []
    def fake_fetch(url, limit):
        requests.append(url)
        if url.endswith('LICENSE.txt'):
            return license_text
        if url.endswith('manifest.json'):
            return b'{"extras":{"license":"CC0-1.0"}}'
        return b'<html>reviewed page</html>'
    monkeypatch.setattr(candidate, 'fetch', fake_fetch)
    with pytest.raises(ValueError, match='grant/origin'):
        candidate.main()
    assert candidate.MODEL not in requests
    assert not list(tmp_path.iterdir())
