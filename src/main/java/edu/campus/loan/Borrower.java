package edu.campus.loan;

/** An immutable borrower snapshot. Monetary values are integer kurus (100 = 1 TL). */
public record Borrower(Role role, boolean activeMembership, int currentLoanCount,
                       long outstandingFeeCents) {
    public Borrower {
        if (role == null) {
            throw new IllegalArgumentException("Borrower role is required.");
        }
        if (currentLoanCount < 0) {
            throw new IllegalArgumentException("Current loan count cannot be negative.");
        }
        if (outstandingFeeCents < 0) {
            throw new IllegalArgumentException("Outstanding fees cannot be negative.");
        }
    }
}
