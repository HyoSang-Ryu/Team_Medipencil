import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from .local_providers import LocalModels
from urllib.parse import urlsplit

REPO = next((p for p in Path(__file__).resolve().parents if (p/'apps/api/pyproject.toml').is_file()), Path.cwd().resolve())

@dataclass
class Settings:
    root: Path
    origin: str = 'http://127.0.0.1:5173'
    secret: str = ''
    models: LocalModels = field(default_factory=LocalModels)
    poc_mode: bool = False
    shared_review: bool = False
    public_review: bool = False
    pages_origin: str = ""
    cookie_path: str = "/"
    proxy_secret: str = field(default="", repr=False)
    reviewers: dict[str, list[str]] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        if self.pages_origin:
            parsed=urlsplit(self.pages_origin)
            if not (self.public_review and self.shared_review and self.poc_mode and parsed.scheme=="https" and parsed.hostname and not parsed.username and not parsed.password and not parsed.path and not parsed.query and not parsed.fragment):
                raise ValueError("Pages origin requires an exact HTTPS origin and public synthetic PoC")
        if self.public_review and not (self.shared_review and self.poc_mode):
            raise ValueError("Public review requires shared PoC mode")
        if self.poc_mode:self.models=LocalModels()
        if not self.cookie_path.startswith("/") or not self.cookie_path.endswith("/") or any(c not in "/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in self.cookie_path):
            raise ValueError("Invalid cookie path")
        original = Path(self.root)
        if not original.is_absolute() or any(p.is_symlink() for p in [original, *original.parents]):
            raise ValueError('DATA_ROOT must be absolute and not symlinked')
        self.root = original.resolve()
        if self.root == REPO or REPO in self.root.parents or self.root in REPO.parents:
            raise ValueError('DATA_ROOT must be a dedicated directory outside repository')
        if len(self.secret) < 32:
            raise ValueError('SESSION_SECRET must contain at least 32 characters')
        parsed=urlsplit(self.origin)
        if self.shared_review:
            if not self.poc_mode or parsed.scheme != 'https' or not parsed.hostname or parsed.hostname in ('localhost','127.0.0.1') or parsed.path or parsed.query or parsed.fragment or parsed.username or parsed.password:
                raise ValueError('Shared review requires PoC mode and an HTTPS origin')
            if not self.public_review and (len(self.proxy_secret) < 32 or self.proxy_secret == self.secret):
                raise ValueError('Shared review requires a separate proxy secret')
            if not self.public_review and (not self.reviewers or any(not isinstance(k,str) or not k or not isinstance(v,list) or not v or any(a not in ('staff','liisa','mikko') for a in v) for k,v in self.reviewers.items())):
                raise ValueError('Explicit reviewer actor permissions are required')
        elif parsed.scheme!='http' or parsed.hostname not in ('127.0.0.1','localhost') or not parsed.port or not 1024<=parsed.port<=65535 or parsed.path or parsed.query or parsed.fragment or parsed.username or parsed.password:
            raise ValueError('Only explicit loopback origins supported')
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)

    @classmethod
    def env(cls):
        shared = os.getenv('MEDIPENCIL_SHARED_REVIEW') == '1'
        public = os.getenv('MEDIPENCIL_PUBLIC_REVIEW') == '1'
        reviewers = {}
        if shared and not public:
            reviewers = json.loads(Path(os.environ['MEDIPENCIL_REVIEWERS_FILE']).read_text())
            if not isinstance(reviewers, dict): raise ValueError('Reviewer configuration must be an object')
        return cls(root=Path(os.environ['MEDIPENCIL_DATA_ROOT']), origin=os.getenv('MEDIPENCIL_ORIGIN', 'http://127.0.0.1:5173'), secret=os.environ['MEDIPENCIL_SESSION_SECRET'], models=LocalModels.env(), poc_mode=os.getenv('MEDIPENCIL_POC') == '1', shared_review=shared, public_review=public, pages_origin=os.getenv("MEDIPENCIL_PAGES_ORIGIN", ""), cookie_path=os.getenv("MEDIPENCIL_COOKIE_PATH", "/"), proxy_secret=os.getenv('MEDIPENCIL_PROXY_SECRET',''), reviewers=reviewers)
