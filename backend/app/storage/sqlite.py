from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from app.consent.models import ConsentEvent, ConsentRecord
    from app.guardian_console.admin_case_models import AdminCase
    from app.trusted_circle.trusted_circle_models import TrustedCircleEscalationRecord

# NOTE: the model classes above are imported *locally* inside the methods that
# deserialize rows (not at module top level). These stores are pulled in eagerly
# via `app.storage.__init__`, and the model packages transitively import services
# that import storage back — so a top-level import here creates a cycle. Local
# runtime imports (the pattern already used for AdminCaseMemoryStore below) both
# avoid the cycle and make the names available at runtime.

from app.storage.config import storage_config


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class SQLiteConnection:
    def __init__(self, path: str) -> None:
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.RLock()

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> sqlite3.Cursor:
        with self._lock:
            cursor = self._conn.execute(sql, params)
            self._conn.commit()
            return cursor

    def close(self) -> None:
        with self._lock:
            self._conn.close()


class SQLiteAdminCaseStore:
    def __init__(self, connection: SQLiteConnection) -> None:
        self._conn = connection
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_cases (
                case_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

    def ensure_initialized(self) -> None:
        if self.case_count() == 0:
            from app.storage.memory import AdminCaseMemoryStore

            memory = AdminCaseMemoryStore()
            for case in memory.list_cases():
                self.save_case(case)

    def list_cases(self) -> List[AdminCase]:
        from app.guardian_console.admin_case_models import AdminCase

        rows = self._conn.execute("SELECT payload FROM admin_cases ORDER BY updated_at DESC").fetchall()
        return [AdminCase.model_validate(json.loads(row["payload"])) for row in rows]

    def get_case(self, case_id: str) -> Optional[AdminCase]:
        from app.guardian_console.admin_case_models import AdminCase

        row = self._conn.execute("SELECT payload FROM admin_cases WHERE case_id = ?", (case_id,)).fetchone()
        return AdminCase.model_validate(json.loads(row["payload"])) if row else None

    def save_case(self, case: AdminCase) -> AdminCase:
        existing = self.get_case(case.case_id)
        if existing:
            case = case.model_copy(update={"created_at": existing.created_at})
        payload = case.model_dump_json(by_alias=False, exclude_none=True)
        self._conn.execute(
            "INSERT INTO admin_cases(case_id, payload, created_at, updated_at) VALUES (?, ?, ?, ?)"
            " ON CONFLICT(case_id) DO UPDATE SET payload=excluded.payload, created_at=excluded.created_at, updated_at=excluded.updated_at",
            (case.case_id, payload, case.created_at, case.updated_at),
        )
        return case

    def upsert_case(self, case: AdminCase) -> AdminCase:
        existing = self.get_case(case.case_id)
        updated_at = _now_iso()
        created_at = existing.created_at if existing else case.created_at
        case = case.model_copy(update={"created_at": created_at, "updated_at": updated_at})
        return self.save_case(case)

    def case_count(self) -> int:
        row = self._conn.execute("SELECT COUNT(1) AS total FROM admin_cases").fetchone()
        return int(row["total"]) if row else 0


class SQLiteConsentStore:
    def __init__(self, connection: SQLiteConnection) -> None:
        self._conn = connection
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS consent_records (
                protected_person_id TEXT PRIMARY KEY,
                consent_id TEXT NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS consent_events (
                consent_event_id TEXT PRIMARY KEY,
                consent_id TEXT NOT NULL,
                payload TEXT NOT NULL,
                occurred_at TEXT NOT NULL
            )
            """
        )

    def get_or_create_record(
        self,
        protected_person_id: str,
        protected_person_alias: str = "Pessoa protegida",
        guardian_id: str | None = None,
        guardian_alias: str | None = None,
        channel_provider: str = "mock",
    ) -> ConsentRecord:
        from app.consent.models import ConsentRecord

        record = self.get_record(protected_person_id)
        if record:
            return record
        record = ConsentRecord(
            protected_person_id=protected_person_id,
            protected_person_alias=protected_person_alias,
            guardian_id=guardian_id,
            guardian_alias=guardian_alias,
            channel_provider=channel_provider,
        )
        return self.save_record(record)

    def save_record(self, record: ConsentRecord) -> ConsentRecord:
        payload = record.model_dump_json(by_alias=False, exclude_none=True)
        self._conn.execute(
            "INSERT INTO consent_records(protected_person_id, consent_id, payload) VALUES (?, ?, ?)"
            " ON CONFLICT(protected_person_id) DO UPDATE SET consent_id=excluded.consent_id, payload=excluded.payload",
            (record.protected_person_id, record.consent_id, payload),
        )
        return record

    def append_event(self, event: ConsentEvent) -> ConsentEvent:
        payload = event.model_dump_json(by_alias=False, exclude_none=True)
        self._conn.execute(
            "INSERT INTO consent_events(consent_event_id, consent_id, payload, occurred_at) VALUES (?, ?, ?, ?)",
            (event.consent_event_id, event.consent_id, payload, event.occurred_at.isoformat()),
        )
        return event

    def list_events(self, consent_id: str) -> List[ConsentEvent]:
        from app.consent.models import ConsentEvent

        rows = self._conn.execute(
            "SELECT payload FROM consent_events WHERE consent_id = ? ORDER BY occurred_at ASC",
            (consent_id,),
        ).fetchall()
        return [ConsentEvent.model_validate(json.loads(row["payload"])) for row in rows]

    def get_record(self, protected_person_id: str) -> Optional[ConsentRecord]:
        from app.consent.models import ConsentRecord

        row = self._conn.execute("SELECT payload FROM consent_records WHERE protected_person_id = ?", (protected_person_id,)).fetchone()
        return ConsentRecord.model_validate(json.loads(row["payload"])) if row else None


class SQLiteProofTrustStore:
    def __init__(self, connection: SQLiteConnection) -> None:
        self._conn = connection
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS proof_trust_sessions (
                session_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

    def save_session(self, record: dict) -> dict:
        payload = json.dumps(record, ensure_ascii=False)
        updated_at = record.get("updated_at") or _now_iso()
        self._conn.execute(
            "INSERT INTO proof_trust_sessions(session_id, payload, updated_at) VALUES (?, ?, ?)"
            " ON CONFLICT(session_id) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at",
            (record["session_id"], payload, updated_at),
        )
        return record

    def get_session(self, session_id: str) -> Optional[dict]:
        row = self._conn.execute("SELECT payload FROM proof_trust_sessions WHERE session_id = ?", (session_id,)).fetchone()
        return json.loads(row["payload"]) if row else None


class SQLiteTrustedCircleStore:
    def __init__(self, connection: SQLiteConnection) -> None:
        self._conn = connection
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trusted_circle_escalations (
                escalation_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                case_id TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

    def save(self, record: TrustedCircleEscalationRecord) -> TrustedCircleEscalationRecord:
        payload = record.model_dump_json(by_alias=False, exclude_none=True)
        self._conn.execute(
            "INSERT INTO trusted_circle_escalations(escalation_id, payload, case_id, created_at) VALUES (?, ?, ?, ?)"
            " ON CONFLICT(escalation_id) DO UPDATE SET payload=excluded.payload, case_id=excluded.case_id, created_at=excluded.created_at",
            (record.escalation_id, payload, record.case_id, record.created_at),
        )
        return record

    def get(self, escalation_id: str) -> Optional[TrustedCircleEscalationRecord]:
        from app.trusted_circle.trusted_circle_models import TrustedCircleEscalationRecord

        row = self._conn.execute("SELECT payload FROM trusted_circle_escalations WHERE escalation_id = ?", (escalation_id,)).fetchone()
        return TrustedCircleEscalationRecord.model_validate(json.loads(row["payload"])) if row else None

    def list_all(self) -> List[TrustedCircleEscalationRecord]:
        from app.trusted_circle.trusted_circle_models import TrustedCircleEscalationRecord

        rows = self._conn.execute("SELECT payload FROM trusted_circle_escalations ORDER BY created_at DESC").fetchall()
        return [TrustedCircleEscalationRecord.model_validate(json.loads(row["payload"])) for row in rows]

    def count(self) -> int:
        row = self._conn.execute("SELECT COUNT(1) AS total FROM trusted_circle_escalations").fetchone()
        return int(row["total"]) if row else 0

    def latest_for_case(self, case_id: str) -> Optional[TrustedCircleEscalationRecord]:
        from app.trusted_circle.trusted_circle_models import TrustedCircleEscalationRecord

        row = self._conn.execute(
            "SELECT payload FROM trusted_circle_escalations WHERE case_id = ? ORDER BY created_at DESC LIMIT 1", (case_id,)).fetchone()
        return TrustedCircleEscalationRecord.model_validate(json.loads(row["payload"])) if row else None


class SQLiteStorage:
    def __init__(self, path: str | None = None) -> None:
        self._path = path or storage_config.sqlite_path()
        self._connection = SQLiteConnection(self._path)
        self.admin_case_store = SQLiteAdminCaseStore(self._connection)
        self.consent_store = SQLiteConsentStore(self._connection)
        self.proof_trust_store = SQLiteProofTrustStore(self._connection)
        self.trusted_circle_store = SQLiteTrustedCircleStore(self._connection)

    def close(self) -> None:
        self._connection.close()
