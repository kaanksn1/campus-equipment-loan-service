package edu.campus.loan;

import java.time.LocalDate;
import java.time.temporal.ChronoUnit;

/** Calendar-day late fees, independent of the borrower's current eligibility. */
public final class OverdueFeeService {
    public static final long DAILY_FEE_CENTS = 100;
    public static final long MAXIMUM_FEE_CENTS = 5_000;

    public long calculateFeeCents(LocalDate checkoutDate, LocalDate dueDate, LocalDate returnDate) {
        if (checkoutDate == null || dueDate == null || returnDate == null) {
            throw new IllegalArgumentException("Checkout, due and return dates are required.");
        }
        if (!dueDate.isAfter(checkoutDate)) {
            throw new IllegalArgumentException("Due date must be after checkout date.");
        }
        if (returnDate.isBefore(checkoutDate)) {
            throw new IllegalArgumentException("Return date cannot be before checkout date.");
        }
        long lateDays = ChronoUnit.DAYS.between(dueDate, returnDate);
        if (lateDays <= 0) {
            return 0;
        }
        // Even the full LocalDate range times 100 fits in long; no floating-point arithmetic.
        return Math.min(lateDays * DAILY_FEE_CENTS, MAXIMUM_FEE_CENTS);
    }
}
