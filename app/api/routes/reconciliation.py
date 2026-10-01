from io import BytesIO

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.core.config import ALLOWED_EXTENSIONS, MAX_UPLOAD_BYTES
from app.schemas.reconciliation import (
    CompareResult,
    DuplicateCheckResult,
    DuplicateSkuEntry,
    DuplicateStrategy,
    ExportRequest,
)
from app.services.excel_io import (
    ExcelParseError,
    build_corrected_workbook,
    build_template_workbook,
    duplicate_stats_from_check,
    find_duplicate_skus,
    parse_product_excel,
)
from app.services.reconcile import reconcile

router = APIRouter(prefix="/api", tags=["reconciliation"])


def _validate_upload(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a filename")
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported")


async def _read_upload(file: UploadFile) -> BytesIO:
    _validate_upload(file)
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="File exceeds maximum upload size")
    return BytesIO(content)


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/template/product-stock")
def download_template():
    buffer = build_template_workbook()
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="product-stock-template.xlsx"'},
    )


@router.post("/reconciliation/compare", response_model=CompareResult)
async def compare_files(
    file_app: UploadFile = File(...),
    file_real: UploadFile = File(...),
    duplicate_strategy: DuplicateStrategy = Form(DuplicateStrategy.REMOVE),
):
    app_buffer = await _read_upload(file_app)
    real_buffer = await _read_upload(file_real)

    duplicates = DuplicateCheckResult()

    try:
        app_buffer.seek(0)
        dup_app = find_duplicate_skus(app_buffer, "file_app")
        duplicates.app = [DuplicateSkuEntry(sku=s, row_numbers=r) for s, r in dup_app]

        real_buffer.seek(0)
        dup_real = find_duplicate_skus(real_buffer, "file_real")
        duplicates.real = [DuplicateSkuEntry(sku=s, row_numbers=r) for s, r in dup_real]

        app_buffer.seek(0)
        app_rows = parse_product_excel(app_buffer, "file_app", duplicate_strategy)
        real_buffer.seek(0)
        real_rows = parse_product_excel(real_buffer, "file_real", duplicate_strategy)
    except ExcelParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    sku_count, extra_rows = duplicate_stats_from_check(duplicates)
    result = reconcile(app_rows, real_rows)
    return result.model_copy(
        update={
            "duplicates": duplicates,
            "duplicate_strategy": duplicate_strategy,
            "duplicate_sku_count": sku_count,
            "duplicate_extra_rows": extra_rows,
        }
    )


@router.post("/reconciliation/check-duplicates", response_model=DuplicateCheckResult)
async def check_duplicates(
    file_app: UploadFile | None = File(None),
    file_real: UploadFile | None = File(None),
):
    if file_app is None and file_real is None:
        raise HTTPException(status_code=400, detail="Upload at least one file (file_app or file_real)")

    result = DuplicateCheckResult()

    if file_app is not None:
        buffer = await _read_upload(file_app)
        try:
            dupes = find_duplicate_skus(buffer, "file_app")
        except ExcelParseError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        result.app = [DuplicateSkuEntry(sku=s, row_numbers=r) for s, r in dupes]

    if file_real is not None:
        buffer = await _read_upload(file_real)
        try:
            dupes = find_duplicate_skus(buffer, "file_real")
        except ExcelParseError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        result.real = [DuplicateSkuEntry(sku=s, row_numbers=r) for s, r in dupes]

    return result


@router.post("/reconciliation/export")
async def export_corrected(body: ExportRequest):
    if not body.rows:
        raise HTTPException(status_code=400, detail="No comparison rows to export")
    buffer = build_corrected_workbook(body.rows)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="corrected-product-stock.xlsx"'},
    )
