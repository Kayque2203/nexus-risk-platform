from sqlalchemy.orm import Session

from app.repositories.process_repository import ProcessRepository
from app.schemas.process import ProcessCreate, ProcessUpdate
from app.services.audit_service import AuditService
from app.models.process import Process


class ProcessService:
    def __init__(self, db: Session):
        self.repository = ProcessRepository(db)
        self.audit = AuditService(db)

    def list_processes(self, skip: int = 0, limit: int = 100) -> list[Process]:
        return self.repository.list_all(skip=skip, limit=limit)

    def get_process(self, process_id: str) -> Process | None:
        return self.repository.get_by_id(process_id)

    def create_process(self, data: ProcessCreate, user_id: str | None = None) -> Process:
        process = self.repository.create(data)
        self.audit.log_create(user_id, "Process", process.id)
        return process

    def update_process(
        self, process_id: str, data: ProcessUpdate, user_id: str | None = None
    ) -> Process | None:
        process = self.repository.get_by_id(process_id)
        if not process:
            return None

        before = {
            "name": process.name,
            "status": process.status,
            "priority": process.priority,
            "department": process.department,
        }

        updated = self.repository.update(process, data)

        after = {
            "name": updated.name,
            "status": updated.status,
            "priority": updated.priority,
            "department": updated.department,
        }

        self.audit.log_update(user_id, "Process", updated.id, before, after)
        return updated

    def delete_process(self, process_id: str, user_id: str | None = None) -> bool:
        process = self.repository.get_by_id(process_id)
        if not process:
            return False
        self.repository.delete(process)
        self.audit.log_delete(user_id, "Process", process_id)
        return True
