from alembic import op
import sqlalchemy as sa


revision = '20250814_000001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'agent',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('agent_type', sa.String(length=32), nullable=False),
        sa.Column('generation', sa.Integer(),
                  nullable=False, server_default='0'),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False,
                  server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'round',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
    )

    op.create_table(
        'agentrun',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('agent_id', sa.Integer(), sa.ForeignKey(
            'agent.id', ondelete='CASCADE'), nullable=False),
        sa.Column('round_id', sa.Integer(), sa.ForeignKey(
            'round.id', ondelete='CASCADE'), nullable=False),
        sa.Column('signal', sa.String(length=16), nullable=True),
        sa.Column('pnl', sa.Float(), nullable=False, server_default='0'),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade() -> None:
    op.drop_table('agentrun')
    op.drop_table('round')
    op.drop_table('agent')
