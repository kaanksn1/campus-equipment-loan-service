package edu.campus.loan;

import java.time.LocalDate;
import java.util.List;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.MethodSource;
import static org.junit.jupiter.api.Assertions.*;

class LoanServiceTest {
    private final LoanService service = new LoanService();
    private static final LocalDate CHECKOUT = LocalDate.of(2026, 11, 23);

    static Stream<Arguments> decisionCases() {
        // Independent eight-rule oracle; A=active, Z=zero debt, C=capacity available.
        Object[][] rules = {
                {"1", true, true, true, "[]"},
                {"2", true, true, false, "[LOAN_LIMIT_REACHED]"},
                {"3", true, false, true, "[OUTSTANDING_FEES]"},
                {"4", true, false, false, "[OUTSTANDING_FEES, LOAN_LIMIT_REACHED]"},
                {"5", false, true, true, "[INACTIVE_MEMBERSHIP]"},
                {"6", false, true, false, "[INACTIVE_MEMBERSHIP, LOAN_LIMIT_REACHED]"},
                {"7", false, false, true, "[INACTIVE_MEMBERSHIP, OUTSTANDING_FEES]"},
                {"8", false, false, false, "[INACTIVE_MEMBERSHIP, OUTSTANDING_FEES, LOAN_LIMIT_REACHED]"}
        };
        return Stream.of(Role.STUDENT, Role.STAFF).flatMap(role -> Stream.of(rules).map(row ->
                Arguments.of("DT-" + role + "-" + row[0], role, row[1], row[2], row[3], row[4])));
    }

    @ParameterizedTest(name = "{0}")
    @MethodSource("decisionCases")
    void decisionTable(String id, Role role, boolean active, boolean zeroDebt,
                       boolean capacity, String expectedReasons) {
        // Literal proposal limits keep the test oracle independent of Role's implementation.
        int limit = role == Role.STUDENT ? 3 : 5;
        Borrower borrower = new Borrower(role, active, capacity ? limit - 1 : limit, zeroDebt ? 0 : 1);
        LoanDecision decision = service.requestLoan(borrower, CHECKOUT, 7);
        boolean approved = "[]".equals(expectedReasons);
        String expected = approved + ";" + expectedReasons + ";" + (approved ? "2026-11-30" : "none");
        String actual = decision.isApproved() + ";" + decision.rejectionReasons() + ";"
                + decision.dueDate().map(Object::toString).orElse("none");
        CaseEvidence.check(id, "FR-02 FR-03 FR-05", "Decision table",
                role + "; active=" + active + "; debt=" + borrower.outstandingFeeCents()
                        + "; count=" + borrower.currentLoanCount() + "; days=7; checkout=" + CHECKOUT,
                expected, actual);
    }

    @ParameterizedTest(name = "CAP-{0}: {1}, count={2}")
    @CsvSource({"01, STUDENT, 0, true", "02, STUDENT, 2, true", "03, STUDENT, 3, false",
            "04, STUDENT, 4, false", "05, STAFF, 0, true", "06, STAFF, 4, true",
            "07, STAFF, 5, false", "08, STAFF, 6, false", "09, STAFF, 2147483647, false"})
    void capacityBoundary(String suffix, Role role, int count, boolean expected) {
        LoanDecision decision = service.requestLoan(new Borrower(role, true, count, 0), CHECKOUT, 1);
        CaseEvidence.check("CAP-" + suffix, "FR-02", "Boundary value analysis",
                role + "; active=true; debt=0; count=" + count + "; days=1; checkout=" + CHECKOUT,
                expected, decision.isApproved());
    }

    @ParameterizedTest(name = "DEBT-{0}: fees={1}")
    @CsvSource({"01, 0, true", "02, 1, false", "03, 100, false", "04, 9223372036854775807, false"})
    void outstandingDebtBoundary(String suffix, long fees, boolean expected) {
        CaseEvidence.check("DEBT-" + suffix, "FR-02", "Boundary value analysis",
                "STUDENT; active=true; count=0; fees=" + fees + "; days=1; checkout=" + CHECKOUT,
                expected, service.requestLoan(new Borrower(Role.STUDENT, true, 0, fees), CHECKOUT, 1).isApproved());
    }

