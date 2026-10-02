from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from .common import Fault, envelope
from .config import Settings

def create_app(settings=None):
    settings = settings or Settings.env()
    app = FastAPI(title='Päivän kuulumiset — local synthetic demo')
    app.state.settings = settings
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1', 'localhost', 'testserver'])

    @app.exception_handler(Fault)
    async def fault(request, exc):
        result = envelope(None)
        result.pop('data')
        result['error'] = {'code': exc.code, 'message_key': 'errors.' + exc.code.lower(), 'retryable': False}
        return JSONResponse(result, status_code=exc.status, headers={'Cache-Control':'no-store'})

    @app.exception_handler(RequestValidationError)
    async def invalid(request, exc):
        return await fault(request, Fault('VALIDATION_FAILED'))

    @app.middleware('http')
    async def no_store(request: Request, call_next):
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        return response

    @app.get('/api/v1/health')
    def health():
        return envelope({'status':'ok'})
    return app
