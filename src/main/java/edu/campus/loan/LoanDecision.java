package edu.campus.loan;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

/** Created by LoanService; rejected requests have no due date. */
public final class LoanDecision {
    private final LocalDate dueDate;
    private final List<RejectionReason> rejectionReasons;

    LoanDecision(LocalDate dueDate, List<RejectionReason> rejectionReasons) {
        this.dueDate = dueDate;
        this.rejectionReasons = List.copyOf(rejectionReasons);
    }

    public boolean isApproved() {
        return rejectionReasons.isEmpty();
    }

    public Optional<LocalDate> dueDate() {
        return Optional.ofNullable(dueDate);
    }

    public List<RejectionReason> rejectionReasons() {
        return rejectionReasons;
    }
}
