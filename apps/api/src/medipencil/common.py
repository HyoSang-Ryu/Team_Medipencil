from datetime import datetime, timezone
from uuid import uuid4
from pydantic import BaseModel, ConfigDict

class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class Fault(Exception):
    def __init__(self, code, status=422):
        self.code, self.status = code, status

def now():
    return datetime.now(timezone.utc).isoformat()

def uid():
    return str(uuid4())

def envelope(data):
    return {'data': data, 'meta': {'request_id': uid(), 'server_time': now()}}
