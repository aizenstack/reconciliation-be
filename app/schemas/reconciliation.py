from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class IssueType(str, Enum):
    STOCK = "stock"
    NAME = "name"
    MISSING_IN_APP = "missing_in_app"
    MISSING_IN_REAL = "missing_in_real"


class DuplicateStrategy(str, Enum):
    REMOVE = "remove"
    MERGE = "merge"


class ProductRow(BaseModel):
    no: Optional[int] = None
    sku: str
    name: str
    stock: int


class ComparisonRow(BaseModel):
    sku: str
    no_app: Optional[int] = None
    no_real: Optional[int] = None
    name_app: Optional[str] = None
    name_real: Optional[str] = None
    stock_app: Optional[int] = None
    stock_real: Optional[int] = None
    diff: Optional[int] = None
    diff_label: Optional[str] = None
    issues: list[IssueType] = Field(default_factory=list)
    highlight_name: bool = False
    matched: bool = False


class CompareSummary(BaseModel):
    total_rows: int
    matched_count: int
    stock_diff_count: int
    name_mismatch_count: int
    missing_in_app_count: int
    missing_in_real_count: int
    net_stock_diff: int


class DuplicateSkuEntry(BaseModel):
    sku: str
    row_numbers: list[int]


class DuplicateCheckResult(BaseModel):
    app: list[DuplicateSkuEntry] = Field(default_factory=list)
    real: list[DuplicateSkuEntry] = Field(default_factory=list)


class CompareResult(BaseModel):
    rows: list[ComparisonRow]
    summary: CompareSummary
    duplicates: DuplicateCheckResult = Field(default_factory=DuplicateCheckResult)
    duplicate_strategy: DuplicateStrategy = DuplicateStrategy.REMOVE
    duplicate_sku_count: int = 0
    duplicate_extra_rows: int = 0


class ExportRequest(BaseModel):
    rows: list[ComparisonRow]
