"""add email verification tokens table and is_verified column (if missing)

Revision ID: f3c2b1e4d567
Revises: d89c08ecc206
Create Date: 2025-11-23
"""
from alembic import op
import sqlalchemy as sa

revision = 'f3c2b1e4d567'
down_revision = 'd89c08ecc206'
branch_labels = None
depends_on = None


def upgrade():
    # Add is_verified column if it does not exist (idempotent safeguard)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('users')]
    if 'is_verified' not in columns:
        op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.false()))
        # Drop server default after backfilling
        op.alter_column('users', 'is_verified', server_default=None)

    # Create email_verification_tokens table if it doesn't exist
    tables = inspector.get_table_names()
    if 'email_verification_tokens' not in tables:
        op.create_table(
            'email_verification_tokens',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('token', sa.String(length=255), nullable=False, unique=True),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('consumed', sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
    
    # Create indexes if they don't exist
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('email_verification_tokens')]
    if 'ix_email_verification_tokens_user_id' not in existing_indexes:
        op.create_index('ix_email_verification_tokens_user_id', 'email_verification_tokens', ['user_id'])
    if 'ix_email_verification_tokens_token' not in existing_indexes:
        op.create_index('ix_email_verification_tokens_token', 'email_verification_tokens', ['token'])


def downgrade():
    # Drop table
    op.drop_index('ix_email_verification_tokens_token', table_name='email_verification_tokens')
    op.drop_index('ix_email_verification_tokens_user_id', table_name='email_verification_tokens')
    op.drop_table('email_verification_tokens')

    # Optionally drop is_verified column (only if existed before downgrade decision)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('users')]
    if 'is_verified' in columns:
        op.drop_column('users', 'is_verified')
