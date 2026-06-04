from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from infrastructure.cache.redis_client import get_redis_client
from infrastructure.database.models.subscription import (
    Subscription as SubscriptionModel,
)

LUA_CHECK_AND_INCREMENT = """
local daily_key = KEYS[1]
local monthly_key = KEYS[2]
local daily_limit = tonumber(ARGV[1])
local monthly_limit = tonumber(ARGV[2])

local daily_count = tonumber(redis.call("GET", daily_key) or "0")
local monthly_count = tonumber(redis.call("GET", monthly_key) or "0")

if daily_count >= daily_limit or monthly_count >= monthly_limit then
    return 0
end

redis.call("INCR", daily_key)
if daily_count == 0 then
    redis.call("EXPIRE", daily_key, 86400)
end

redis.call("INCR", monthly_key)
if monthly_count == 0 then
    redis.call("EXPIRE", monthly_key, 2592000)
end

return 1
"""


class QuotaService:
    def __init__(self, db: Session, tenant_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        try:
            self.redis = get_redis_client()
        except Exception:
            self.redis = None

    def check_and_increment(self, channel_id: UUID) -> bool:
        subscription = (
            self.db.query(SubscriptionModel)
            .filter(SubscriptionModel.tenant_id == self.tenant_id)
            .first()
        )
        if not subscription:
            return False

        limits = {
            "starter": {"daily": 100, "monthly": 3000},
            "professional": {"daily": 1000, "monthly": 30000},
            "enterprise": {"daily": 10000, "monthly": 300000},
        }

        plan = subscription.plan
        plan_limits = limits.get(plan, limits["starter"])

        if self.redis:
            now = datetime.now(timezone.utc)
            daily_key = f"quota:{self.tenant_id}:daily:{now.strftime('%Y%m%d')}"
            monthly_key = f"quota:{self.tenant_id}:monthly:{now.strftime('%Y%m')}"

            try:
                result = self.redis.eval(
                    LUA_CHECK_AND_INCREMENT,
                    2,
                    daily_key,
                    monthly_key,
                    plan_limits["daily"],
                    plan_limits["monthly"],
                )
                return bool(result)
            except Exception:
                # Fallback to DB if Redis fails
                pass

        # Fallback implementation (original DB-based)
        from sqlalchemy import func
        from infrastructure.database.models.message import Message as MessageModel
        from datetime import timedelta

        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        monthly_count = (
            self.db.query(func.count(MessageModel.id))
            .filter(
                MessageModel.tenant_id == self.tenant_id,
                MessageModel.created_at >= month_start,
            )
            .scalar()
        )

        daily_count = (
            self.db.query(func.count(MessageModel.id))
            .filter(
                MessageModel.tenant_id == self.tenant_id,
                MessageModel.created_at >= now - timedelta(days=1),
            )
            .scalar()
        )

        if monthly_count >= plan_limits["monthly"]:
            return False
        if daily_count >= plan_limits["daily"]:
            return False

        return True
