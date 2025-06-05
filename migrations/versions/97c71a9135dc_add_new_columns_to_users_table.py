"""add new columns to users table

Revision ID: 97c71a9135dc
Revises: 47d1bed949ac
Create Date: 2025-06-02 20:56:17.471864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.exc import OperationalError


# revision identifiers, used by Alembic.
revision: str = '97c71a9135dc'
down_revision: Union[str, None] = '47d1bed949ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def index_exists(table_name, index_name):
    """Check if an index exists on a table."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
    return index_name in indexes


def upgrade() -> None:
    """Upgrade schema."""
    columns_to_add = [
        ('first_name', sa.String(), True, None),
        ('last_name', sa.String(), True, None),
        ('phone_number', sa.String(), True, None),
        ('birth_date', sa.DateTime(), True, None),
        ('gender', sa.String(), True, None),
        ('country', sa.String(), True, None),
        ('city', sa.String(), True, None),
        ('timezone', sa.String(), True, None),
        ('language', sa.String(), True, 'tr'),
        ('last_login_at', sa.DateTime(), True, None),
        ('last_seen_at', sa.DateTime(), True, None),
        ('login_count', sa.Integer(), True, '0'),
        ('registration_ip', sa.String(), True, None),
        ('last_login_ip', sa.String(), True, None),
        ('account_status', sa.String(), True, 'active'),
        ('suspension_reason', sa.String(), True, None),
        ('bio', sa.Text(), True, None),
        ('website_url', sa.String(), True, None),
        ('privacy_public_profile', sa.Boolean(), True, 'true'),
        ('privacy_show_email', sa.Boolean(), True, 'false'),
        ('privacy_show_phone', sa.Boolean(), True, 'false'),
        ('privacy_show_stats', sa.Boolean(), True, 'true'),
        ('theme_preference', sa.String(), True, 'system'),
        ('notification_email', sa.Boolean(), True, 'true'),
        ('notification_push', sa.Boolean(), True, 'true'),
        ('notification_sms', sa.Boolean(), True, 'false'),
        ('instagram_pk', sa.String(), True, None),
        ('instagram_username', sa.String(), True, None),
        ('instagram_session_data', sa.String(), True, None),
        ('instagram_followers', sa.Integer(), True, '0'),
        ('instagram_following', sa.Integer(), True, '0'),
        ('instagram_posts_count', sa.Integer(), True, '0'),
        ('instagram_profile_pic_url', sa.String(), True, None),
        ('instagram_bio', sa.Text(), True, None),
        ('instagram_is_private', sa.Boolean(), True, 'false'),
        ('instagram_is_verified', sa.Boolean(), True, 'false'),
        ('instagram_external_url', sa.String(), True, None),
        ('instagram_category', sa.String(), True, None),
        ('instagram_contact_phone', sa.String(), True, None),
        ('instagram_contact_email', sa.String(), True, None),
        ('instagram_business_category', sa.String(), True, None),
        ('instagram_connected_at', sa.DateTime(), True, None),
        ('instagram_last_sync', sa.DateTime(), True, None),
        ('instagram_sync_enabled', sa.Boolean(), True, 'true')
    ]

    for name, type, nullable, server_default in columns_to_add:
        if not column_exists('users', name):
            op.add_column('users', sa.Column(name, type, nullable=nullable, server_default=server_default))
        else:
            print(f"Column {name} already exists in users table. Skipping.")

    with op.batch_alter_table('users') as batch_op:
        if not index_exists('users', 'ix_users_instagram_pk'):
            batch_op.create_index(batch_op.f('ix_users_instagram_pk'), ['instagram_pk'], unique=True)
        else:
            print("Index ix_users_instagram_pk already exists. Skipping.")
        
        if not index_exists('users', 'ix_users_instagram_username'):
            batch_op.create_index(batch_op.f('ix_users_instagram_username'), ['instagram_username'], unique=False)
        else:
            print("Index ix_users_instagram_username already exists. Skipping.")


def downgrade() -> None:
    """Downgrade schema."""
    columns_to_drop = [
        'first_name', 'last_name', 'phone_number', 'birth_date', 'gender', 'country', 'city',
        'timezone', 'language', 'last_login_at', 'last_seen_at', 'login_count', 'registration_ip',
        'last_login_ip', 'account_status', 'suspension_reason', 'bio', 'website_url',
        'privacy_public_profile', 'privacy_show_email', 'privacy_show_phone', 'privacy_show_stats',
        'theme_preference', 'notification_email', 'notification_push', 'notification_sms',
        'instagram_pk', 'instagram_username', 'instagram_session_data', 'instagram_followers',
        'instagram_following', 'instagram_posts_count', 'instagram_profile_pic_url', 'instagram_bio',
        'instagram_is_private', 'instagram_is_verified', 'instagram_external_url', 'instagram_category',
        'instagram_contact_phone', 'instagram_contact_email', 'instagram_business_category',
        'instagram_connected_at', 'instagram_last_sync', 'instagram_sync_enabled'
    ]

    with op.batch_alter_table('users') as batch_op:
        if index_exists('users', 'ix_users_instagram_username'):
            batch_op.drop_index(batch_op.f('ix_users_instagram_username'))
        else:
            print("Index ix_users_instagram_username does not exist. Skipping drop.")
            
        if index_exists('users', 'ix_users_instagram_pk'):
            batch_op.drop_index(batch_op.f('ix_users_instagram_pk'))
        else:
            print("Index ix_users_instagram_pk does not exist. Skipping drop.")

    for col_name in columns_to_drop:
        if column_exists('users', col_name):
            op.drop_column('users', col_name)
        else:
            print(f"Column {col_name} does not exist in users table. Skipping drop.")
