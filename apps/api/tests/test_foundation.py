import pytest
from fastapi.testclient import TestClient
from medipencil.config import Settings, REPO
from medipencil.main import create_app

def test_health(tmp_path):
    client = TestClient(create_app(Settings(tmp_path, secret='s'*32)))
    assert client.get('/api/v1/health').json()['data'] == {'status':'ok','poc_mode':False,'allowed_actors':[]}
    assert client.get('/api/v1/health').headers['cache-control'] == 'no-store'

def test_root_boundary():
    with pytest.raises(ValueError): Settings(REPO / 'data', secret='s'*32)

def test_poc_mode_disables_configured_models(tmp_path):
    from medipencil.local_providers import LocalModels
    settings=Settings(tmp_path,secret='p'*32,models=LocalModels(llm_backend='ollama'),poc_mode=True)
    assert settings.models.llm_backend=='disabled' and settings.models.stt_backend=='disabled'
    client=TestClient(create_app(settings))
    assert client.get('/api/v1/health').json()['data']=={'status':'ok','poc_mode':True,'allowed_actors':[]}