    @ParameterizedTest(name = "PERIOD-{0}: {1}, days={2}")
    @CsvSource({"01, STUDENT, 0, invalid", "02, STUDENT, 1, 2026-11-24",
            "03, STUDENT, 6, 2026-11-29", "04, STUDENT, 7, 2026-11-30",
            "05, STUDENT, 8, invalid", "06, STAFF, 0, invalid", "07, STAFF, 1, 2026-11-24",
            "08, STAFF, 13, 2026-12-06", "09, STAFF, 14, 2026-12-07",
            "10, STAFF, 15, invalid", "11, STUDENT, -2147483648, invalid",
            "12, STAFF, 2147483647, invalid"})
    void loanPeriodBoundary(String suffix, Role role, int days, String expected) {
        Borrower borrower = new Borrower(role, true, 0, 0);
        String input = role + "; active=true; count=0; fees=0; days=" + days + "; checkout=" + CHECKOUT;
        if ("invalid".equals(expected)) {
            CaseEvidence.invalid("PERIOD-" + suffix, "FR-04", input,
                    () -> service.requestLoan(borrower, CHECKOUT, days));
        } else {
            CaseEvidence.check("PERIOD-" + suffix, "FR-04 FR-05", "Boundary value analysis", input,
                    expected, service.requestLoan(borrower, CHECKOUT, days).dueDate().orElseThrow().toString());
        }
    }

    @ParameterizedTest(name = "DATE-{0}: {1} + {2} days")
    @CsvSource({"01, 2026-01-31, 1, 2026-02-01", "02, 2026-12-31, 1, 2027-01-01",
            "03, 2024-02-28, 1, 2024-02-29", "04, 2024-02-28, 2, 2024-03-01",
            "05, 2026-02-28, 1, 2026-03-01", "06, +999999999-12-30, 1, +999999999-12-31",
            "07, -999999999-01-01, 1, -999999999-01-02"})
    void calendarDates(String suffix, LocalDate checkout, int days, String expected) {
        CaseEvidence.check("DATE-" + suffix, "FR-05", "Boundary value analysis",
                "STUDENT; active=true; count=0; debt=0; checkout=" + checkout + "; days=" + days,
                expected, service.requestLoan(new Borrower(Role.STUDENT, true, 0, 0), checkout, days)
                        .dueDate().orElseThrow().toString());
    }

    @Test
    void missingBorrower() {
        CaseEvidence.invalid("LOAN-NEG-01", "FR-01", "borrower=null; checkout=" + CHECKOUT + "; days=1",
                () -> service.requestLoan(null, CHECKOUT, 1));
    }

    @Test
    void missingCheckout() {
        CaseEvidence.invalid("LOAN-NEG-02", "FR-05", "STUDENT; checkout=null; days=1",
                () -> service.requestLoan(new Borrower(Role.STUDENT, true, 0, 0), null, 1));
    }

    @Test
    void dueDateOverflow() {
        CaseEvidence.invalid("LOAN-NEG-03", "FR-05", "checkout=LocalDate.MAX; days=1",
                () -> service.requestLoan(new Borrower(Role.STUDENT, true, 0, 0), LocalDate.MAX, 1));
    }

    @Test
    void validateBeforeEligibility() {
        CaseEvidence.invalid("LOAN-NEG-04", "FR-04 FR-08", "inactive STUDENT; checkout=" + CHECKOUT + "; days=8",
                () -> service.requestLoan(new Borrower(Role.STUDENT, false, 0, 0), CHECKOUT, 8));
    }

    @Test
    void rejectionReasonsAreImmutable() {
        LoanDecision decision = service.requestLoan(new Borrower(Role.STUDENT, false, 3, 1), CHECKOUT, 1);
        assertThrows(UnsupportedOperationException.class, () -> decision.rejectionReasons().clear());
        CaseEvidence.check("STATE-01", "FR-03 FR-08", "Negative testing",
                "attempt to clear all three returned rejection reasons", 3, decision.rejectionReasons().size());
    }

    @Test
    void repeatedCallsDoNotLeakStateOrIssueLoans() {
        Borrower blocked = new Borrower(Role.STAFF, false, 5, 100);
        Borrower eligible = new Borrower(Role.STUDENT, true, 2, 0);
        service.requestLoan(blocked, CHECKOUT, 1);
        LoanDecision first = service.requestLoan(eligible, CHECKOUT, 7);
        LoanDecision second = service.requestLoan(eligible, CHECKOUT, 7);
        assertEquals(List.of(), first.rejectionReasons());
        assertEquals(first.dueDate(), second.dueDate());
        CaseEvidence.check("STATE-02", "FR-08", "Regression testing",
                "blocked request followed by two eligible requests on the same service",
                "true;true;2", first.isApproved() + ";" + second.isApproved() + ";" + eligible.currentLoanCount());
    }
}
