from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from infrastructure.database.models.message import Message as MessageModel
from infrastructure.database.models.subscription import (
    Subscription as SubscriptionModel,
)


class QuotaService:
    def __init__(self, db: Session, tenant_id: UUID):
        self.db = db
        self.tenant_id = tenant_id

    def check_and_increment(self, channel_id: UUID) -> bool:
        subscription = (
            self.db.query(SubscriptionModel)
            .filter(SubscriptionModel.tenant_id == self.tenant_id)
            .first()
        )
        if not subscription:
            return False

        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        monthly_count = (
            self.db.query(MessageModel)
            .filter(
                MessageModel.tenant_id == self.tenant_id,
                MessageModel.created_at >= month_start,
            )
            .count()
        )

        daily_count = (
            self.db.query(MessageModel)
            .filter(
                MessageModel.tenant_id == self.tenant_id,
                MessageModel.created_at >= now - timedelta(days=1),
            )
            .count()
        )

        limits = {
            "starter": {"daily": 100, "monthly": 3000},
            "professional": {"daily": 1000, "monthly": 30000},
            "enterprise": {"daily": 10000, "monthly": 300000},
        }

        plan = subscription.plan
        plan_limits = limits.get(plan, limits["starter"])

        if monthly_count >= plan_limits["monthly"]:
            return False
        if daily_count >= plan_limits["daily"]:
            return False

        return True
