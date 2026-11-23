package edu.campus.loan;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import static org.junit.jupiter.api.Assertions.*;

class ConsoleAppTest {
    @ParameterizedTest(name = "CLI-{0}")
    @CsvSource(delimiter = '|', value = {
            "01 | loan STUDENT true 2 0 2026-11-23 7 | APPROVED; due date: 2026-11-30",
            "02 | loan staff FALSE 5 1 2026-11-23 14 | REJECTED; reasons: [INACTIVE_MEMBERSHIP, OUTSTANDING_FEES, LOAN_LIMIT_REACHED]",
            "03 | fee 2026-11-23 2026-11-30 2026-12-03 | Overdue fee: 3.00 TL (300 kurus)",
            "04 | fee 2026-11-23 2026-11-30 2026-11-30 | Overdue fee: 0.00 TL (0 kurus)",
            "05 | fee 2026-11-23 2026-11-30 2027-03-01 | Overdue fee: 50.00 TL (5000 kurus)"
    })
    void validCommands(String suffix, String command, String expected) {
        Result result = execute(command);
        assertEquals(0, result.status());
        assertEquals("", result.error());
        CaseEvidence.check("CLI-" + suffix, "FR-09", "Equivalence partitioning",
                command, expected, result.output().strip());
    }

    @ParameterizedTest(name = "CLI-NEG-{0}")
    @CsvSource(delimiter = '|', value = {
            "01 | loan VISITOR true 0 0 2026-11-23 1",
            "02 | loan STUDENT maybe 0 0 2026-11-23 1",
            "03 | loan STUDENT true -1 0 2026-11-23 1",
            "04 | loan STUDENT true 0 -1 2026-11-23 1",
            "05 | loan STUDENT true 0 0 2026-02-30 1",
            "06 | loan STUDENT true 0 0 2026-11-23 8",
            "07 | loan STUDENT true 0 0.5 2026-11-23 1",
            "08 | loan STUDENT true 2147483648 0 2026-11-23 1",
            "09 | loan STUDENT true 0 9223372036854775808 2026-11-23 1",
            "10 | fee 2026-11-23 2026-11-30 2026-11-22",
            "11 | fee 2026-11-23 2026-11-30",
            "12 | unknown",
            "13 | loan STUDENT true 0 0 23/11/2026 1",
            "14 | loan STUDENT true 0 0 2026-11-23 word"
    })
    void invalidCommands(String suffix, String command) {
        Result result = execute(command);
        assertEquals("", result.output());
        assertTrue(result.error().startsWith("Input error:"));
        assertTrue(result.error().contains("Usage:"));
        CaseEvidence.check("CLI-NEG-" + suffix, "FR-09", "Negative testing", command, 2, result.status());
    }

    @Test
    void helpAndEmptyArguments() {
        Result empty = execute("");
        Result help = execute("--help");
        assertEquals(empty.output(), help.output());
        assertTrue(help.output().contains("integer kurus"));
        CaseEvidence.check("CLI-HELP-01", "FR-09", "Equivalence partitioning",
                "empty arguments; --help", "0;0", empty.status() + ";" + help.status());
    }

    @Test
    void deterministicDemo() {
        Result result = execute("--demo");
        assertTrue(result.output().contains("APPROVED; due date: 2026-11-30"));
        assertTrue(result.output().contains("REJECTED; reasons: [INACTIVE_MEMBERSHIP, OUTSTANDING_FEES, LOAN_LIMIT_REACHED]"));
        assertTrue(result.output().contains("Three days late: 3.00 TL"));
        CaseEvidence.check("CLI-DEMO-01", "FR-09", "Regression testing", "--demo", 0, result.status());
    }

    private static Result execute(String command) {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        ByteArrayOutputStream err = new ByteArrayOutputStream();
        int status = ConsoleApp.run(command.isEmpty() ? new String[0] : command.split(" "),
                new PrintStream(out, true, StandardCharsets.UTF_8),
                new PrintStream(err, true, StandardCharsets.UTF_8));
        return new Result(status, out.toString(StandardCharsets.UTF_8), err.toString(StandardCharsets.UTF_8));
    }

    private record Result(int status, String output, String error) {
    }
}
