# Library loan schema — synthetic example

Version: demo-1. Dialect: PostgreSQL.

```sql
CREATE TABLE members (
    id bigint PRIMARY KEY,
    display_name text NOT NULL
);

CREATE TABLE book_copies (
    id bigint PRIMARY KEY,
    title text NOT NULL
);

CREATE TABLE loans (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    member_id bigint NOT NULL REFERENCES members(id),
    copy_id bigint NOT NULL REFERENCES book_copies(id),
    created_at timestamptz NOT NULL,
    due_at timestamptz NOT NULL,
    returned_at timestamptz,
    CHECK (due_at > created_at),
    CHECK (returned_at IS NULL OR returned_at >= created_at)
);

CREATE UNIQUE INDEX one_active_loan_per_copy
    ON loans(copy_id) WHERE returned_at IS NULL;
```

The database enforces one active loan per copy and timestamp ordering. The maximum of three active loans per member and the fourteen-day due interval are application rules described in the design; this SQL does not independently enforce those two rules.
