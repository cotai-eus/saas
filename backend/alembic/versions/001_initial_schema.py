"""Initial schema with multi-tenancy and RLS

Revision ID: 001
Revises: None
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 0. Extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')

    # 1. Tenants
    op.create_table(
        'tenants',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('keycloak_realm_id', sa.String(length=255), nullable=True),
        sa.Column('subscription_plan', sa.String(length=50), server_default='starter', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('keycloak_realm_id'),
        sa.UniqueConstraint('slug'),
        sa.CheckConstraint("slug ~ '^[a-z0-9-]+$'", name='tenant_slug_format')
    )
    op.create_index('idx_tenants_deleted_at', 'tenants', ['deleted_at'], unique=False)
    op.create_index('idx_tenants_keycloak_realm_id', 'tenants', ['keycloak_realm_id'], unique=False)
    op.create_index('idx_tenants_slug', 'tenants', ['slug'], unique=False)

    # RLS for Tenants
    op.execute('ALTER TABLE tenants ENABLE ROW LEVEL SECURITY')
    op.execute("CREATE POLICY tenants_isolation ON tenants USING (id = current_setting('app.current_tenant_id')::uuid)")

    # 2. Users
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('keycloak_user_id', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('roles', sa.ARRAY(sa.String()), server_default='{}', nullable=False),
        sa.Column('groups', sa.ARRAY(sa.String()), server_default='{}', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='TRUE', nullable=False),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'email', name='users_email_per_tenant'),
        sa.UniqueConstraint('tenant_id', 'keycloak_user_id', name='users_keycloak_id_unique')
    )
    op.create_index('idx_users_deleted_at', 'users', ['deleted_at'], unique=False)
    op.create_index('idx_users_email', 'users', ['email'], unique=False)
    op.create_index('idx_users_keycloak_user_id', 'users', ['keycloak_user_id'], unique=False)
    op.create_index('idx_users_tenant_id', 'users', ['tenant_id'], unique=False)

    # RLS for Users
    op.execute('ALTER TABLE users ENABLE ROW LEVEL SECURITY')
    op.execute("CREATE POLICY users_isolation ON users USING (tenant_id = current_setting('app.current_tenant_id')::uuid)")

    # 3. Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.UUID(), nullable=True),
        sa.Column('old_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('new_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_logs_created_at', 'audit_logs', [sa.text('created_at DESC')], unique=False)
    op.create_index('idx_audit_logs_resource', 'audit_logs', ['resource_type', 'resource_id'], unique=False)
    op.create_index('idx_audit_logs_tenant_id', 'audit_logs', ['tenant_id'], unique=False)
    op.create_index('idx_audit_logs_user_id', 'audit_logs', ['user_id'], unique=False)

    # RLS for Audit Logs
    op.execute('ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY')
    op.execute("CREATE POLICY audit_logs_isolation ON audit_logs USING (tenant_id = current_setting('app.current_tenant_id')::uuid)")

    # 4. Subscriptions
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('plan', sa.String(length=50), nullable=False),
        sa.Column('billing_cycle', sa.String(length=10), server_default='monthly', nullable=False),
        sa.Column('price_cents', sa.BigInteger(), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='active', nullable=False),
        sa.Column('seats_limit', sa.Integer(), server_default='5', nullable=False),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('trial_ends_at', sa.DateTime(), nullable=True),
        sa.Column('renewed_at', sa.DateTime(), nullable=True),
        sa.Column('canceled_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id')
    )
    op.create_index('idx_subscriptions_renewed_at', 'subscriptions', ['renewed_at'], unique=False)
    op.create_index('idx_subscriptions_status', 'subscriptions', ['status'], unique=False)
    op.create_index('idx_subscriptions_tenant_id', 'subscriptions', ['tenant_id'], unique=False)

    # 5. Sessions
    op.create_table(
        'sessions',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('keycloak_session_id', sa.String(length=255), nullable=False),
        sa.Column('access_token_jti', sa.String(length=500), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('last_activity_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint('expires_at > started_at', name='session_not_expired'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sessions_expires_at', 'sessions', ['expires_at'], unique=False)
    op.create_index('idx_sessions_keycloak_session_id', 'sessions', ['keycloak_session_id'], unique=False)
    op.create_index('idx_sessions_tenant_id', 'sessions', ['tenant_id'], unique=False)
    op.create_index('idx_sessions_user_id', 'sessions', ['user_id'], unique=False)

    # 6. API Keys
    op.create_table(
        'api_keys',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('key_hash', sa.String(length=255), nullable=False),
        sa.Column('scopes', sa.ARRAY(sa.String()), nullable=False),
        sa.Column('rate_limit', sa.Integer(), server_default='1000', nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='TRUE', nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_hash')
    )
    op.create_index('idx_api_keys_key_hash', 'api_keys', ['key_hash'], unique=False)
    op.create_index('idx_api_keys_tenant_id', 'api_keys', ['tenant_id'], unique=False)

    # 7. Feature Flags
    op.create_table(
        'feature_flags',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('enabled', sa.Boolean(), server_default='FALSE', nullable=False),
        sa.Column('rollout_percentage', sa.Integer(), server_default='0', nullable=True),
        sa.Column('allowed_tenants', sa.ARRAY(sa.String()), server_default='{}', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Helper Functions & Triggers
    op.execute("""
    CREATE OR REPLACE FUNCTION set_current_tenant(tenant_id UUID)
    RETURNS void AS $$
    BEGIN
      PERFORM set_config('app.current_tenant_id', tenant_id::text, true);
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    CREATE OR REPLACE FUNCTION update_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
      NEW.updated_at = CURRENT_TIMESTAMP;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants FOR EACH ROW EXECUTE FUNCTION update_updated_at();")
    op.execute("CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at();")
    op.execute("CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at();")

    # Placeholder for current_user_id() - should be implemented based on app context
    op.execute("""
    CREATE OR REPLACE FUNCTION current_user_id()
    RETURNS UUID AS $$
    BEGIN
      RETURN NULL; -- To be implemented with app context session
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    CREATE OR REPLACE FUNCTION audit_changes()
    RETURNS TRIGGER AS $$
    BEGIN
      INSERT INTO audit_logs (
        tenant_id, user_id, action, resource_type, resource_id,
        old_values, new_values
      ) VALUES (
        COALESCE(NEW.tenant_id, OLD.tenant_id),
        current_user_id(),
        TG_ARGV[0],
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        to_jsonb(OLD),
        to_jsonb(NEW)
      );
      RETURN COALESCE(NEW, OLD);
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("CREATE TRIGGER audit_users AFTER INSERT OR UPDATE OR DELETE ON users FOR EACH ROW EXECUTE FUNCTION audit_changes('users');")

def downgrade():
    op.drop_table('feature_flags')
    op.drop_table('api_keys')
    op.drop_table('sessions')
    op.drop_table('subscriptions')
    op.drop_table('audit_logs')
    op.drop_table('users')
    op.drop_table('tenants')
    op.execute("DROP FUNCTION IF EXISTS audit_changes CASCADE")
    op.execute("DROP FUNCTION IF EXISTS current_user_id CASCADE")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at CASCADE")
    op.execute("DROP FUNCTION IF EXISTS set_current_tenant CASCADE")
