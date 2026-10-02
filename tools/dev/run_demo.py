"""Single-process loopback demo; retains its synthetic DB after stopping."""
import argparse,secrets
from pathlib import Path
import uvicorn
from medipencil.common import uid
from medipencil.local_providers import LocalModels
from medipencil.config import Settings,REPO
from medipencil.main import create_app
from medipencil.db import one
from medipencil.seed import seed
parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8767);parser.add_argument('--data-root',type=Path)
args=parser.parse_args()
if not (REPO/'apps/web/dist/index.html').exists():parser.error('Build apps/web first')
root=args.data_root or Path.home()/'.local/share/medipencil/runs'/uid()
settings=Settings(root,origin=f'http://127.0.0.1:{args.port}',secret=secrets.token_urlsafe(48),models=LocalModels.env())
app=create_app(settings)
with app.state.store.transaction() as db:empty=one(db,'SELECT * FROM units') is None
if empty:seed(app.state.store)
print(f'LOCAL SYNTHETIC DEMO: {settings.origin}\nDATA_ROOT: {settings.root}\nAI: STT={settings.models.stt_backend}, LLM={settings.models.llm_backend}; sessions reset on restart',flush=True)
uvicorn.run(app,host='127.0.0.1',port=args.port,workers=1,access_log=False)
