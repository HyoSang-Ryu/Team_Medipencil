import os
from pathlib import Path
from dataclasses import dataclass

REPO = Path(__file__).resolve().parents[4]

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
        if self.origin not in ('http://127.0.0.1:5173', 'http://127.0.0.1:8000', 'http://localhost:5173', 'http://127.0.0.1:5179'):
            raise ValueError('Only local origins supported')
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)

    @classmethod
    def env(cls):
        return cls(Path(os.environ['MEDIPENCIL_DATA_ROOT']), os.getenv('MEDIPENCIL_ORIGIN', 'http://127.0.0.1:5173'), os.environ['MEDIPENCIL_SESSION_SECRET'])
