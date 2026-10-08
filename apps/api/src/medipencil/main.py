from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from .common import Fault, envelope
from .config import Settings

def create_app(settings=None):
    settings = settings or Settings.env()
    from contextlib import asynccontextmanager
    from .lifecycle import run_lock
    @asynccontextmanager
    async def lifespan(app):
        with run_lock(settings.root):
            if settings.shared_review:
                from .db import one
                from .seed import seed
                with app.state.store.transaction() as db:
                    empty=one(db,"SELECT * FROM units") is None
                if empty: seed(app.state.store)
            from .audio import recover
            recover(app.state.store,settings.root)
            yield
            app.state.store.engine.dispose()
    app = FastAPI(title='Päivän kuulumiset — local synthetic demo', lifespan=lifespan)
    app.state.settings = settings
    from urllib.parse import urlsplit
    hosts=[urlsplit(settings.origin).hostname] if settings.shared_review else ['127.0.0.1', 'localhost', 'testserver']
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=hosts)

    @app.exception_handler(Fault)
    async def fault(request, exc):
        result = envelope(None)
        result.pop('data')
        result['error'] = {'code': exc.code, 'message_key': 'errors.' + exc.code.lower(), 'retryable': False}
        return JSONResponse(result, status_code=exc.status, headers={'Cache-Control':'no-store'})

    import sqlite3
    @app.exception_handler(sqlite3.Error)
    async def storage_error(request, exc):
        return await fault(request, Fault('STORAGE_UNAVAILABLE',503))

    @app.exception_handler(RequestValidationError)
    async def invalid(request, exc):
        return await fault(request, Fault('VALIDATION_FAILED'))

    @app.middleware('http')
    async def no_store(request: Request, call_next):
        from .security import reviewer
        try: reviewer(request)
        except Fault as exc: return await fault(request,exc)
        if request.headers.get('content-length','').isdigit() and int(request.headers['content-length'])>21*1024*1024:
            return await fault(request, Fault('AUDIO_TOO_LARGE',413))
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        return response

    @app.get('/api/v1/health')
    def health(request: Request):
        from .security import reviewer
        identity=reviewer(request)
        actors=settings.reviewers[identity] if identity is not None else ['liisa','mikko','staff']
        extra={'shared_review':True,'allowed_actors':actors} if settings.shared_review else {}
        if settings.shared_review:
            import os
            commit=os.getenv('MEDIPENCIL_RELEASE_COMMIT')
            if commit:extra['deployment_commit']=commit
        return envelope({'status':'ok','poc_mode':settings.poc_mode,**extra})
    from .db import Store
    from .sessions import router
    app.state.store = Store(settings.root)
    app.state.store.migrate()
    app.include_router(router)
    from .questions import router as questions
    app.include_router(questions)
    from .records import router as records
    app.include_router(records)
    from .publications import router as publications
    app.include_router(publications)
    from .family_events import router as family_events
    app.include_router(family_events)
    from .dashboard import router as dashboard
    app.include_router(dashboard)
    from .consents import router as consents
    app.include_router(consents)
    from .corrections import router as corrections
    app.include_router(corrections)
    from .audio import router as audio, recover
    app.include_router(audio)
    from .sensors import router as sensors
    app.include_router(sensors)
    from .review_comments import router as review_comments
    app.include_router(review_comments)
    from .config import REPO
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    built=REPO/'apps/web/dist'
    if (built/'index.html').exists():
        app.mount('/assets',StaticFiles(directory=built/'assets'),name='assets')
        @app.get('/{path:path}',include_in_schema=False)
        def frontend(path:str):
            if path.startswith('api/'):raise Fault('RESOURCE_NOT_FOUND',404)
            return FileResponse(built/'index.html')
    from .body_limit import BodyLimit
    app.add_middleware(BodyLimit)
    if settings.pages_origin:
        from fastapi.middleware.cors import CORSMiddleware
        app.add_middleware(CORSMiddleware, allow_origins=[settings.pages_origin],
            allow_credentials=False, allow_methods=['GET','POST','PATCH','DELETE'],
            allow_headers=['Content-Type','Authorization','X-CSRF-Token','Idempotency-Key','If-Match'])
    return app

_application = None
async def app(scope, receive, send):
    """Uvicorn ASGI entry; settings are resolved only at server startup."""
    global _application
    if _application is None:
        _application = create_app()
    await _application(scope, receive, send)
