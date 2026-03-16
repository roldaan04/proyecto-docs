import logging
import pandas as pd
import hashlib
import json
from pathlib import Path
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.financial_movement import FinancialMovement

logger = logging.getLogger(__name__)

class ExcelProcessingService:
    # Semantic mapping for headers
    HEADER_MAPPING = {
        "movement_date": ["Fecha", "F. emisión", "Fecha factura", "Date", "Fecha mov.", "Día"],
        "third_party_name": ["Tercero", "Cliente", "Proveedor", "Empresa", "Nombre", "Acreedor", "Razón Social"],
        "net_amount": ["Base Imponible", "Base", "Neto", "Importe base", "Subtotal"],
        "tax_amount": ["IVA", "Cuota IVA", "Impuesto", "VAT"],
        "total_amount": ["Total", "Importe", "Total factura", "Importe final", "Total con IVA", "Salida", "Entrada"],
        "withholding_amount": ["IRPF General", "IRPF Alquiler", "Retención", "IRPF", "Ret."],
        "source_reference": ["Nº Factura", "Factura", "Referencia", "Ref.", "Doc."],
        "concept": ["Concepto", "Descripción", "Detalle", "Observaciones"]
    }

    @staticmethod
    def _normalize_headers(row_list: list) -> dict:
        """Determines which column index corresponds to which model field."""
        mapping = {}
        for idx, cell in enumerate(row_list):
            if pd.isna(cell) or not isinstance(cell, str):
                continue
            
            clean_cell = cell.strip().lower()
            for field, aliases in ExcelProcessingService.HEADER_MAPPING.items():
                for alias in aliases:
                    if alias.lower() in clean_cell or clean_cell in alias.lower():
                        mapping[field] = idx
                        break
        return mapping

    @staticmethod
    def _find_table_start(df: pd.DataFrame) -> tuple[int, dict]:
        """Finds the row index that contains the most recognized headers."""
        best_row = 0
        best_mapping = {}
        max_matches = 0

        for i in range(min(20, len(df))):
            current_row = df.iloc[i].tolist()
            mapping = ExcelProcessingService._normalize_headers(current_row)
            if len(mapping) > max_matches:
                max_matches = len(mapping)
                best_row = i
                best_mapping = mapping
        
        return best_row, best_mapping

    @staticmethod
    def _classify_sheet(sheet_name: str, mapping: dict, df_sample: pd.DataFrame) -> str:
        """Heuristic to decide if a sheet is 'income' or 'expense'."""
        s_name = sheet_name.lower()
        if "venta" in s_name or "ingreso" in s_name or "facturación" in s_name:
            return "income"
        if "gasto" in s_name or "compra" in s_name or "inversión" in s_name or "proveedor" in s_name:
            return "expense"
        
        # Check column names
        if "third_party_name" in mapping:
            # If we see "Cliente", it's likely income. If "Proveedor", likely expense.
            pass # More complex checks could go here
            
        return "expense" # Default

    @staticmethod
    def _generate_fingerprint(tenant_id: UUID, data: dict) -> str:
        hash_dict = {
            "tenant_id": str(tenant_id),
            "date": str(data.get("movement_date")),
            "third_party": str(data.get("third_party_name")).strip().lower(),
            "total": str(data.get("total_amount")),
            "reference": str(data.get("source_reference")).strip().lower() if data.get("source_reference") else "",
            "kind": data.get("kind"),
            "concept": str(data.get("concept")).strip().lower() if data.get("concept") else ""
        }
        encoded = json.dumps(hash_dict, sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _check_exists(db: Session, fingerprint: str) -> bool:
        return db.query(FinancialMovement).filter(FinancialMovement.fingerprint == fingerprint).first() is not None

    @staticmethod
    def preview_document(file_path: str) -> dict:
        """
        Analyzes an Excel file and returns a structural preview.
        """
        path = Path(file_path)
        if not path.exists():
            return {"error": "File not found"}

        try:
            with pd.ExcelFile(path) as xls:
                preview = {"sheets": []}

                for sheet_name in xls.sheet_names:
                    # Use header=None to ensure _find_table_start sees the actual header row
                    df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
                    if df.empty:
                        continue

                    header_row, mapping = ExcelProcessingService._find_table_start(df)
                    if not mapping or len(mapping) < 2:
                        logger.info(f"[Preview] Skipping sheet '{sheet_name}': Insufficient headers found.")
                        continue

                    # Sample some data for classification
                    sample_for_class = df.iloc[header_row+1:header_row+6] if len(df) > header_row + 1 else pd.DataFrame()
                    kind = ExcelProcessingService._classify_sheet(sheet_name, mapping, sample_for_class)
                    
                    # Sample some rows
                    sample_rows = []
                    for i in range(header_row + 1, min(header_row + 6, len(df))):
                        sample_rows.append(df.iloc[i].fillna("").to_dict())

                    preview["sheets"].append({
                        "name": sheet_name,
                        "kind": kind,
                        "header_row": int(header_row),
                        "columns_detected": list(mapping.keys()),
                        "total_rows_detected": int(len(df) - header_row - 1),
                        "sample": sample_rows
                    })

                return preview
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}

    @staticmethod
    def process_document(db: Session, tenant_id: UUID, document_id: UUID, file_path: str) -> int:
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return 0

        try:
            with pd.ExcelFile(path) as xls:
                total_created = 0
                logger.info(f"--- Starting processing for document {document_id} ---")

                for sheet_name in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
                    created_in_sheet = ExcelProcessingService._process_generic_sheet(db, tenant_id, document_id, sheet_name, df)
                    total_created += created_in_sheet
                    logger.info(f"Sheet '{sheet_name}': {created_in_sheet} records created.")

                logger.info(f"--- Finished processing document {document_id}: Total {total_created} records ---")
                return total_created
        except Exception as e:
            logger.error(f"Error processing Excel {file_path}: {str(e)}")
            raise e

    @staticmethod
    def _process_generic_sheet(db: Session, tenant_id: UUID, document_id: UUID, sheet_name: str, df: pd.DataFrame) -> int:
        if df.empty:
            return 0
            
        header_row, mapping = ExcelProcessingService._find_table_start(df)
        if not mapping or len(mapping) < 2:
            logger.info(f"Sheet '{sheet_name}': Table not found (mapping too sparse).")
            return 0

        logger.info(f"Sheet '{sheet_name}': Header found at row {header_row}. Mapping: {list(mapping.keys())}")

        sample_for_class = df.iloc[header_row+1:header_row+6] if len(df) > header_row + 1 else pd.DataFrame()
        kind = ExcelProcessingService._classify_sheet(sheet_name, mapping, sample_for_class)
        
        imported = 0
        skipped_duplicate = 0
        skipped_empty = 0
        skipped_error = 0
        
        # Process from header_row + 1 onwards
        for i in range(header_row + 1, len(df)):
            row = df.iloc[i]
            
            try:
                # Extract values using mapping
                m_date_val = row.iloc[mapping["movement_date"]] if "movement_date" in mapping else None
                total_val = row.iloc[mapping["total_amount"]] if "total_amount" in mapping else None
                
                if pd.isna(m_date_val) or pd.isna(total_val):
                    skipped_empty += 1
                    continue
                
                m_date = ExcelProcessingService._to_date(m_date_val)
                total = ExcelProcessingService._to_decimal(total_val)
                
                # Check for sign-based kind override
                row_kind = kind
                if total < 0 and sheet_name.lower() == "movimientos sin factura":
                    row_kind = "expense"
                    total = abs(total)
                elif total > 0 and sheet_name.lower() == "movimientos sin factura":
                    row_kind = "income"

                tp_name = str(row.iloc[mapping["third_party_name"]]) if "third_party_name" in mapping and not pd.isna(row.iloc[mapping["third_party_name"]]) else "Desconocido"
                ref = str(row.iloc[mapping["source_reference"]]) if "source_reference" in mapping and not pd.isna(row.iloc[mapping["source_reference"]]) else None
                concept = str(row.iloc[mapping["concept"]]) if "concept" in mapping and not pd.isna(row.iloc[mapping["concept"]]) else f"Importado de {sheet_name}"
                
                base = ExcelProcessingService._to_decimal(row.iloc[mapping["net_amount"]]) if "net_amount" in mapping else Decimal("0.00")
                iva = ExcelProcessingService._to_decimal(row.iloc[mapping["tax_amount"]]) if "tax_amount" in mapping else Decimal("0.00")
                withholding = ExcelProcessingService._to_decimal(row.iloc[mapping["withholding_amount"]]) if "withholding_amount" in mapping else Decimal("0.00")

                if base == 0 and total != 0:
                    if iva == 0:
                        base = total - withholding
                    else:
                        base = total - iva - withholding

                fingerprint = ExcelProcessingService._generate_fingerprint(tenant_id, {
                    "movement_date": m_date,
                    "third_party_name": tp_name,
                    "total_amount": total,
                    "source_reference": ref,
                    "kind": row_kind,
                    "concept": concept
                })

                if ExcelProcessingService._check_exists(db, fingerprint):
                    skipped_duplicate += 1
                    continue

                category = "General"
                if sheet_name == "Ventas": category = "Ventas"
                elif "alquiler" in (concept + sheet_name).lower() or withholding > 0: category = "Alquiler"
                elif "nomina" in concept.lower() or "nómina" in concept.lower(): category = "Nóminas"

                movement = FinancialMovement(
                    tenant_id=tenant_id,
                    source_document_id=document_id,
                    source_type="excel_import",
                    kind=row_kind,
                    movement_date=m_date,
                    source_reference=ref,
                    net_amount=base,
                    tax_amount=iva,
                    withholding_amount=withholding,
                    total_amount=total,
                    third_party_name=tp_name,
                    concept=concept,
                    category=category,
                    status="proposed",
                    needs_review=True,
                    fingerprint=fingerprint,
                    source_data=json.dumps(row.to_dict(), default=str)
                )
                db.add(movement)
                imported += 1
            except Exception as e:
                skipped_error += 1
                logger.warning(f"Row {i} in '{sheet_name}' error: {str(e)}")

        logger.info(f"Sheet summary: {imported} imported, {skipped_duplicate} duplicates, {skipped_empty} empty/invalid, {skipped_error} errors.")
        db.commit()
        return imported

    @staticmethod
    def _to_decimal(value) -> Decimal:
        if pd.isna(value):
            return Decimal("0.00")
        if isinstance(value, str):
            value = value.replace("€", "").replace(".", "").replace(",", ".").strip()
        try:
            return Decimal(str(value)).quantize(Decimal("0.01"))
        except:
            return Decimal("0.00")

    @staticmethod
    def _to_date(value) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
                try:
                    return datetime.strptime(value, fmt)
                except:
                    continue
        return datetime.utcnow()
