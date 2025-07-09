"""add_component_tables

Revision ID: c28edb4b8472
Revises: 
Create Date: 2025-07-06 03:08:48.573459

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'c28edb4b8472'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 创建组件表
    op.create_table(
        'components',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(), nullable=False, server_default='1.0.0'),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('path', sa.String(), nullable=False),
        sa.Column('author', sa.String(), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('dependencies', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('extra_info', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_components_category'), 'components', ['category'], unique=False)
    op.create_index(op.f('ix_components_id'), 'components', ['id'], unique=False)
    op.create_index(op.f('ix_components_name'), 'components', ['name'], unique=False)
    
    # 创建组件版本表
    op.create_table(
        'component_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('component_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(), nullable=False),
        sa.Column('commit_id', sa.String(), nullable=False),
        sa.Column('changes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['component_id'], ['components.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_component_versions_id'), 'component_versions', ['id'], unique=False)


def downgrade():
    # 删除表
    op.drop_index(op.f('ix_component_versions_id'), table_name='component_versions')
    op.drop_table('component_versions')
    op.drop_index(op.f('ix_components_name'), table_name='components')
    op.drop_index(op.f('ix_components_id'), table_name='components')
    op.drop_index(op.f('ix_components_category'), table_name='components')
    op.drop_table('components') 