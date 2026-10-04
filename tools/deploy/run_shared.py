"""Authenticated synthetic review service behind a trusted reverse proxy."""
import os
import uvicorn
from medipencil.config import Settings, REPO
from medipencil.main import create_app

settings=Settings.env()
if not settings.shared_review:
    raise SystemExit('MEDIPENCIL_SHARED_REVIEW=1 is required')
if not (REPO/'apps/web/dist/index.html').is_file():
    raise SystemExit('Build frontend before starting the service')
app=create_app(settings)
uvicorn.run(app,host='127.0.0.1',port=int(os.getenv('MEDIPENCIL_PORT','8767')),workers=1,access_log=False)
