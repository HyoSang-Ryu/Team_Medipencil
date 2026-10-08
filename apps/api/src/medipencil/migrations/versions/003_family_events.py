from alembic import op
revision = '003'
down_revision = '002'


def upgrade():
    op.execute('''CREATE TABLE family_events (
        event_id TEXT PRIMARY KEY, subject_id TEXT NOT NULL REFERENCES residents(subject_id),
        external_id TEXT NOT NULL, source_version INTEGER NOT NULL,
        payload_json TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 1,
        state TEXT NOT NULL DEFAULT 'draft', created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
        UNIQUE(subject_id,external_id)
    )''')
    op.execute('''CREATE TABLE family_event_deliveries (
        event_id TEXT NOT NULL REFERENCES family_events(event_id),
        recipient_id TEXT NOT NULL REFERENCES actors(actor_id),
        event_revision INTEGER NOT NULL, consent_version INTEGER NOT NULL,
        published_by TEXT NOT NULL REFERENCES actors(actor_id), published_at TEXT NOT NULL,
        acknowledged_at TEXT, PRIMARY KEY(event_id,recipient_id)
    )''')


def downgrade():
    raise RuntimeError('Destructive downgrade is not supported')
