import importlib.util
from pathlib import Path
import pytest
p=Path(__file__).parents[1]/'experiments/2d_to_3d/acquire_unvanquished_human.py'
@pytest.fixture
def module(monkeypatch):
    monkeypatch.syspath_prepend(str(p.parent))
    spec=importlib.util.spec_from_file_location('acquire_unv',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def credits(license='CC BY-SA 3.0',author='Angelo'):
    return '<table>'+''.join(f'<tr><td>{name}</td><td>{author}</td><td>In game</td><td>{license}</td></tr>' for name in ['Male','Light Armour','Medium Armour'])+'</table>'

def test_specific_player_armor_grant_parsed_not_global_default(module):
    assert set(module.reviewed_credits(credits()))=={'Male','Light Armour','Medium Armour'}

@pytest.mark.parametrize('license',['CC BY-NC 3.0','CC BY-ND 3.0','Unknown'])
def test_changed_or_restrictive_grant_rejected(module,license):
    with pytest.raises(ValueError):module.reviewed_credits(credits(license=license))

def test_missing_author_or_missing_exact_component_rejected(module):
    with pytest.raises(ValueError):module.reviewed_credits(credits(author='Unknown'))
    with pytest.raises(ValueError):module.reviewed_credits(credits().replace('Medium Armour','Other'))


def test_upcoming_different_male_does_not_override_shipped_source(module):
    html=credits()+'<table><tr><td>Male</td><td>RXMT</td><td>Modelled</td><td>CC BY-SA 3.0</td></tr></table>'
    assert 'Angelo' in module.reviewed_credits(html)['Male']
