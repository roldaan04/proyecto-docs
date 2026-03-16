import hashlib
import os
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.tenant import Tenant
from app.models.user import User
from app.models.job import Job


class DocumentService:
    UPLOAD_ROOT = Path("storage/uploads")
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _ensure_tenant_folder(tenant_id: str) -> Path:
        tenant_folder = DocumentService.UPLOAD_ROOT / tenant_id
        tenant_folder.mkdir(parents=True, exist_ok=True)
        return tenant_folder

    @staticmethod
    async def save_uploaded_document(
        db: Session,
        file: UploadFile,
        current_user: User,
        current_tenant: Tenant
    ) -> Document:
        if not file.filename:
            raise ValueError("El archivo no tiene nombre")

        content = await file.read()

        if not content:
            raise ValueError("El archivo está vacío")

        tenant_folder = DocumentService._ensure_tenant_folder(str(current_tenant.id))

        extension = Path(file.filename).suffix
        internal_filename = f"{uuid.uuid4()}{extension}"
        file_path = tenant_folder / internal_filename

        with open(file_path, "wb") as f:
            f.write(content)

        checksum = hashlib.sha256(content).hexdigest()

        document = Document(
            tenant_id=current_tenant.id,
            uploaded_by_user_id=current_user.id,
            storage_key=str(file_path).replace("\\", "/"),
            filename_original=file.filename,
            mime_type=file.content_type or "application/octet-stream",
            file_size=len(content),
            checksum=checksum,
            upload_status="uploaded",
            processing_status="pending",
            document_type=None,
            confidence_score=None,
            error_message=None
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    @staticmethod
    def list_documents_by_tenant(db: Session, tenant_id: str):
        return (
            db.query(Document)
            .filter(Document.tenant_id == tenant_id)
            .order_by(Document.created_at.desc())
            .all()
        )

    @staticmethod
    def get_document_by_id(db: Session, tenant_id: str, document_id: str) -> Document | None:
        return (
            db.query(Document)
            .filter(
                Document.id == document_id,
                Document.tenant_id == tenant_id
            )
            .first()
        )

    @staticmethod
    def delete_document(db: Session, document: Document) -> None:
        # Borrar archivo físico si existe
        if document.storage_key:
            file_path = Path(document.storage_key)
            if file_path.exists() and file_path.is_file():
                try:
                    file_path.unlink()
                except OSError:
                    raise ValueError("No se pudo eliminar el archivo del almacenamiento")

        # Borrar jobs asociados si no tienes cascade ya configurado
        db.query(Job).filter(Job.document_id == document.id).delete(synchronize_session=False)

        # Borrar documento
        db.delete(document)
        db.commit()