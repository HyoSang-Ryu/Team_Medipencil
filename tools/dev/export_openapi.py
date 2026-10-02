import json,tempfile
from pathlib import Path
from medipencil.config import Settings
from medipencil.main import create_app
with tempfile.TemporaryDirectory(prefix='medipencil-schema-') as root:
    app=create_app(Settings(Path(root).resolve(),secret='schema-export-not-a-session-secret'))
    print(json.dumps(app.openapi(),indent=2))
    app.state.store.engine.dispose()
