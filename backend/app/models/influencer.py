from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Influencer(Base):
    __tablename__ = "influencers"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, index=True)
    platform = Column(String(50), nullable=False)  # instagram / tiktok
    full_name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    profile_pic_url = Column(String(1024), nullable=True)
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    zone_operation = Column(String(255), nullable=True)  # wilaya
    country = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    snapshots = relationship("Snapshot", back_populates="influencer", cascade="all, delete-orphan")
    screenshots = relationship("Screenshot", back_populates="influencer", cascade="all, delete-orphan")


class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True, index=True)
    influencer_id = Column(Integer, ForeignKey("influencers.id", ondelete="CASCADE"), nullable=False)
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    avg_likes = Column(Float, default=0.0)
    avg_comments = Column(Float, default=0.0)
    avg_shares = Column(Float, default=0.0)
    engagement_rate = Column(Float, default=0.0)
    fake_followers_pct = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    captured_at = Column(DateTime, default=datetime.utcnow)

    influencer = relationship("Influencer", back_populates="snapshots")
    comment_analysis = relationship("CommentAnalysis", back_populates="snapshot", cascade="all, delete-orphan", uselist=False)
    audience_demographic = relationship("AudienceDemographic", back_populates="snapshot", cascade="all, delete-orphan", uselist=False)


class CommentAnalysis(Base):
    __tablename__ = "comment_analyses"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(Integer, ForeignKey("snapshots.id", ondelete="CASCADE"), nullable=False)
    total_comments_analyzed = Column(Integer, default=0)
    bot_comments_pct = Column(Float, default=0.0)
    positive_pct = Column(Float, default=0.0)
    negative_pct = Column(Float, default=0.0)
    neutral_pct = Column(Float, default=0.0)
    top_languages = Column(JSON, nullable=True)
    avg_comment_length = Column(Float, default=0.0)

    snapshot = relationship("Snapshot", back_populates="comment_analysis")


class AudienceDemographic(Base):
    __tablename__ = "audience_demographics"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(Integer, ForeignKey("snapshots.id", ondelete="CASCADE"), nullable=False)
    estimated_male_pct = Column(Float, default=0.0)
    estimated_female_pct = Column(Float, default=0.0)
    age_13_17_pct = Column(Float, default=0.0)
    age_18_24_pct = Column(Float, default=0.0)
    age_25_34_pct = Column(Float, default=0.0)
    age_35_44_pct = Column(Float, default=0.0)
    age_45_plus_pct = Column(Float, default=0.0)
    top_countries = Column(JSON, nullable=True)
    top_cities = Column(JSON, nullable=True)

    snapshot = relationship("Snapshot", back_populates="audience_demographic")


class Screenshot(Base):
    __tablename__ = "screenshots"

    id = Column(Integer, primary_key=True, index=True)
    influencer_id = Column(Integer, ForeignKey("influencers.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(1024), nullable=False)
    ocr_data = Column(JSON, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    influencer = relationship("Influencer", back_populates="screenshots")
