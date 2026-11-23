package edu.campus.loan;

import java.time.DateTimeException;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

/** Stateless loan evaluation. A decision does not issue or reserve equipment. */
public final class LoanService {
    public LoanDecision requestLoan(Borrower borrower, LocalDate checkoutDate, int requestedDays) {
        if (borrower == null) {
            throw new IllegalArgumentException("Borrower is required.");
        }
        if (checkoutDate == null) {
            throw new IllegalArgumentException("Checkout date is required.");
        }
        if (requestedDays < 1 || requestedDays > borrower.role().maximumLoanDays()) {
            throw new IllegalArgumentException("Requested days must be between 1 and "
                    + borrower.role().maximumLoanDays() + ".");
        }

        // Validate the entire request before evaluating eligibility, even for a blocked borrower.
        LocalDate candidateDueDate;
        try {
            candidateDueDate = checkoutDate.plusDays(requestedDays);
        } catch (DateTimeException ex) {
            throw new IllegalArgumentException("Due date exceeds the supported calendar range.", ex);
        }

        List<RejectionReason> reasons = new ArrayList<>();
        if (!borrower.activeMembership()) {
            reasons.add(RejectionReason.INACTIVE_MEMBERSHIP);
        }
        if (borrower.outstandingFeeCents() > 0) {
            reasons.add(RejectionReason.OUTSTANDING_FEES);
        }
        if (borrower.currentLoanCount() >= borrower.role().loanLimit()) {
            reasons.add(RejectionReason.LOAN_LIMIT_REACHED);
        }
        return new LoanDecision(reasons.isEmpty() ? candidateDueDate : null, reasons);
    }
}
