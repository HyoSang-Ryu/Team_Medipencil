from alembic import op
from medipencil.schema_v1 import SCHEMA, TRIGGERS
revision = '001'
down_revision = None

def upgrade():
    for statement in SCHEMA.split(';'):
        if statement.strip(): op.execute(statement)
    for statement in TRIGGERS: op.execute(statement)

def downgrade():
    raise RuntimeError('Destructive downgrade is not supported')
