"""Avoid restrictive temporary-directory ACLs in managed Windows workspaces."""
from pathlib import Path
import uuid,sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend import create_app

@pytest.fixture
def app(tmp_path):
    return create_app({'TESTING':True,'SECRET_KEY':'test-secret','DATABASE':str(tmp_path/'db.sqlite'),'UPLOAD_FOLDER':str(tmp_path/'reports'),'DOCTOR_CODE':'invite'})

@pytest.fixture
def tmp_path():
    path=Path(__file__).resolve().parents[1]/'instance'/'test-runs'/uuid.uuid4().hex
    path.mkdir(parents=True)
    return path
