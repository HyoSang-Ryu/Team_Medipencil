"""Dedicated temporary TEAM_SYNTHETIC server; never uses caller DATA_ROOT."""
import os,secrets,tempfile
from pathlib import Path
import uvicorn
from medipencil.config import Settings
from medipencil.main import create_app
from medipencil.seed import seed
with tempfile.TemporaryDirectory(prefix='medipencil-e2e-') as root:
    settings=Settings(Path(root).resolve(),origin='http://127.0.0.1:5179',secret=secrets.token_urlsafe(48))
    app=create_app(settings);seed(app.state.store)
    uvicorn.run(app,host='127.0.0.1',port=8765,workers=1,access_log=False)
    app.state.store.engine.dispose()
