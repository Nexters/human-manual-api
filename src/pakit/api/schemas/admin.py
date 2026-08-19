from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class DistributionItem(BaseModel):
    key: str
    count: int
    ratio: float


class DashboardCounts(BaseModel):
    today_results: int
    seven_day_results: int
    thirty_day_results: int
    total_results: int
    today_compatibility: int
    seven_day_compatibility: int


class TrendPoint(BaseModel):
    date: date
    results: int
    views: int
    compatibility: int


class AdminDashboardOutput(BaseModel):
    counts: DashboardCounts
    experience_ratio: float | None
    view_to_compatibility_ratio: float | None
    trend: list[TrendPoint]
    top_mbti: list[DistributionItem]
    top_characters: list[DistributionItem]
    top_tags: list[DistributionItem]
    top_compatibility_pairs: list[DistributionItem]


class AdminResultSummary(BaseModel):
    created_at: datetime
    result_code: str
    nickname: str
    mbti: str | None
    result_name: str | None
    character_id: str | None
    tags: list[str]
    axis_scores: dict[str, int]
    assessment_version: str
    content_version: str
    view_count: int
    compatibility_count: int


class AdminResultListOutput(BaseModel):
    items: list[AdminResultSummary]
    page: int
    page_size: int
    total: int
    pages: int


class UsageSummary(BaseModel):
    view_count: int
    last_viewed_at: datetime | None
    compatibility_count: int


class AdminResultDetailOutput(BaseModel):
    result_code: str
    created_at: datetime
    nickname: str | None
    assessment_version: str
    content_version: str
    usage: UsageSummary
    snapshot: dict[str, Any]


class AxisAnalytics(BaseModel):
    average: float | None
    median: float | None
    bands: dict[str, int]


class ResultAnalyticsOutput(BaseModel):
    total_results: int
    mbti: list[DistributionItem]
    characters: list[DistributionItem]
    result_names: list[DistributionItem]
    tags: list[DistributionItem]
    assessment_versions: list[DistributionItem]
    content_versions: list[DistributionItem]
    axes: dict[str, AxisAnalytics]


class CompatibilityAnalyticsOutput(BaseModel):
    tracking_started_at: datetime | None
    completed_count: int
    experienced_result_count: int
    experience_ratio: float | None
    viewed_result_count: int
    result_view_count: int
    viewed_result_ratio: float | None
    view_to_compatibility_ratio: float | None
    average_per_experienced_result: float | None
    average_score: float | None
    score_bands: dict[str, int]
    mbti_combinations: list[DistributionItem]
    versions: list[DistributionItem]


class AdminError(BaseModel):
    detail: str = Field(description="관리자 접근 오류")
