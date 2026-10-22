# Library loan requirements — synthetic example

Version: demo-1

REQ-01: An authenticated member can request a loan for an available copy of a book.

REQ-02: A member may have at most three active loans. A request exceeding this limit must be rejected before a loan is created.

REQ-03: Every new loan records its member, book copy, creation time and due time. The due time is fourteen days after creation.

REQ-04: Returning a copy records a return time and makes the copy available for another loan.

REQ-05: A librarian can list overdue active loans. A returned loan is not active.

External payment handling and fine calculation are outside this example's scope.
