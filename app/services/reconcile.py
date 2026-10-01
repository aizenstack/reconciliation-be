from app.schemas.reconciliation import (
    CompareResult,
    CompareSummary,
    ComparisonRow,
    IssueType,
    ProductRow,
)


def _normalize_name(name: str) -> str:
    return name.strip().casefold()


def _format_diff_label(diff: int) -> str:
    if diff > 0:
        return f"+{diff}"
    if diff < 0:
        return str(diff)
    return "0"


def build_export_rows(comparison_rows: list[ComparisonRow]) -> list[ProductRow]:
    """Build corrected product rows from comparison result (real data wins)."""
    app_only: list[ComparisonRow] = []
    matched_and_real_only: list[ComparisonRow] = []

    for row in comparison_rows:
        if IssueType.MISSING_IN_REAL in row.issues:
            app_only.append(row)
        else:
            matched_and_real_only.append(row)

    matched_and_real_only.sort(key=lambda r: (r.no_real or 0, r.sku))
    app_only.sort(key=lambda r: (r.no_app or 0, r.sku))

    export: list[ProductRow] = []
    for row in matched_and_real_only:
        name = row.name_real or row.name_app or ""
        stock = row.stock_real if row.stock_real is not None else (row.stock_app or 0)
        export.append(ProductRow(no=None, sku=row.sku, name=name, stock=stock))

    for row in app_only:
        export.append(
            ProductRow(
                no=None,
                sku=row.sku,
                name=row.name_app or "",
                stock=row.stock_app or 0,
            )
        )

    return export


def reconcile(app_rows: list[ProductRow], real_rows: list[ProductRow]) -> CompareResult:
    app_by_sku = {r.sku: r for r in app_rows}
    real_by_sku = {r.sku: r for r in real_rows}
    all_skus = sorted(set(app_by_sku) | set(real_by_sku))

    comparison_rows: list[ComparisonRow] = []
    stock_diff_count = 0
    name_mismatch_count = 0
    missing_in_app_count = 0
    missing_in_real_count = 0
    matched_count = 0
    net_stock_diff = 0

    for sku in all_skus:
        app = app_by_sku.get(sku)
        real = real_by_sku.get(sku)
        issues: list[IssueType] = []
        highlight_name = False
        matched = app is not None and real is not None

        stock_app = app.stock if app else None
        stock_real = real.stock if real else None
        name_app = app.name if app else None
        name_real = real.name if real else None
        no_app = app.no if app else None
        no_real = real.no if real else None

        diff: int | None = None
        diff_label: str | None = None

        if app is None:
            issues.append(IssueType.MISSING_IN_APP)
            missing_in_app_count += 1
            diff = stock_real
            diff_label = _format_diff_label(diff) if diff is not None else None
            if diff is not None:
                net_stock_diff += diff
        elif real is None:
            issues.append(IssueType.MISSING_IN_REAL)
            missing_in_real_count += 1
            diff = -(stock_app or 0)
            diff_label = _format_diff_label(diff)
            net_stock_diff += diff
        else:
            matched_count += 1
            diff = (stock_real or 0) - (stock_app or 0)
            diff_label = _format_diff_label(diff)
            net_stock_diff += diff
            if diff != 0:
                issues.append(IssueType.STOCK)
                stock_diff_count += 1
            if _normalize_name(name_app or "") != _normalize_name(name_real or ""):
                issues.append(IssueType.NAME)
                highlight_name = True
                name_mismatch_count += 1

        comparison_rows.append(
            ComparisonRow(
                sku=sku,
                no_app=no_app,
                no_real=no_real,
                name_app=name_app,
                name_real=name_real,
                stock_app=stock_app,
                stock_real=stock_real,
                diff=diff,
                diff_label=diff_label,
                issues=issues,
                highlight_name=highlight_name,
                matched=matched,
            )
        )

    summary = CompareSummary(
        total_rows=len(comparison_rows),
        matched_count=matched_count,
        stock_diff_count=stock_diff_count,
        name_mismatch_count=name_mismatch_count,
        missing_in_app_count=missing_in_app_count,
        missing_in_real_count=missing_in_real_count,
        net_stock_diff=net_stock_diff,
    )

    return CompareResult(rows=comparison_rows, summary=summary)
