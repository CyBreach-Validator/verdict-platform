"""Guard for N-D13: duplicate detection on `content_hash`.

The conflict asked for a unique constraint on the verdict hash. Implemented
literally as a global UNIQUE, that would *break* the product: `content_hash` is
derived from the seven contract fields, and both `correct_verdict` and
`revalidate_verdict` are deterministic, so re-validating an unchanged verdict
legitimately reproduces the same hash as the row it supersedes.

The constraint therefore has to be PARTIAL -- covering only current
(non-superseded) rows -- and the supersede-then-insert order has to be
explicit, because SQLAlchemy's unit of work emits INSERTs before UPDATEs for
the same mapper. If that order regresses, these tests fail.
"""

import os
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

os.environ.setdefault(
    "DATABASE_URL", "postgresql://user:pass@localhost:5432/verdict_db"
)

sys.path.insert(0, str(BACKEND_DIR))

import app.models.verdict  # noqa: E402
from sqlalchemy.dialects import postgresql  # noqa: E402
from sqlalchemy.schema import CreateIndex  # noqa: E402

INDEX_NAME = "uq_verdict_events_content_hash_active"


# --- the constraint itself -------------------------------------------------


def test_partial_unique_index_exists_on_model():
    from app.database.base import Base

    import app.models.verdict  # noqa: F401

    indexes = {idx.name: idx for idx in Base.metadata.tables["verdict_events"].indexes}

    assert INDEX_NAME in indexes, (
        f"verdict_events is missing the {INDEX_NAME} index; "
        f"present: {sorted(indexes)}"
    )

    index = indexes[INDEX_NAME]

    assert index.unique, f"{INDEX_NAME} must be UNIQUE to catch double-writes"
    assert [c.name for c in index.columns] == ["content_hash"]


def test_partial_unique_index_is_scoped_to_current_rows():
    """The WHERE clause is what makes this safe. Without it, the index is a
    global unique constraint and revalidation breaks."""

    from app.database.base import Base

    import app.models.verdict  # noqa: F401

    # `Table.indexes` is an unordered set, so it cannot be subscripted.
    index = next(
        i
        for i in Base.metadata.tables["verdict_events"].indexes
        if i.name == INDEX_NAME
    )

    ddl = str(CreateIndex(index).compile(dialect=postgresql.dialect()))

    assert "WHERE is_superseded = false" in ddl, (
        "the index must be partial (`WHERE is_superseded = false`). A global "
        f"unique constraint would reject the re-insert of a re-validated, "
        f"unchanged verdict. Rendered DDL was:\n{ddl}"
    )


def test_migration_creates_the_same_partial_index():
    """N-D2 discipline: the migration must match the model, not just the
    columns. Column-level parity alone would not have caught a missing index."""

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    assert f"CREATE UNIQUE INDEX {INDEX_NAME}" in result.stdout, (
        "the migration does not create the unique index the model declares"
    )

    create_line = next(
        line
        for line in result.stdout.splitlines()
        if f"CREATE UNIQUE INDEX {INDEX_NAME}" in line
    )
    assert "WHERE is_superseded = false" in create_line, (
        f"migration index is not partial: {create_line}"
    )


def test_downgrade_drops_the_index():
    """A dropped-but-not-recreated index turns `alembic downgrade` into a
    one-way trip that the next upgrade cannot repair."""

    source = (
        BACKEND_DIR / "alembic" / "versions" / "0001_initial_verdict_platform.py"
    ).read_text(encoding="utf-8")

    downgrade_body = source.split("def downgrade()", 1)[1]

    assert INDEX_NAME in downgrade_body, "downgrade() never drops " + INDEX_NAME


# --- the insert ordering that makes the constraint satisfiable --------------


