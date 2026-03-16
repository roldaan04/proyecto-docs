import hashlib
import io
import re
import uuid
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import pandas as pd
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.purchase_entry import PurchaseEntry
from app.models.purchase_import_batch import PurchaseImportBatch
from app.services.financial_movement_writer import FinancialMovementWriter


class PurchaseImportService:
    ALLOWED_EXTENSIONS = {".xlsx", ".xls"}
    DEFAULT_CURRENCY = "EUR"

    MONTHS_ES = {
        "ene": "01",
        "feb": "02",
        "mar": "03",
        "abr": "04",
        "may": "05",
        "jun": "06",
        "jul": "07",
        "ago": "08",
        "sep": "09",
        "oct": "10",
        "nov": "11",
        "dic": "12",
    }

    def __init__(self, db: Session):
        self.db = db

    async def import_excel(
        self,
        *,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID | None,
        file: UploadFile,
    ) -> PurchaseImportBatch:
        self._validate_file(file)

        content = await file.read()
        checksum = hashlib.sha256(content).hexdigest()

        existing_batch = self._get_batch_by_checksum(
            tenant_id=tenant_id,
            checksum=checksum,
        )
        if existing_batch:
            return existing_batch

        batch = PurchaseImportBatch(
            tenant_id=tenant_id,
            uploaded_by_user_id=user_id,
            filename_original=file.filename or "purchases.xlsx",
            mime_type=file.content_type,
            file_size=len(content),
            checksum=checksum,
            status="processing",
            started_at=datetime.utcnow(),
        )
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)

        try:
            df = self._read_excel(content)
            rows = self._normalize_dataframe(df)

            batch.rows_detected = len(rows)

            imported = 0
            skipped = 0

            for row in rows:
                fingerprint = self._build_row_fingerprint(
                    tenant_id=tenant_id,
                    row=row,
                )

                if self._row_exists(
                    tenant_id=tenant_id,
                    row_fingerprint=fingerprint,
                ):
                    skipped += 1
                    continue

                issue_date = row.get("issue_date")
                month_key = issue_date.strftime("%Y-%m") if issue_date else None

                net_amount = row["net_amount"]
                total_amount = row["total_amount"]
                tax_amount = total_amount - net_amount

                entry = PurchaseEntry(
                    tenant_id=tenant_id,
                    import_batch_id=batch.id,
                    provider_name=row["provider_name"],
                    issue_date=issue_date,
                    order_date=row.get("order_date"),
                    month_key=month_key,
                    net_amount=net_amount,
                    tax_amount=tax_amount,
                    total_amount=total_amount,
                    currency=row.get("currency") or self.DEFAULT_CURRENCY,
                    category=row.get("category"),
                    subcategory=row.get("subcategory"),
                    notes=row.get("notes"),
                    source_type="excel_import",
                    source_reference=file.filename,
                    status="active",
                    row_fingerprint=fingerprint,
                )
                self.db.add(entry)
                self.db.commit()
                self.db.refresh(entry)

                if not FinancialMovementWriter.exists_for_purchase_entry(self.db, entry.id):
                    FinancialMovementWriter.create_from_purchase_entry(self.db, entry)

                imported += 1

            batch.rows_imported = imported
            batch.rows_skipped = skipped
            batch.status = "completed"
            batch.finished_at = datetime.utcnow()

            self.db.add(batch)
            self.db.commit()
            self.db.refresh(batch)
            return batch

        except Exception as exc:
            self.db.rollback()

            batch.status = "failed"
            batch.error_message = str(exc)
            batch.finished_at = datetime.utcnow()

            self.db.add(batch)
            self.db.commit()
            self.db.refresh(batch)
            return batch

    def _validate_file(self, file: UploadFile) -> None:
        filename = (file.filename or "").strip()
        if not filename:
            raise ValueError("El archivo no tiene nombre.")

        ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError("Formato no permitido. Usa .xlsx o .xls.")

    def _get_batch_by_checksum(
        self,
        *,
        tenant_id: uuid.UUID,
        checksum: str,
    ) -> PurchaseImportBatch | None:
        stmt = select(PurchaseImportBatch).where(
            PurchaseImportBatch.tenant_id == tenant_id,
            PurchaseImportBatch.checksum == checksum,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def _read_excel(self, content: bytes) -> pd.DataFrame:
        excel_file = io.BytesIO(content)
        xls = pd.ExcelFile(excel_file)

        preferred_sheet: str | None = None
        for raw_sheet_name in xls.sheet_names:
            sheet_name = str(raw_sheet_name)
            normalized = sheet_name.strip().lower()
            if normalized in ("análisis de compra", "analisis de compra"):
                preferred_sheet = sheet_name
                break

        excel_file.seek(0)
        if preferred_sheet:
            return pd.read_excel(excel_file, sheet_name=preferred_sheet)

        return pd.read_excel(excel_file)

    def _normalize_dataframe(self, df: pd.DataFrame) -> list[dict]:
        if df.empty:
            return []

        rename_map: dict[str, str] = {}
        for col in df.columns:
            rename_map[col] = self._normalize_column_name(str(col))

        df = df.rename(columns=rename_map).copy()

        provider_col = self._pick_first_existing(df, ["proveedor", "provider", "supplier"])
        issue_date_col = self._pick_first_existing(
            df,
            ["fecha", "fecha_pedido", "fecha pedido", "issue_date", "order_date"],
        )
        order_date_col = self._pick_first_existing(
            df,
            ["fecha_pedido", "fecha pedido", "order_date"],
        )
        net_col = self._pick_first_existing(
            df,
            ["importe_neto", "net_amount", "base_imponible", "importe base"],
        )
        gross_col = self._pick_first_existing(
            df,
            ["importe_con_iva", "total_amount", "total", "importe total", "importe con iva"],
        )
        category_col = self._pick_first_existing(df, ["categoria", "category"])
        subcategory_col = self._pick_first_existing(df, ["subcategoria", "subcategory"])
        notes_col = self._pick_first_existing(df, ["notas", "notes", "concepto"])

        if not provider_col:
            raise ValueError("No se ha encontrado la columna de proveedor.")
        if not issue_date_col:
            raise ValueError("No se ha encontrado ninguna columna de fecha.")
        if not net_col:
            raise ValueError("No se ha encontrado la columna de importe neto.")
        if not gross_col:
            raise ValueError("No se ha encontrado la columna de importe con IVA o total.")

        rows: list[dict] = []

        for _, row in df.iterrows():
            provider_name = self._safe_str(row.get(provider_col))
            if not provider_name:
                continue

            issue_date = self._parse_date(row.get(issue_date_col))
            order_date = self._parse_date(row.get(order_date_col)) if order_date_col else None

            net_amount = self._parse_decimal(row.get(net_col))
            total_amount = self._parse_decimal(row.get(gross_col))

            if net_amount is None or total_amount is None:
                continue

            rows.append(
                {
                    "provider_name": provider_name,
                    "issue_date": issue_date,
                    "order_date": order_date,
                    "net_amount": net_amount,
                    "total_amount": total_amount,
                    "currency": self.DEFAULT_CURRENCY,
                    "category": self._safe_str(row.get(category_col)) if category_col else None,
                    "subcategory": self._safe_str(row.get(subcategory_col)) if subcategory_col else None,
                    "notes": self._safe_str(row.get(notes_col)) if notes_col else None,
                }
            )

        return rows

    def _row_exists(self, *, tenant_id: uuid.UUID, row_fingerprint: str) -> bool:
        stmt = select(PurchaseEntry.id).where(
            PurchaseEntry.tenant_id == tenant_id,
            PurchaseEntry.row_fingerprint == row_fingerprint,
        )
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def _build_row_fingerprint(self, *, tenant_id: uuid.UUID, row: dict) -> str:
        payload = "|".join(
            [
                str(tenant_id),
                (row.get("provider_name") or "").strip().lower(),
                row["issue_date"].isoformat() if row.get("issue_date") else "",
                f"{row['net_amount']:.2f}",
                f"{row['total_amount']:.2f}",
            ]
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _normalize_column_name(self, value: str) -> str:
        value = str(value or "").strip().lower()
        value = value.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        value = value.replace("ñ", "n")
        value = re.sub(r"[^a-z0-9]+", "_", value)
        return value.strip("_")

    def _pick_first_existing(self, df: pd.DataFrame, candidates: list[str]) -> str | None:
        normalized_candidates = [self._normalize_column_name(c) for c in candidates]
        for candidate in normalized_candidates:
            if candidate in df.columns:
                return candidate
        return None

    def _safe_str(self, value) -> str | None:
        if value is None:
            return None
        if pd.isna(value):
            return None
        text = str(value).strip()
        return text or None

    def _parse_decimal(self, value) -> Decimal | None:
        if value is None or pd.isna(value):
            return None

        if isinstance(value, Decimal):
            return value.quantize(Decimal("0.01"))

        text = str(value).strip()
        if not text:
            return None

        text = text.replace("€", "").replace("\u200b", "").replace(" ", "")

        if "," in text and "." in text:
            text = text.replace(".", "").replace(",", ".")
        elif "," in text:
            text = text.replace(",", ".")

        try:
            return Decimal(text).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            return None

    def _parse_date(self, value) -> date | None:
        if value is None or pd.isna(value):
            return None

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        text = str(value).strip().lower()
        if not text:
            return None

        for short_month, month_num in self.MONTHS_ES.items():
            text = re.sub(rf"\b{short_month}\b", month_num, text)

        extracted = re.search(r"(\d{2})[\s/\-](\d{2})[\s/\-](\d{4})", text)
        if extracted:
            day, month, year = extracted.groups()
            try:
                return datetime.strptime(f"{day}/{month}/{year}", "%d/%m/%Y").date()
            except ValueError:
                pass

        parsed = pd.to_datetime(text, errors="coerce", dayfirst=True)

        if isinstance(parsed, pd.Timestamp):
            return parsed.date()

        return None