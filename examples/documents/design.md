# Library loan design — synthetic example

Version: demo-1

## Loan creation

The API authenticates the member, locks the member record and requested copy in a database transaction, counts that member's active loans and checks that the copy has no active loan. It rejects requests at the active-loan limit of three. On success, it inserts a loan with a due time fourteen days after creation and commits.

The member lock serializes concurrent creation requests for the same member. The copy lock serializes requests for the same copy. A partial unique index is a second guard against two active loans for one copy.

## Returns and overdue listing

Returning a loan sets `returned_at` once. Availability is derived from the absence of an active loan, not stored in a separate copy-status column. The librarian view lists rows with `returned_at IS NULL` and `due_at` earlier than the current time.

## Trace references

The transaction/count check supports REQ-02. The stored timestamps support REQ-03 and REQ-04. The librarian-only listing supports REQ-05. Fine calculation is not designed here.
