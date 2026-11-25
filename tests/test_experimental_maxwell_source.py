import importlib.util,sys
from pathlib import Path
import pytest
folder=Path(__file__).parents[1]/'experiments/2d_to_3d';sys.path.insert(0,str(folder))
from acquire_maxwell_hair import qualify_grant

def inputs():
 return {'elvs_maxwell_hair':{'author':'Elvaerwyn','license':'CC-BY','original_author':'','original_source':''}},'# author Elvaerwyn\n# license CC_by\n','# author Elvaerwyn\n# license CC_by\n','CC-BY https://creativecommons.org/licenses/by/4.0/'

def test_source_labels_and_version_basis_remain_distinct():
 result=qualify_grant(*inputs())
 assert result['source_grant_label']=='CC-BY / CC_by'
 assert result['documented_platform_license']=='CC-BY-4.0' and result['attribution_required']

@pytest.mark.parametrize('field,value',[('author','Unknown'),('license','CC-BY-NC'),('original_source','unverified upstream')])
def test_changed_publisher_grant_rejected(field,value):
 args=list(inputs());args[0]['elvs_maxwell_hair'][field]=value
 with pytest.raises(ValueError):qualify_grant(*args)

def test_conflicting_source_header_rejected():
 args=list(inputs());args[1]=args[1].replace('CC_by','CC_by_nc')
 with pytest.raises(ValueError):qualify_grant(*args)

def test_undefined_short_licence_label_not_upgraded_silently():
 args=list(inputs());args[3]='CC-BY'
 with pytest.raises(ValueError):qualify_grant(*args)
