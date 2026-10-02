import os
from pathlib import Path
from dataclasses import dataclass
from urllib.parse import urlsplit

REPO = next((p for p in Path(__file__).resolve().parents if (p/'apps/api/pyproject.toml').is_file()), Path.cwd().resolve())

@dataclass
class Settings:
    root: Path
    origin: str = 'http://127.0.0.1:5173'
    secret: str = ''

    def __post_init__(self):
        original = Path(self.root)
        if not original.is_absolute() or any(p.is_symlink() for p in [original, *original.parents]):
            raise ValueError('DATA_ROOT must be absolute and not symlinked')
        self.root = original.resolve()
        if self.root == REPO or REPO in self.root.parents or self.root in REPO.parents:
            raise ValueError('DATA_ROOT must be a dedicated directory outside repository')
        if len(self.secret) < 32:
            raise ValueError('SESSION_SECRET must contain at least 32 characters')
        parsed=urlsplit(self.origin)
        if parsed.scheme!='http' or parsed.hostname not in ('127.0.0.1','localhost') or not parsed.port or not 1024<=parsed.port<=65535 or parsed.path or parsed.query or parsed.fragment or parsed.username or parsed.password:
            raise ValueError('Only explicit loopback origins supported')
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)

    @classmethod
    def env(cls):
        return cls(Path(os.environ['MEDIPENCIL_DATA_ROOT']), os.getenv('MEDIPENCIL_ORIGIN', 'http://127.0.0.1:5173'), os.environ['MEDIPENCIL_SESSION_SECRET'])
