from datetime import UTC, datetime


def utc_now() -> datetime:
    """Hora atual em UTC sem fuso (naive), igual ao formato ja gravado no banco."""
    return datetime.now(UTC).replace(tzinfo=None)
