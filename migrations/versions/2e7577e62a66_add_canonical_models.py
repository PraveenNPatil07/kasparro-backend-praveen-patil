"""Add canonical models

Revision ID: 2e7577e62a66
Revises: 1a2b3c4d5e6f
Create Date: 2023-12-27 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2e7577e62a66'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Create canonical_assets table
    op.create_table('canonical_assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_canonical_assets_id'), 'canonical_assets', ['id'], unique=False)
    op.create_index(op.f('ix_canonical_assets_name'), 'canonical_assets', ['name'], unique=False)
    op.create_index(op.f('ix_canonical_assets_symbol'), 'canonical_assets', ['symbol'], unique=True)

    # 2. Create asset_mappings table
    op.create_table('asset_mappings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('canonical_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['canonical_id'], ['canonical_assets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_asset_mappings_canonical_id'), 'asset_mappings', ['canonical_id'], unique=False)
    op.create_index(op.f('ix_asset_mappings_external_id'), 'asset_mappings', ['external_id'], unique=False)
    op.create_index(op.f('ix_asset_mappings_id'), 'asset_mappings', ['id'], unique=False)
    op.create_index(op.f('ix_asset_mappings_source'), 'asset_mappings', ['source'], unique=False)

    # 3. Add canonical_id to unified_data
    op.add_column('unified_data', sa.Column('canonical_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_unified_data_canonical_id', 'unified_data', 'canonical_assets', ['canonical_id'], ['id'])
    op.create_index(op.f('ix_unified_data_canonical_id'), 'unified_data', ['canonical_id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_unified_data_canonical_id'), table_name='unified_data')
    op.drop_constraint('fk_unified_data_canonical_id', 'unified_data', type_='foreignkey')
    op.drop_column('unified_data', 'canonical_id')
    op.drop_index(op.f('ix_asset_mappings_source'), table_name='asset_mappings')
    op.drop_index(op.f('ix_asset_mappings_id'), table_name='asset_mappings')
    op.drop_index(op.f('ix_asset_mappings_external_id'), table_name='asset_mappings')
    op.drop_index(op.f('ix_asset_mappings_canonical_id'), table_name='asset_mappings')
    op.drop_table('asset_mappings')
    op.drop_index(op.f('ix_canonical_assets_symbol'), table_name='canonical_assets')
    op.drop_index(op.f('ix_canonical_assets_name'), table_name='canonical_assets')
    op.drop_index(op.f('ix_canonical_assets_id'), table_name='canonical_assets')
    op.drop_table('canonical_assets')
