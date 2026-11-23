package edu.campus.loan;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class BorrowerTest {
    @ParameterizedTest(name = "MODEL-{0}: negative {1}")
    @CsvSource({"01, -1, 0", "02, -2147483648, 0", "03, 0, -1", "04, 0, -9223372036854775808"})
    void negativeValues(String suffix, int count, long fees) {
        CaseEvidence.invalid("MODEL-" + suffix, "FR-01", "count=" + count + "; fees=" + fees,
                () -> new Borrower(Role.STUDENT, true, count, fees));
    }

    @Test
    void missingRole() {
        CaseEvidence.invalid("MODEL-05", "FR-01", "role=null",
                () -> new Borrower(null, true, 0, 0));
    }

    @Test
    void zeroAndLargeValuesAreValidSnapshots() {
        Borrower zero = new Borrower(Role.STUDENT, true, 0, 0);
        Borrower large = new Borrower(Role.STAFF, false, Integer.MAX_VALUE, Long.MAX_VALUE);
        CaseEvidence.check("MODEL-06", "FR-01", "Equivalence partitioning",
                "zero snapshot; count=INT_MAX; fees=LONG_MAX",
                "STUDENT,true,0,0;STAFF,false,2147483647,9223372036854775807",
                zero.role() + "," + zero.activeMembership() + "," + zero.currentLoanCount() + ","
                        + zero.outstandingFeeCents() + ";" + large.role() + "," + large.activeMembership()
                        + "," + large.currentLoanCount() + "," + large.outstandingFeeCents());
    }
}
