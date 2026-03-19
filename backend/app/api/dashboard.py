from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.influencer import Influencer, Snapshot

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get global dashboard statistics."""
    # Total influencers analyzed
    total_result = await db.execute(select(func.count(Influencer.id)))
    total_analyzed = total_result.scalar() or 0

    # Platform breakdown
    ig_result = await db.execute(
        select(func.count(Influencer.id)).where(Influencer.platform == "instagram")
    )
    ig_count = ig_result.scalar() or 0

    tt_result = await db.execute(
        select(func.count(Influencer.id)).where(Influencer.platform == "tiktok")
    )
    tt_count = tt_result.scalar() or 0

    # Average overall score from latest snapshots
    avg_score_result = await db.execute(select(func.avg(Snapshot.overall_score)))
    avg_score = avg_score_result.scalar() or 0.0

    # Average engagement rate
    avg_er_result = await db.execute(select(func.avg(Snapshot.engagement_rate)))
    avg_engagement = avg_er_result.scalar() or 0.0

    # Average fake followers
    avg_fake_result = await db.execute(select(func.avg(Snapshot.fake_followers_pct)))
    avg_fake = avg_fake_result.scalar() or 0.0

    # Top 5 influencers by overall score (latest snapshot)
    # Subquery to get latest snapshot per influencer
    latest_snapshots = (
        select(
            Snapshot.influencer_id,
            func.max(Snapshot.id).label("latest_id"),
        )
        .group_by(Snapshot.influencer_id)
        .subquery()
    )

    top_stmt = (
        select(Influencer, Snapshot)
        .join(latest_snapshots, Influencer.id == latest_snapshots.c.influencer_id)
        .join(Snapshot, Snapshot.id == latest_snapshots.c.latest_id)
        .order_by(Snapshot.overall_score.desc())
        .limit(5)
    )
    top_result = await db.execute(top_stmt)
    top_influencers = [
        {
            "id": inf.id,
            "username": inf.username,
            "platform": inf.platform,
            "full_name": inf.full_name,
            "profile_pic_url": inf.profile_pic_url,
            "followers_count": inf.followers_count,
            "overall_score": snap.overall_score,
            "engagement_rate": snap.engagement_rate,
            "fake_followers_pct": snap.fake_followers_pct,
        }
        for inf, snap in top_result.all()
    ]

    # Zone distribution
    zone_stmt = (
        select(Influencer.zone_operation, func.count(Influencer.id))
        .where(Influencer.zone_operation.isnot(None))
        .group_by(Influencer.zone_operation)
        .order_by(func.count(Influencer.id).desc())
        .limit(10)
    )
    zone_result = await db.execute(zone_stmt)
    zone_distribution = [
        {"zone": zone, "count": count}
        for zone, count in zone_result.all()
    ]

    return {
        "total_analyzed": total_analyzed,
        "platform_breakdown": {
            "instagram": ig_count,
            "tiktok": tt_count,
        },
        "avg_overall_score": round(float(avg_score), 1),
        "avg_engagement_rate": round(float(avg_engagement), 2),
        "avg_fake_followers_pct": round(float(avg_fake), 1),
        "top_influencers": top_influencers,
        "zone_distribution": zone_distribution,
    }


@router.get("/recent")
async def get_recent_analyses(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get most recent analyses."""
    stmt = (
        select(Influencer)
        .options(selectinload(Influencer.snapshots))
        .order_by(Influencer.updated_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    influencers = result.scalars().all()

    recent = []
    for inf in influencers:
        latest_snapshot = None
        if inf.snapshots:
            latest_snapshot = sorted(inf.snapshots, key=lambda s: s.captured_at, reverse=True)[0]

        recent.append({
            "id": inf.id,
            "username": inf.username,
            "platform": inf.platform,
            "full_name": inf.full_name,
            "profile_pic_url": inf.profile_pic_url,
            "followers_count": inf.followers_count,
            "is_verified": inf.is_verified,
            "zone_operation": inf.zone_operation,
            "overall_score": latest_snapshot.overall_score if latest_snapshot else None,
            "engagement_rate": latest_snapshot.engagement_rate if latest_snapshot else None,
            "fake_followers_pct": latest_snapshot.fake_followers_pct if latest_snapshot else None,
            "analyzed_at": inf.updated_at.isoformat() if inf.updated_at else None,
        })

    return {"recent": recent}
