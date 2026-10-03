from alembic import op
revision = '002'
down_revision = '001'


def upgrade():
    op.execute('''CREATE TABLE review_comments (
        comment_id TEXT PRIMARY KEY,
        actor_id TEXT NOT NULL REFERENCES actors(actor_id),
        reviewer_alias TEXT NOT NULL,
        screen TEXT NOT NULL,
        body TEXT NOT NULL,
        created_at TEXT NOT NULL
    )''')


def downgrade():
    raise RuntimeError('Destructive downgrade is not supported')
