from alembic import op
revision='006'
down_revision='005'
def upgrade():
    op.execute("UPDATE actors SET display_name='Liisa Nieminen' WHERE actor_id='liisa' AND display_name='Liisa'")
    op.execute("UPDATE actors SET display_name='Heli Koskinen' WHERE actor_id='staff' AND display_name='Koskinen'")
    op.execute("UPDATE residents SET display_name='Aino Nieminen' WHERE subject_id='aino' AND data_origin='TEAM_SYNTHETIC' AND display_name IN ('Aino','Aino (synteettinen)')")
def downgrade():
    raise RuntimeError('Destructive downgrade is not supported')
