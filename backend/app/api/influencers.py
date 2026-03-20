import asyncio
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from typing import Any

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.models.influencer import (
    AudienceDemographic,
    CommentAnalysis,
    Influencer,
    Screenshot,
    Snapshot,
)
from app.services.analyzer import AnalyzerService
from app.services.fake_detector import FakeFollowerDetector
from app.services.instagram_scraper import InstagramScraper
from app.services.ocr_service import OCRService
from app.services.tiktok_scraper import TikTokScraper

router = APIRouter(prefix="/api/influencers", tags=["influencers"])

instagram_scraper = InstagramScraper()
tiktok_scraper = TikTokScraper()

# Auto-login Instagram via saved session or credentials
import os
_session_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ig_session.json")
if os.path.exists(_session_path):
    try:
        from instagrapi import Client as _IgClient
        _cl = _IgClient()
        try:
            from app.core.proxy import PROXY_URL
            if PROXY_URL:
                _cl.set_proxy(PROXY_URL)
        except ImportError:
            pass
        _cl.load_settings(_session_path)
        _cl.login("bapk2026", "bapk2026@")
        instagram_scraper._ig_client = _cl
        instagram_scraper._ig_logged_in = True
        import logging
        logging.getLogger(__name__).info("Instagram: logged in via saved session")
    except Exception as _e:
        import logging
        logging.getLogger(__name__).warning(f"Instagram session login failed: {_e}")
analyzer = AnalyzerService()
fake_detector = FakeFollowerDetector()
ocr_service = OCRService()


