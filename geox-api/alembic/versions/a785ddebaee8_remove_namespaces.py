"""Remove namespaces.

Revision ID: a785ddebaee8
Revises: c2667d46ff0f
Create Date: 2022-08-30 13:25:43.225416

Namespaces are a future feature that aren't currently being used.
This will simplify the values.

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a785ddebaee8'
down_revision = 'c2667d46ff0f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_db_credentials_name', table_name='db_credentials')
    op.drop_table('db_credentials')
    op.drop_index('ix_namespaces_id', table_name='namespaces')
    op.drop_table('namespaces')
    op.drop_index('ix_namespace_members_added_by_user_id', table_name='namespace_members')
    op.drop_index('ix_namespace_members_id', table_name='namespace_members')
    op.drop_index('ix_namespace_members_namespace_id', table_name='namespace_members')
    op.drop_index('ix_namespace_members_user_id', table_name='namespace_members')
    op.drop_table('namespace_members')
    op.drop_constraint('shapes_namespace_id_fkey', 'shapes', type_='foreignkey')
    op.drop_column('shapes', 'namespace_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shapes', sa.Column('namespace_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('shapes_namespace_id_fkey', 'shapes', 'namespaces', ['namespace_id'], ['id'])
    op.create_table('namespace_members',
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('has_read', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('has_write', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('is_admin', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('namespace_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('added_by_user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['added_by_user_id'], ['users.id'], name='namespace_members_added_by_user_id_fkey'),
    sa.ForeignKeyConstraint(['namespace_id'], ['namespaces.id'], name='namespace_members_namespace_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='namespace_members_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='namespace_members_pkey')
    )
    op.create_index('ix_namespace_members_user_id', 'namespace_members', ['user_id'], unique=False)
    op.create_index('ix_namespace_members_namespace_id', 'namespace_members', ['namespace_id'], unique=False)
    op.create_index('ix_namespace_members_id', 'namespace_members', ['id'], unique=False)
    op.create_index('ix_namespace_members_added_by_user_id', 'namespace_members', ['added_by_user_id'], unique=False)
    op.create_table('namespaces',
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('created_by_user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('organization_id', postgresql.UUID(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='namespaces_created_by_user_id_fkey'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='namespaces_organization_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='namespaces_pkey')
    )
    op.create_index('ix_namespaces_id', 'namespaces', ['id'], unique=False)
    op.create_table('db_credentials',
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('id', postgresql.UUID(), server_default=sa.text('gen_random_uuid()'), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('organization_id', postgresql.UUID(), autoincrement=False, nullable=True),
    sa.Column('is_default', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('created_by_user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('updated_by_user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('db_driver', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('db_user', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('db_password', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('db_host', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('db_port', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('db_database', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('db_extras', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='db_credentials_created_by_user_id_fkey', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='db_credentials_organization_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['updated_by_user_id'], ['users.id'], name='db_credentials_updated_by_user_id_fkey', ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name='db_credentials_pkey')
    )
    op.create_index('ix_db_credentials_name', 'db_credentials', ['name'], unique=False)
    # ### end Alembic commands ###
