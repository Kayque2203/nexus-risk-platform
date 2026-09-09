from sqlalchemy.orm import Session
from app.models.process import Process
from app.schemas.process import ProcessCreate, ProcessUpdate


class ProcessRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, process_id: str) -> Process | None:
        return self.db.query(Process).filter(Process.id == process_id).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> list[Process]:
        return self.db.query(Process).offset(skip).limit(limit).all()

    def create(self, data: ProcessCreate) -> Process:
        process = Process(**data.model_dump())
        self.db.add(process)
        self.db.commit()
        self.db.refresh(process)
        return process

    def update(self, process: Process, data: ProcessUpdate) -> Process:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(process, field, value)
        self.db.commit()
        self.db.refresh(process)
        return process

    def delete(self, process: Process) -> None:
        self.db.delete(process)
        self.db.commit()