@router.post("/analyze")
async def analyze_influencer(
    username: str,
    platform: str = "instagram",
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Analyze an influencer by username and platform."""
    if platform not in ("instagram", "tiktok"):
        raise HTTPException(status_code=400, detail="Platform must be 'instagram' or 'tiktok'")

    username = username.strip().lstrip("@").lower()
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    try:
        # Scrape profile
        if platform == "instagram":
            try:
                profile_data = await asyncio.wait_for(
                    instagram_scraper.scrape_profile(username), timeout=30
                )
                engagement_data = await asyncio.wait_for(
                    instagram_scraper.analyze_engagement(username), timeout=45
                )
            except asyncio.TimeoutError:
                raise HTTPException(status_code=504, detail="Le scraping a pris trop de temps. Réessayez ou utilisez un screenshot.")
            fake_report = fake_detector.detect(
                followers=profile_data.get("followers_count", 0),
                following=profile_data.get("following_count", 0),
                posts_count=profile_data.get("posts_count", 0),
                engagement_rate=engagement_data.get("engagement_rate", 0),
                platform="instagram",
                consistency=engagement_data.get("consistency"),
                comment_like_ratio=engagement_data.get("comment_like_ratio"),
                er_by_views=engagement_data.get("er_by_views"),
                er_by_followers=engagement_data.get("er_by_followers"),
                views_followers_ratio=engagement_data.get("views_followers_ratio"),
                is_verified=profile_data.get("is_verified", False),
            )
            fake_pct = fake_report.fake_pct
        else:
            profile_data = await tiktok_scraper.scrape_profile(username)
            engagement_data = await tiktok_scraper.analyze_engagement(username)
            fake_report = fake_detector.detect(
                followers=profile_data.get("followers_count", 0),
                following=profile_data.get("following_count", 0),
                posts_count=profile_data.get("posts_count", 0),
                engagement_rate=engagement_data.get("engagement_rate", 0),
                platform="tiktok",
                consistency=engagement_data.get("consistency"),
                comment_like_ratio=engagement_data.get("comment_like_ratio"),
                er_by_views=engagement_data.get("er_by_views"),
                er_by_followers=engagement_data.get("er_by_followers"),
                views_followers_ratio=engagement_data.get("views_followers_ratio"),
                is_verified=profile_data.get("is_verified", False),
            )
            fake_pct = fake_report.fake_pct

        # Detect zone
        zone = analyzer.detect_zone_operation(
            bio=profile_data.get("bio", ""),
            location="",
            followers_count=profile_data.get("followers_count", profile_data.get("followers", 0)),
            is_verified=profile_data.get("is_verified", profile_data.get("verified", False)),
        )

        # Calculate scores
        engagement_rate = engagement_data.get("engagement_rate", 0)
        comment_quality = 5.0  # Default without comment data
        overall_score = analyzer.calculate_overall_score(
            engagement_rate=engagement_rate,
            fake_pct=fake_pct,
            comment_quality=comment_quality,
            followers_count=profile_data.get("followers_count", 0),
        )

        # Demographics
        demographics = analyzer.estimate_demographics(profile_data, {})

        # Check if influencer already exists
        stmt = select(Influencer).where(
            Influencer.username == username,
            Influencer.platform == platform,
        )
        result = await db.execute(stmt)
        influencer = result.scalar_one_or_none()

        if influencer:
            # Update existing
            influencer.full_name = profile_data.get("full_name")
            influencer.bio = profile_data.get("bio")
            influencer.profile_pic_url = profile_data.get("profile_pic_url")
            influencer.followers_count = profile_data.get("followers_count", 0)
            influencer.following_count = profile_data.get("following_count", 0)
            influencer.posts_count = profile_data.get("posts_count", 0)
            influencer.is_verified = profile_data.get("is_verified", False)
            influencer.zone_operation = zone
            influencer.updated_at = datetime.utcnow()
        else:
            # Create new
            influencer = Influencer(
                username=username,
                platform=platform,
                full_name=profile_data.get("full_name"),
                bio=profile_data.get("bio"),
                profile_pic_url=profile_data.get("profile_pic_url"),
                followers_count=profile_data.get("followers_count", 0),
                following_count=profile_data.get("following_count", 0),
                posts_count=profile_data.get("posts_count", 0),
                is_verified=profile_data.get("is_verified", False),
                zone_operation=zone,
                country="Algeria" if zone else None,
            )
            db.add(influencer)
            await db.flush()

        # Create snapshot
        snapshot = Snapshot(
            influencer_id=influencer.id,
            followers_count=profile_data.get("followers_count", 0),
            following_count=profile_data.get("following_count", 0),
            posts_count=profile_data.get("posts_count", 0),
            avg_likes=engagement_data.get("avg_likes", 0),
            avg_comments=engagement_data.get("avg_comments", 0),
            avg_shares=engagement_data.get("avg_shares", 0),
            engagement_rate=engagement_rate,
            fake_followers_pct=fake_pct,
            overall_score=overall_score,
        )
        db.add(snapshot)
        await db.flush()

        # Create comment analysis placeholder
        comment_analysis = CommentAnalysis(
            snapshot_id=snapshot.id,
            total_comments_analyzed=0,
            bot_comments_pct=0.0,
            positive_pct=0.0,
            negative_pct=0.0,
            neutral_pct=100.0,
            top_languages=[],
            avg_comment_length=0.0,
        )
        db.add(comment_analysis)

        # Create demographics
        audience = AudienceDemographic(
            snapshot_id=snapshot.id,
            estimated_male_pct=demographics["estimated_male_pct"],
            estimated_female_pct=demographics["estimated_female_pct"],
            age_13_17_pct=demographics["age_13_17_pct"],
            age_18_24_pct=demographics["age_18_24_pct"],
            age_25_34_pct=demographics["age_25_34_pct"],
            age_35_44_pct=demographics["age_35_44_pct"],
            age_45_plus_pct=demographics["age_45_plus_pct"],
            top_countries=demographics["top_countries"],
            top_cities=demographics["top_cities"],
        )
        db.add(audience)

        await db.commit()
        await db.refresh(influencer)

        return {
            "id": influencer.id,
            "username": influencer.username,
            "platform": influencer.platform,
            "full_name": influencer.full_name,
            "bio": influencer.bio,
            "profile_pic_url": influencer.profile_pic_url,
            "followers_count": influencer.followers_count,
            "following_count": influencer.following_count,
            "posts_count": influencer.posts_count,
            "is_verified": influencer.is_verified,
            "zone_operation": influencer.zone_operation,
            "engagement_rate": engagement_rate,
            "fake_followers_pct": fake_pct,
            "overall_score": overall_score,
            "demographics": demographics,
            "snapshot_id": snapshot.id,
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


@router.post("/screenshot")
async def analyze_screenshot(
    file: UploadFile = File(...),
    platform: str = Form("instagram"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Upload a screenshot for OCR-based analysis."""
    # Accept common image types by extension or content_type
    allowed_ext = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif")
    fname = (file.filename or "").lower()
    is_image_ext = any(fname.endswith(e) for e in allowed_ext)
    is_image_ct = file.content_type and file.content_type.startswith("image/")
    if not is_image_ext and not is_image_ct:
        raise HTTPException(status_code=400, detail="File must be an image (jpg, png, webp)")

    # Save the uploaded file
    ext = os.path.splitext(file.filename or "upload.png")[1] or ".png"
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    try:
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        # Run OCR
        ocr_data = ocr_service.extract_from_screenshot(file_path)
        detected_platform = ocr_data.get("platform") or platform

        # If username was detected, try to create/update influencer
        username = ocr_data.get("username")
        influencer_id = None

        if username:
            stmt = select(Influencer).where(
                Influencer.username == username.lower(),
                Influencer.platform == detected_platform,
            )
            result = await db.execute(stmt)
            influencer = result.scalar_one_or_none()

            if not influencer:
                influencer = Influencer(
                    username=username.lower(),
                    platform=detected_platform,
                    followers_count=ocr_data.get("followers") or 0,
                    following_count=ocr_data.get("following") or 0,
                    posts_count=ocr_data.get("posts") or 0,
                )
                db.add(influencer)
                await db.flush()

            influencer_id = influencer.id

            # Save screenshot record
            screenshot = Screenshot(
                influencer_id=influencer.id,
                file_path=f"/static/uploads/{filename}",
                ocr_data=ocr_data,
            )
            db.add(screenshot)
            await db.commit()

        return {
            "filename": filename,
            "file_path": f"/static/uploads/{filename}",
            "ocr_data": ocr_data,
            "influencer_id": influencer_id,
            "platform": detected_platform,
        }

    except Exception as e:
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Screenshot analysis failed: {e}")


@router.get("/")
async def list_influencers(
    skip: int = 0,
    limit: int = 50,
    platform: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """List all analyzed influencers."""
    stmt = select(Influencer).order_by(Influencer.updated_at.desc())

    if platform:
        stmt = stmt.where(Influencer.platform == platform)

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    influencers = result.scalars().all()

    # Get total count
    count_stmt = select(Influencer)
    if platform:
        count_stmt = count_stmt.where(Influencer.platform == platform)
    count_result = await db.execute(count_stmt)
    total = len(count_result.scalars().all())

    return {
        "total": total,
        "influencers": [
            {
                "id": inf.id,
                "username": inf.username,
                "platform": inf.platform,
                "full_name": inf.full_name,
                "profile_pic_url": inf.profile_pic_url,
                "followers_count": inf.followers_count,
                "is_verified": inf.is_verified,
                "zone_operation": inf.zone_operation,
                "updated_at": inf.updated_at.isoformat() if inf.updated_at else None,
            }
            for inf in influencers
        ],
    }


@router.get("/{influencer_id}")
async def get_influencer(
    influencer_id: int,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get detailed analysis for an influencer."""
    stmt = (
        select(Influencer)
        .options(
            selectinload(Influencer.snapshots).selectinload(Snapshot.comment_analysis),
            selectinload(Influencer.snapshots).selectinload(Snapshot.audience_demographic),
            selectinload(Influencer.screenshots),
        )
        .where(Influencer.id == influencer_id)
    )
    result = await db.execute(stmt)
    influencer = result.scalar_one_or_none()

    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer not found")

    latest_snapshot = None
    if influencer.snapshots:
        latest_snapshot = sorted(influencer.snapshots, key=lambda s: s.captured_at, reverse=True)[0]

    snapshot_data = None
    if latest_snapshot:
        comment_data = None
        if latest_snapshot.comment_analysis:
            ca = latest_snapshot.comment_analysis
            comment_data = {
                "total_comments_analyzed": ca.total_comments_analyzed,
                "bot_comments_pct": ca.bot_comments_pct,
                "positive_pct": ca.positive_pct,
                "negative_pct": ca.negative_pct,
                "neutral_pct": ca.neutral_pct,
                "top_languages": ca.top_languages,
                "avg_comment_length": ca.avg_comment_length,
            }

        demographic_data = None
        if latest_snapshot.audience_demographic:
            ad = latest_snapshot.audience_demographic
            demographic_data = {
                "estimated_male_pct": ad.estimated_male_pct,
                "estimated_female_pct": ad.estimated_female_pct,
                "age_13_17_pct": ad.age_13_17_pct,
                "age_18_24_pct": ad.age_18_24_pct,
                "age_25_34_pct": ad.age_25_34_pct,
                "age_35_44_pct": ad.age_35_44_pct,
                "age_45_plus_pct": ad.age_45_plus_pct,
                "top_countries": ad.top_countries,
                "top_cities": ad.top_cities,
            }

        snapshot_data = {
            "id": latest_snapshot.id,
            "followers_count": latest_snapshot.followers_count,
            "following_count": latest_snapshot.following_count,
            "posts_count": latest_snapshot.posts_count,
            "avg_likes": latest_snapshot.avg_likes,
            "avg_comments": latest_snapshot.avg_comments,
            "avg_shares": latest_snapshot.avg_shares,
            "engagement_rate": latest_snapshot.engagement_rate,
            "fake_followers_pct": latest_snapshot.fake_followers_pct,
            "overall_score": latest_snapshot.overall_score,
            "captured_at": latest_snapshot.captured_at.isoformat() if latest_snapshot.captured_at else None,
            "comment_analysis": comment_data,
            "audience_demographic": demographic_data,
        }

    return {
        "id": influencer.id,
        "username": influencer.username,
        "platform": influencer.platform,
        "full_name": influencer.full_name,
        "bio": influencer.bio,
        "profile_pic_url": influencer.profile_pic_url,
        "followers_count": influencer.followers_count,
        "following_count": influencer.following_count,
        "posts_count": influencer.posts_count,
        "is_verified": influencer.is_verified,
        "zone_operation": influencer.zone_operation,
        "country": influencer.country,
        "created_at": influencer.created_at.isoformat() if influencer.created_at else None,
        "updated_at": influencer.updated_at.isoformat() if influencer.updated_at else None,
        "latest_snapshot": snapshot_data,
        "total_snapshots": len(influencer.snapshots),
        "screenshots": [
            {
                "id": s.id,
                "file_path": s.file_path,
                "ocr_data": s.ocr_data,
                "uploaded_at": s.uploaded_at.isoformat() if s.uploaded_at else None,
            }
            for s in influencer.screenshots
        ],
    }


@router.get("/{influencer_id}/history")
async def get_snapshot_history(
    influencer_id: int,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get snapshot history for an influencer."""
    stmt = select(Influencer).where(Influencer.id == influencer_id)
    result = await db.execute(stmt)
    influencer = result.scalar_one_or_none()

    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer not found")

    stmt = (
        select(Snapshot)
        .where(Snapshot.influencer_id == influencer_id)
        .order_by(Snapshot.captured_at.desc())
    )
    result = await db.execute(stmt)
    snapshots = result.scalars().all()

    return {
        "influencer_id": influencer_id,
        "username": influencer.username,
        "snapshots": [
            {
                "id": s.id,
                "followers_count": s.followers_count,
                "following_count": s.following_count,
                "posts_count": s.posts_count,
                "avg_likes": s.avg_likes,
                "avg_comments": s.avg_comments,
                "engagement_rate": s.engagement_rate,
                "fake_followers_pct": s.fake_followers_pct,
                "overall_score": s.overall_score,
                "captured_at": s.captured_at.isoformat() if s.captured_at else None,
            }
            for s in snapshots
        ],
    }


@router.delete("/{influencer_id}")
async def delete_influencer(
    influencer_id: int,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    """Delete an influencer and all related data."""
    stmt = select(Influencer).where(Influencer.id == influencer_id)
    result = await db.execute(stmt)
    influencer = result.scalar_one_or_none()

    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer not found")

    await db.delete(influencer)
    await db.commit()

    return {"message": f"Influencer '{influencer.username}' deleted successfully"}


@router.post("/compare")
async def compare_influencers(
    ids: List[int],
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Compare multiple influencers side by side."""
    if len(ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 influencer IDs required")
    if len(ids) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 influencers for comparison")

    comparisons = []

    for inf_id in ids:
        stmt = (
            select(Influencer)
            .options(selectinload(Influencer.snapshots))
            .where(Influencer.id == inf_id)
        )
        result = await db.execute(stmt)
        influencer = result.scalar_one_or_none()

        if not influencer:
            raise HTTPException(status_code=404, detail=f"Influencer with ID {inf_id} not found")

        latest_snapshot = None
        if influencer.snapshots:
            latest_snapshot = sorted(influencer.snapshots, key=lambda s: s.captured_at, reverse=True)[0]

        comparisons.append({
            "id": influencer.id,
            "username": influencer.username,
            "platform": influencer.platform,
            "full_name": influencer.full_name,
            "profile_pic_url": influencer.profile_pic_url,
            "followers_count": influencer.followers_count,
            "following_count": influencer.following_count,
            "posts_count": influencer.posts_count,
            "is_verified": influencer.is_verified,
            "zone_operation": influencer.zone_operation,
            "engagement_rate": latest_snapshot.engagement_rate if latest_snapshot else 0,
            "fake_followers_pct": latest_snapshot.fake_followers_pct if latest_snapshot else 0,
            "overall_score": latest_snapshot.overall_score if latest_snapshot else 0,
            "avg_likes": latest_snapshot.avg_likes if latest_snapshot else 0,
            "avg_comments": latest_snapshot.avg_comments if latest_snapshot else 0,
        })

    return {"comparisons": comparisons}
