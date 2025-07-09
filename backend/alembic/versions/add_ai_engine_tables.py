"""add_ai_engine_tables

Revision ID: 589e72a9b843
Revises: c28edb4b8472
Create Date: 2023-09-08 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '589e72a9b843'
down_revision = 'c28edb4b8472'
branch_labels = None
depends_on = None


def upgrade():
    # 创建AI模型表
    op.create_table(
        'ai_models',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('provider', sa.String(length=100), nullable=False),
        sa.Column('model_id', sa.String(length=100), nullable=False),
        sa.Column('api_key_name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('max_tokens', sa.Integer(), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_ai_models_id'), 'ai_models', ['id'], unique=False)
    
    # 创建个性化模板表
    op.create_table(
        'personalization_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('prompt_template', sa.Text(), nullable=False),
        sa.Column('task_type', sa.String(length=50), nullable=False),
        sa.Column('example_input', sa.Text(), nullable=True),
        sa.Column('example_output', sa.Text(), nullable=True),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('ai_model_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['ai_model_id'], ['ai_models.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_personalization_templates_id'), 'personalization_templates', ['id'], unique=False)
    
    # 创建个性化日志表
    op.create_table(
        'personalization_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('input_code', sa.Text(), nullable=False),
        sa.Column('output_code', sa.Text(), nullable=True),
        sa.Column('prompt_used', sa.Text(), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('processing_time', sa.Float(), nullable=True),
        sa.Column('extra_info', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['personalization_templates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_personalization_logs_id'), 'personalization_logs', ['id'], unique=False)


def downgrade():
    # 删除表 - 注意顺序以避免外键约束错误
    op.drop_index(op.f('ix_personalization_logs_id'), table_name='personalization_logs')
    op.drop_table('personalization_logs')
    op.drop_index(op.f('ix_personalization_templates_id'), table_name='personalization_templates')
    op.drop_table('personalization_templates')
    op.drop_index(op.f('ix_ai_models_id'), table_name='ai_models')
    op.drop_table('ai_models') 