class _RecordingSession:
    """Records the order of `add`/`commit` so the supersede-before-insert
    requirement can be asserted without a live database."""

    def __init__(self, old_verdict, fail_insert=False):
        self.old_verdict = old_verdict
        self.fail_insert = fail_insert
        self.ops = []
        self._next_id = 99
        self._pending_adds = 0

        self._filter_result = old_verdict
        self._existing = old_verdict

    # -- query plumbing ----------------------------------------------------
    def query(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        # The service filters on `Verdict.id` to load the row, then on
        # `content_hash` to look for an existing active row. Both resolve to
        # our single stub row here.
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return self._filter_result

    def all(self):
        return [self.old_verdict]

    # -- mutation ----------------------------------------------------------
    def add(self, obj):
        self.ops.append(("add", obj))
        self._pending_adds += 1

    def commit(self):
        self.ops.append(("commit", None))

        # Only fail the flush of a pending INSERT. The service's first commit
        # retires the old row without adding anything, and that one must
        # succeed -- failing it would not exercise the restore path at all.
        if self.fail_insert and self._pending_adds:
            self._pending_adds = 0
            _raise_integrity_error()

        self._pending_adds = 0

    def refresh(self, obj):
        self.ops.append(("refresh", obj))
        if getattr(obj, "id", None) is None:
            obj.id = self._next_id
            self._next_id += 1

    def rollback(self):
        self.ops.append(("rollback", None))
        self._pending_adds = 0

    # -- assertions helpers ------------------------------------------------
    def index_of(self, kind):
        return next(i for i, (op, _) in enumerate(self.ops) if op == kind)

    def index_of_old_superseded_set(self):
        """Where in the op log the old row was retired."""
        for i, (op, _) in enumerate(self.ops):
            if op == "commit" and self.old_verdict.is_superseded:
                return i
        raise AssertionError(
            "the old verdict was never committed as superseded. Recorded ops: "
            + ", ".join(op for op, _ in self.ops)
        )


def _raise_integrity_error():
    from sqlalchemy.exc import IntegrityError

    raise IntegrityError("INSERT", {}, Exception("duplicate key value"))


class _StubVerdict:
    """Minimal stand-in for the ORM row."""

    def __init__(self, **kwargs):
        self.id = 1
        self.is_superseded = False
        self.superseded_by = None
        for key, value in kwargs.items():
            setattr(self, key, value)


def _old_verdict():
    return _StubVerdict(
        action_id="act-1",
        rule_id="r-1",
        rule_name="Suspicious PowerShell",
        verdict="Detected",
        confidence=0.9,
        causal_chain=["step one"],
        mttd_seconds=12.0,
        matched_evidence_ref="ev-1",
        regulatory_control_refs=["AC-1"],
        event_data='{"a": 1}',
        content_hash="0" * 64,
        created_at=None,
    )


def test_correct_verdict_retires_the_old_row_before_inserting():
    from app.services import verdict_service

    old = _old_verdict()
    session = _RecordingSession(old)

    # Neutralise the Kafka side effect; this test is about DB ordering.
    verdict_service.publish_corrected_verdict = lambda *a, **k: None

    verdict_service.correct_verdict(session, 1, "Missed", confidence=0.2)

    add_at = session.index_of("add")
    retired_at = session.index_of_old_superseded_set()

    assert retired_at < add_at, (
        "the old row must be committed as superseded BEFORE the replacement is "
        "inserted. The partial unique index covers current rows only, so an "
        "insert-first order fails the constraint whenever the re-computed hash "
        "matches the superseded row's."
    )


def test_correct_verdict_rolls_back_the_supersession_if_the_insert_fails():
    """Otherwise a failed insert silently removes the only current verdict for
    the action_id from every feed."""

    from app.services import verdict_service

    old = _old_verdict()
    session = _RecordingSession(old, fail_insert=True)

    verdict_service.publish_corrected_verdict = lambda *a, **k: None

    try:
        verdict_service.correct_verdict(session, 1, "Missed", confidence=0.2)
    except Exception:
        pass
    else:
        raise AssertionError("the IntegrityError should have propagated")

    assert old.is_superseded is False, (
        "after a failed replacement insert the original verdict must be "
        "restored to is_superseded=False, or the action_id is left with no "
        "current verdict at all"
    )

    rollback_at = session.index_of("rollback")
    commits = [i for i, (op, _) in enumerate(session.ops) if op == "commit"]

    assert any(i > rollback_at for i in commits), (
        "the restore must be committed after the rollback; setting the flag "
        "inside the aborted transaction would be discarded with it"
    )


# --- duplicate submissions are idempotent, not 500s ------------------------


def test_save_verdict_returns_the_existing_row_on_duplicate():
    from app.services import verdict_service

    existing = _old_verdict()
    session = _RecordingSession(existing, fail_insert=True)

    row, payload = verdict_service.save_verdict(
        session,
        action_id="act-1",
        rule_id="r-1",
        rule_name="Suspicious PowerShell",
        verdict="Detected",
        confidence=0.9,
        event={"a": 1},
    )

    assert row is existing, (
        "re-submitting an identical verdict must return the stored row, not "
        "raise: the partial unique index means the insert cannot succeed"
    )
    assert payload["content_hash"] == verdict_service.get_verdict_payload(existing)[
        "content_hash"
    ], "the returned payload must match the row that is actually stored"
