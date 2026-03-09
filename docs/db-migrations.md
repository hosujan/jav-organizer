# Database Migrations Guide

This document describes how to move from inline schema initialization to ordered SQL migrations in `jav_toolkit`.

Goal:
- Keep schema changes deterministic and reviewable.
- Avoid scattered runtime `ALTER TABLE` logic.
- Support both fresh databases and upgrades of existing `.db` files.

## Target Pattern

1. Create a migration tracker table:
```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
  version TEXT PRIMARY KEY,
  applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

2. Store migrations as ordered `.sql` files:
- `src/jav_toolkit/migrations/0001_init.sql`
- `src/jav_toolkit/migrations/0002_drop_local_video_path.sql`
- `src/jav_toolkit/migrations/0003_add_indexes.sql`

3. On `open_db()` startup:
- Ensure `schema_migrations` exists.
- Read already-applied `version` values.
- Run pending migration files in lexical order.
- Record each applied version in `schema_migrations`.

4. Keep `SCHEMA` only as optional bootstrap fallback, or move full bootstrap into `0001_init.sql` and remove inline schema execution.

## Recommended File Layout

```text
src/jav_toolkit/
  config.py
  migrations/
    0001_init.sql
    0002_*.sql
    ...
```

Rationale:
- Keeps migration assets close to DB code.
- Allows packaging later if needed.

## `open_db()` Integration Blueprint

In `src/jav_toolkit/config.py`, add helpers:
- `ensure_migration_table(conn)`
- `list_migration_files()`
- `get_applied_migrations(conn)`
- `apply_pending_migrations(conn)`

Then call `apply_pending_migrations(conn)` inside `open_db()` before returning the connection.

Pseudo-flow:

```python
def open_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    apply_pending_migrations(conn)
    return conn
```

Implementation details:
- Sort files by filename (`0001_...`, `0002_...`).
- Use filename stem (for example `0002_drop_local_video_path`) as `version`.
- Execute each file inside a transaction.
- Insert into `schema_migrations` only after successful SQL execution.
- Commit once all pending migrations succeed.
- Roll back on any failure and surface the exception.

## SQL Authoring Rules

Use these rules to keep migrations safe:
- Never edit a migration that has been applied in shared environments.
- Add a new migration for every schema change.
- Make SQL idempotent when reasonable (`IF EXISTS`/`IF NOT EXISTS`).
- Include data backfill steps in the same migration when required.

Prefer this:
- `0004_add_watch_state_index.sql`

Avoid this:
- editing `0001_init.sql` after release, unless no existing DBs rely on old history.

## Initial Bootstrap Strategy

Two valid options:

1. Migration-only bootstrap (recommended):
- Put full initial schema in `0001_init.sql`.
- `open_db()` always runs migration engine.
- No separate `SCHEMA` execution path.

2. Mixed bootstrap:
- Keep `SCHEMA` for brand-new DB creation.
- Still run migration engine for upgrades.
- Higher maintenance because schema logic exists in two places.

Use option 1 unless there is a strong reason not to.

## Error Handling and Logging

Suggested log style (matching project conventions):
- `[DB] applying migration 0002_drop_local_video_path`
- `[DB] migration applied 0002_drop_local_video_path`
- `[WARN] migration failed 0003_add_indexes: <error>`

Behavior on failure:
- Keep DB unchanged for the failing migration transaction.
- Stop startup and return a clear error.

## Verification Checklist

After implementing migration runner:

1. Fresh DB test:
- Delete local test DB.
- Start command that calls `open_db()`.
- Confirm all migrations are applied and tables exist.

2. Existing DB upgrade test:
- Use a DB created before latest migration.
- Start command that calls `open_db()`.
- Confirm only pending migrations are applied.

3. Re-run idempotency test:
- Start app twice.
- Confirm second run applies nothing new.

4. Manual inspection:
```sql
SELECT version, applied_at
FROM schema_migrations
ORDER BY version;
```

## Migration History Compaction (Squashing)

Compaction is optional, not required for correctness.

Keep full history by default. Consider squashing only when:
- Migration count becomes hard to manage.
- New environment setup time becomes noticeably slow.
- You are preparing a major release boundary.

Safe squashing approach:
1. Create a new baseline migration representing current schema.
2. Keep old files until all active environments are beyond old versions.
3. Communicate cutover clearly in release notes.

For this project size, keeping full history for now is usually the lowest-risk path.

