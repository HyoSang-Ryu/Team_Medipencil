"""Rename the original demo resident; preserve IDs and historical evidence."""
from alembic import op
revision='008'
down_revision='007'
def upgrade():
    op.execute("UPDATE residents SET display_name='Helmi Nieminen' WHERE subject_id='aino' AND data_origin='TEAM_SYNTHETIC' AND display_name IN ('Aino','Aino (synteettinen)','Aino Nieminen')")
def downgrade():
    raise RuntimeError('Destructive downgrade is not supported')
