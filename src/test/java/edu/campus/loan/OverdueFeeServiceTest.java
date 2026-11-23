package edu.campus.loan;

import java.time.LocalDate;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class OverdueFeeServiceTest {
    private final OverdueFeeService service = new OverdueFeeService();
    private static final LocalDate CHECKOUT = LocalDate.of(2026, 11, 1);
    private static final LocalDate DUE = LocalDate.of(2026, 11, 8);

    @ParameterizedTest(name = "FEE-{0}: {1} days after due")
    @CsvSource({"01, -7, 0", "02, -1, 0", "03, 0, 0", "04, 1, 100", "05, 2, 200",
            "06, 49, 4900", "07, 50, 5000", "08, 51, 5000", "09, 100, 5000"})
    void feeBoundary(String suffix, int offset, long expected) {
        LocalDate returned = DUE.plusDays(offset);
        CaseEvidence.check("FEE-" + suffix, "FR-06", "Boundary value analysis",
                "checkout=" + CHECKOUT + "; due=" + DUE + "; return=" + returned,
                expected, service.calculateFeeCents(CHECKOUT, DUE, returned));
    }

    @ParameterizedTest(name = "FEE-DATE-{0}")
    @CsvSource({"01, 2024-02-20, 2024-02-28, 2024-03-01, 200",
            "02, 2026-02-20, 2026-02-28, 2026-03-01, 100",
            "03, 2026-12-25, 2026-12-31, 2027-01-01, 100",
            "04, 2026-01-25, 2026-01-31, 2026-02-02, 200",
            "05, 2026-11-23, 2026-11-30, 2026-11-29, 0"})
    void calendarFeeCases(String suffix, LocalDate checkout, LocalDate due, LocalDate returned, long expected) {
        CaseEvidence.check("FEE-DATE-" + suffix, "FR-06", "Equivalence partitioning",
                "checkout=" + checkout + "; due=" + due + "; return=" + returned,
                expected, service.calculateFeeCents(checkout, due, returned));
    }

    @ParameterizedTest(name = "FEE-NEG-{0}")
    @CsvSource({"01, NULL, 2026-11-08, 2026-11-09", "02, 2026-11-01, NULL, 2026-11-09",
            "03, 2026-11-01, 2026-11-08, NULL", "04, 2026-11-01, 2026-11-01, 2026-11-02",
            "05, 2026-11-01, 2026-10-31, 2026-11-02", "06, 2026-11-01, 2026-11-08, 2026-10-31"})
    void invalidDates(String suffix, String checkout, String due, String returned) {
        CaseEvidence.invalid("FEE-NEG-" + suffix, "FR-07",
                "checkout=" + checkout + "; due=" + due + "; return=" + returned,
                () -> service.calculateFeeCents(dateOrNull(checkout), dateOrNull(due), dateOrNull(returned)));
    }

    @Test
    void maximumCalendarSpanStillCapsSafely() {
        CaseEvidence.check("FEE-EXTREME-01", "FR-06", "Boundary value analysis",
                "checkout=LocalDate.MIN; due=MIN+1; return=LocalDate.MAX",
                5000L, service.calculateFeeCents(LocalDate.MIN, LocalDate.MIN.plusDays(1), LocalDate.MAX));
    }

    @Test
    void sameInstanceDoesNotCarryAnEarlierFee() {
        service.calculateFeeCents(CHECKOUT, DUE, DUE.plusDays(51));
        CaseEvidence.check("FEE-STATE-01", "FR-08", "Regression testing",
                "capped late return followed by an on-time return; checkout=" + CHECKOUT + "; due=" + DUE,
                0L, service.calculateFeeCents(CHECKOUT, DUE, DUE));
    }

    private static LocalDate dateOrNull(String value) {
        return "NULL".equals(value) ? null : LocalDate.parse(value);
    }
}
