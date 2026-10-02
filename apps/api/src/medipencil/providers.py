"""Provider boundary. No verified STT/LLM is configured in this release."""
from typing import Protocol
from urllib.parse import urlparse
from .common import Fault

class SpeechToTextPort(Protocol):
    def transcribe(self, audio_ref:str, lang:str, lineage:list[str]): ...
class CareExtractionPort(Protocol):
    def extract(self, snapshot:dict): ...
class FamilyWordingPort(Protocol):
    def render(self, permitted_snapshot:dict): ...
class AudioLifecyclePort(Protocol):
    def cleanup(self, artifact_refs:list[str]): ...

class UnconfiguredProvider:
    def transcribe(self,*args,**kwargs):raise Fault('PROVIDER_NOT_CONFIGURED',503)
    def extract(self,*args,**kwargs):raise Fault('PROVIDER_NOT_CONFIGURED',503)
    def render(self,*args,**kwargs):raise Fault('PROVIDER_NOT_CONFIGURED',503)

def egress(lineage, endpoint, allowlist=()):
    # Fail closed: even mixed/unknown lineage is denied before any network operation.
    if not lineage or any(value!='TEAM_SYNTHETIC' for value in lineage):raise Fault('EGRESS_DENIED',403)
    p=urlparse(endpoint)
    if endpoint not in allowlist or p.scheme not in ('http','https') or p.hostname not in ('127.0.0.1','localhost') or p.username or p.password:raise Fault('EGRESS_DENIED',403)
    return True

class VeilImportPort(Protocol):
    def plan(self, approved_schema_metadata:dict): ...

class BlockedVeilImport:
    def plan(self,approved_schema_metadata):
        # No file path/read capability until Q-02 and an actual schema are confirmed locally.
        raise Fault('VEIL_NOT_AUTHORIZED',403)
