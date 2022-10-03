"""Generate all tables

Revision ID: c545e0392ef6
Revises: 3a689a11fa3b
Create Date: 2022-08-05 16:27:01.099202

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c545e0392ef6'
down_revision = '3a689a11fa3b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('organizations',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name="organizations_pkey")
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sub_id', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('given_name', sa.String(), nullable=True),
    sa.Column('family_name', sa.String(), nullable=True),
    sa.Column('nickname', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('picture', sa.String(), nullable=True),
    sa.Column('locale', sa.String(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('email_verified', sa.Boolean(), nullable=True),
    sa.Column('iss', sa.String(), nullable=True),
    sa.Column('last_login_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name="users_pkey")
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_sub_id'), 'users', ['sub_id'], unique=True)
    op.create_table('db_credentials',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('is_default', sa.Boolean(), nullable=False),
    sa.Column('created_by_user_id', sa.Integer(), nullable=False),
    sa.Column('updated_by_user_id', sa.Integer(), nullable=False),
    sa.Column('db_driver', sa.String(), nullable=False),
    sa.Column('db_user', sa.String(), nullable=False),
    sa.Column('db_password', sa.String(), nullable=False),
    sa.Column('db_host', sa.String(), nullable=False),
    sa.Column('db_port', sa.String(), nullable=False),
    sa.Column('db_database', sa.String(), nullable=False),
    sa.Column('db_extras', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name=op.f("db_credentials_created_by_user_id_fkey")),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f("db_credentials_organization_id_fkey"), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['updated_by_user_id'], ['users.id'], name=op.f("db_credentials_updated_by_user_id_fkey")),
    sa.PrimaryKeyConstraint('id', name=op.f("db_credentials_pkey"))
    )
    op.create_index(op.f('ix_db_credentials_name'), 'db_credentials', ['name'], unique=False)
    op.create_table('namespaces',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('created_by_user_id', sa.Integer(), nullable=True),
    sa.Column('organization_id', postgresql.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name=op.f("namespaces_created_by_user_id_fkey")),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f("namespaces_organization_id_fkey")),
    sa.PrimaryKeyConstraint('id', name=op.f("namespaces_pkey"))
    )
    op.create_index(op.f('ix_namespaces_id'), 'namespaces', ['id'], unique=False)
    op.create_table('organization_members',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('has_read', sa.Boolean(), nullable=False),
    sa.Column('has_write', sa.Boolean(), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('added_by_user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['added_by_user_id'], ['users.id'], ondelete='SET NULL', name=op.f("namespace_members_added_by_user_id_fkey")),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE', name=op.f("namespace_members_namespace_id_fkey")),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name=op.f("namespace_members_user_id_fkey")),
    sa.PrimaryKeyConstraint('id', name=op.f("organization_members_pkey"))
    )
    op.create_index(op.f('ix_organization_members_added_by_user_id'), 'organization_members', ['added_by_user_id'], unique=False)
    op.create_index(op.f('ix_organization_members_id'), 'organization_members', ['id'], unique=False)
    op.create_index(op.f('ix_organization_members_organization_id'), 'organization_members', ['organization_id'], unique=False)
    op.create_index(op.f('ix_organization_members_user_id'), 'organization_members', ['user_id'], unique=True)
    op.create_table('namespace_members',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('has_read', sa.Boolean(), nullable=False),
    sa.Column('has_write', sa.Boolean(), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('namespace_id', sa.Integer(), nullable=False),
    sa.Column('added_by_user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['added_by_user_id'], ['users.id'], name=op.f("namespace_members_added_by_user_id_fke")),
    sa.ForeignKeyConstraint(['namespace_id'], ['namespaces.id']),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f("namespace_members_user_id_fkey")),
    sa.PrimaryKeyConstraint('id', name=op.f("namespace_members_pkey"))
    )
    op.create_index(op.f('ix_namespace_members_added_by_user_id'), 'namespace_members', ['added_by_user_id'], unique=False)
    op.create_index(op.f('ix_namespace_members_id'), 'namespace_members', ['id'], unique=False)
    op.create_index(op.f('ix_namespace_members_namespace_id'), 'namespace_members', ['namespace_id'], unique=False)
    op.create_index(op.f('ix_namespace_members_user_id'), 'namespace_members', ['user_id'], unique=False)
    op.create_table('shapes',
    sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by_user_id', sa.Integer(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('updated_by_user_id', sa.Integer(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at_by_user_id', sa.Integer(), nullable=True),
    sa.Column('geojson', postgresql.JSON(astext_type=sa.Text()), nullable=False),
    sa.Column('namespace_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name = op.f("shapes_created_by_user_id_fkey")),
    sa.ForeignKeyConstraint(['deleted_at_by_user_id'], ['users.id'], name = op.f("shapes_deleted_at_by_user_id_fkey")),
    sa.ForeignKeyConstraint(['namespace_id'], ['namespaces.id'], name = op.f("shapes_namespace_id_fkey")),
    sa.ForeignKeyConstraint(['updated_by_user_id'], ['users.id'], name = op.f("shapes_updated_by_user_id_fkey")),
    sa.PrimaryKeyConstraint('uuid', name=op.f("shapes_uuid_pkey"))
    )
    op.create_index(op.f('ix_shapes_name'), 'shapes', ['name'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_shapes_name'), table_name='shapes')
    op.drop_table('shapes')
    op.drop_index(op.f('ix_namespace_members_user_id'), table_name='namespace_members')
    op.drop_index(op.f('ix_namespace_members_namespace_id'), table_name='namespace_members')
    op.drop_index(op.f('ix_namespace_members_id'), table_name='namespace_members')
    op.drop_index(op.f('ix_namespace_members_added_by_user_id'), table_name='namespace_members')
    op.drop_table('namespace_members')
    op.drop_index(op.f('ix_organization_members_user_id'), table_name='organization_members')
    op.drop_index(op.f('ix_organization_members_organization_id'), table_name='organization_members')
    op.drop_index(op.f('ix_organization_members_id'), table_name='organization_members')
    op.drop_index(op.f('ix_organization_members_added_by_user_id'), table_name='organization_members')
    op.drop_table('organization_members')
    op.drop_index(op.f('ix_namespaces_id'), table_name='namespaces')
    op.drop_table('namespaces')
    op.drop_index(op.f('ix_db_credentials_name'), table_name='db_credentials')
    op.drop_table('db_credentials')
    op.drop_index(op.f('ix_users_sub_id'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('organizations')
