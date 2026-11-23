package edu.campus.loan;

import java.io.PrintStream;
import java.time.DateTimeException;
import java.time.LocalDate;
import java.util.Locale;

/** A command-line entry point; service inputs remain explicit and reproducible. */
public final class ConsoleApp {
    private ConsoleApp() {
    }

    public static void main(String[] args) {
        int status = run(args, System.out, System.err);
        if (status != 0) {
            System.exit(status);
        }
    }

    public static int run(String[] args, PrintStream out, PrintStream err) {
        try {
            if (args.length == 0 || (args.length == 1 && "--help".equals(args[0]))) {
                usage(out);
            } else if (args.length == 1 && "--demo".equals(args[0])) {
                demonstrate(out);
            } else if (args.length == 7 && "loan".equals(args[0])) {
                Borrower borrower = new Borrower(Role.valueOf(args[1].toUpperCase(Locale.ROOT)),
                        parseMembership(args[2]), Integer.parseInt(args[3]), Long.parseLong(args[4]));
                printDecision(new LoanService().requestLoan(borrower,
                        LocalDate.parse(args[5]), Integer.parseInt(args[6])), out);
            } else if (args.length == 4 && "fee".equals(args[0])) {
                long fee = new OverdueFeeService().calculateFeeCents(LocalDate.parse(args[1]),
                        LocalDate.parse(args[2]), LocalDate.parse(args[3]));
                out.println("Overdue fee: " + formatMoney(fee) + " TL (" + fee + " kurus)");
            } else {
                throw new IllegalArgumentException("Unknown command or incorrect argument count.");
            }
            return 0;
        } catch (IllegalArgumentException | DateTimeException ex) {
            err.println("Input error: " + ex.getMessage());
            usage(err);
            return 2;
        }
    }

    private static boolean parseMembership(String value) {
        if ("true".equalsIgnoreCase(value)) {
            return true;
        }
        if ("false".equalsIgnoreCase(value)) {
            return false;
        }
        throw new IllegalArgumentException("Membership must be true or false.");
    }

    private static void printDecision(LoanDecision decision, PrintStream out) {
        if (decision.isApproved()) {
            out.println("APPROVED; due date: " + decision.dueDate().orElseThrow());
        } else {
            out.println("REJECTED; reasons: " + decision.rejectionReasons());
        }
    }

    private static String formatMoney(long cents) {
        return String.format(Locale.ROOT, "%d.%02d", cents / 100, cents % 100);
    }

    private static void demonstrate(PrintStream out) {
        out.println("Campus Equipment Loan Eligibility and Overdue Fee Service");
        out.println("Educational policy; no equipment is reserved or issued.");
        LoanService loans = new LoanService();
        LocalDate checkout = LocalDate.of(2026, 11, 23);
        printDecision(loans.requestLoan(new Borrower(Role.STUDENT, true, 2, 0), checkout, 7), out);
        printDecision(loans.requestLoan(new Borrower(Role.STAFF, false, 5, 1), checkout, 14), out);
        long fee = new OverdueFeeService().calculateFeeCents(checkout,
                LocalDate.of(2026, 11, 30), LocalDate.of(2026, 12, 3));
        out.println("Three days late: " + formatMoney(fee) + " TL");
    }

    private static void usage(PrintStream out) {
        out.println("Usage: java -jar target/campus-equipment-loan.jar --demo");
        out.println("       java -jar target/campus-equipment-loan.jar loan <STUDENT|STAFF>"
                + " <true|false> <currentLoans> <outstandingKurus> <YYYY-MM-DD> <days>");
        out.println("       java -jar target/campus-equipment-loan.jar fee"
                + " <checkoutDate> <dueDate> <returnDate>");
        out.println("Dates are ISO calendar dates; money inputs are integer kurus (100 = 1 TL).");
    }
}
