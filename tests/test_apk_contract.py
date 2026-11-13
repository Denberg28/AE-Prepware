import importlib.util
from pathlib import Path
import zipfile
import pytest

spec=importlib.util.spec_from_file_location('apk_contract',Path(__file__).resolve().parents[1]/'scripts/apk_contract.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def archive(path,revision='a'*40,code=b'actual-dex',extra=None):
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('classes.dex',code)
        z.writestr('assets/bank.json','{"schema":1}')
        z.writestr(module.VCS_ENTRY,'repositories {\n  system: GIT\n  local_root_path: "$PROJECT_DIR"\n  revision: "'+revision+'"\n}\n')
        if extra:z.writestr(*extra)
    return path

def test_apk_payload_allows_only_the_known_vcs_revision_difference(tmp_path):
    a=archive(tmp_path/'a.apk');b=archive(tmp_path/'b.apk',revision='b'*40)
    assert module.vcs_revision(a)=='a'*40 and module.vcs_revision(b)=='b'*40
    assert module.payload(a)==module.payload(b)
    c=archive(tmp_path/'c.apk',code=b'changed-dex')
    assert module.payload(a)!=module.payload(c)
    d=archive(tmp_path/'d.apk',extra=('META-INF/unexpected.txt','unreviewed'))
    assert module.payload(a)!=module.payload(d)

def test_apk_vcs_metadata_schema_is_not_an_unchecked_exclusion(tmp_path):
    a=archive(tmp_path/'invalid.apk',revision='not-a-source-commit')
    with pytest.raises(ValueError):module.payload(a)
