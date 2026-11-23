package edu.campus.loan;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.function.Executable;

/** Test evidence is captured in Surefire XML, including genuine expected/actual values. */
final class CaseEvidence {
    private CaseEvidence() {
    }

    static void check(String id, String requirement, String technique, String input,
                      Object expected, Object actual) {
        System.out.printf("CASE\t%s\t%s\t%s\t%s\t%s\t%s%n", id, requirement, technique,
                clean(input), clean(expected), clean(actual));
        Assertions.assertEquals(expected, actual, id);
    }

    static void invalid(String id, String requirement, String input, Executable action) {
        String actual;
        try {
            action.execute();
            actual = "NO_EXCEPTION";
        } catch (Throwable error) {
            actual = error.getClass().getSimpleName();
        }
        check(id, requirement, "Negative testing", input, "IllegalArgumentException", actual);
    }

    private static String clean(Object value) {
        return String.valueOf(value).replace("\t", " ").replace("\n", " ").replace("\r", " ");
    }
}
