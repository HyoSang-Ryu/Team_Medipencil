from alembic import op
revision = '004'
down_revision = '003'


def upgrade():
    # Preserve historical questions, publications and audit trails; remove current access.
    op.execute("UPDATE actors SET active=0 WHERE actor_id='mikko'")
    op.execute("UPDATE access_memberships SET active=0 WHERE actor_id='mikko'")
    op.execute("DELETE FROM demo_sessions WHERE actor_id='mikko'")


def downgrade():
    raise RuntimeError('Automatic restoration of retired account access is not supported')
