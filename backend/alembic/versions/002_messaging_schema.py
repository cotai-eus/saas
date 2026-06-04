"""Messaging: channels, messages, conversations, contacts, webhook_events

Revision ID: 002
Revises: 001
Create Date: 2024-06-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    # --- channels ---
    op.create_table(
        "channels",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("type", sa.String(32), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("status", sa.String(16), server_default="inactive", nullable=False),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("daily_limit", sa.Integer(), server_default="1000", nullable=False),
        sa.Column("monthly_limit", sa.Integer(), server_default="30000", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_channels_tenant_id", "channels", ["tenant_id"])
    op.create_index("idx_channels_type", "channels", ["type"])
    op.create_unique_constraint(
        "uq_channels_tenant_type", "channels", ["tenant_id", "type"]
    )
    op.execute("ALTER TABLE channels ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY channels_isolation ON channels "
        "USING (tenant_id = current_setting('app.current_tenant_id')::uuid)"
    )

    # --- contacts ---
    op.create_table(
        "contacts",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("channel_id", sa.UUID(), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("name", sa.String(255), server_default="", nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_contacts_tenant_id", "contacts", ["tenant_id"])
    op.create_index("idx_contacts_channel_id", "contacts", ["channel_id"])
    op.create_index("idx_contacts_external_id", "contacts", ["external_id"])
    op.create_unique_constraint(
        "uq_contacts_channel_external", "contacts", ["channel_id", "external_id"]
    )
    op.execute("ALTER TABLE contacts ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY contacts_isolation ON contacts "
        "USING (tenant_id = current_setting('app.current_tenant_id')::uuid)"
    )

    # --- conversations ---
    op.create_table(
        "conversations",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("channel_id", sa.UUID(), nullable=False),
        sa.Column("channel_type", sa.String(32), nullable=False),
        sa.Column("contact_id", sa.UUID(), nullable=True),
        sa.Column("status", sa.String(16), server_default="active", nullable=False),
        sa.Column("last_message_at", sa.DateTime(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_conversations_tenant_id", "conversations", ["tenant_id"])
    op.create_index("idx_conversations_channel_id", "conversations", ["channel_id"])
    op.create_index("idx_conversations_contact_id", "conversations", ["contact_id"])
    op.execute("ALTER TABLE conversations ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY conversations_isolation ON conversations "
        "USING (tenant_id = current_setting('app.current_tenant_id')::uuid)"
    )

    # --- messages ---
    op.create_table(
        "messages",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("channel_id", sa.UUID(), nullable=False),
        sa.Column("channel_type", sa.String(32), nullable=False),
        sa.Column("contact_id", sa.UUID(), nullable=True),
        sa.Column("conversation_id", sa.UUID(), nullable=True),
        sa.Column("direction", sa.String(10), nullable=False, server_default="outbound"),
        sa.Column("content_type", sa.String(20), nullable=False),
        sa.Column("content_text", sa.Text(), nullable=True),
        sa.Column("content_media_url", sa.String(500), nullable=True),
        sa.Column("content_template_name", sa.String(128), nullable=True),
        sa.Column("content_template_vars", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("provider_message_id", sa.String(255), nullable=True),
        sa.Column("error_code", sa.String(50), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("delivered_at", sa.DateTime(), nullable=True),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_messages_tenant_id", "messages", ["tenant_id"])
    op.create_index("idx_messages_channel_id", "messages", ["channel_id"])
    op.create_index("idx_messages_status", "messages", ["status"])
    op.create_index("idx_messages_provider_message_id", "messages", ["provider_message_id"])
    op.create_index("idx_messages_created_at", "messages", [sa.text("created_at DESC")])
    op.execute("ALTER TABLE messages ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY messages_isolation ON messages "
        "USING (tenant_id = current_setting('app.current_tenant_id')::uuid)"
    )

    # --- webhook_events (sem RLS — idempotência global) ---
    op.create_table(
        "webhook_events",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("event_hash", sa.String(64), nullable=False),
        sa.Column("channel_id", sa.UUID(), nullable=False),
        sa.Column("received_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_webhook_events_hash", "webhook_events", ["event_hash"], unique=True)

    # --- RLS nas tabelas existentes que estavam sem ---
    op.execute("ALTER TABLE sessions ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY sessions_isolation ON sessions "
        "USING (tenant_id = current_setting('app.current_tenant_id')::uuid)"
    )
    op.execute("ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY api_keys_isolation ON api_keys "
        "USING (tenant_id = current_setting('app.current_tenant_id')::uuid)"
    )
    op.execute("ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY subscriptions_isolation ON subscriptions "
        "USING (tenant_id = current_setting('app.current_tenant_id')::uuid)"
    )


def downgrade():
    op.drop_constraint("uq_contacts_channel_external", "contacts", type_="unique")
    op.drop_constraint("uq_channels_tenant_type", "channels", type_="unique")
    op.drop_table("webhook_events")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("contacts")
    op.drop_table("channels")

    op.execute("ALTER TABLE sessions DISABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS sessions_isolation ON sessions")
    op.execute("ALTER TABLE api_keys DISABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS api_keys_isolation ON api_keys")
    op.execute("ALTER TABLE subscriptions DISABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS subscriptions_isolation ON subscriptions")
