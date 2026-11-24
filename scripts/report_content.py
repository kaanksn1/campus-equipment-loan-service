"""Seven-page report content assembled from preserved project evidence."""
import html
import textwrap


def code(source):
    return "<pre>" + html.escape(textwrap.dedent(source).strip()) + "</pre>"


def build_pages(root, summary, cases, faults, student, report_date, table, ratio):
    by_id = {row["id"]: row for row in cases}
    page1 = f"""
<p class="title"><b>Campus Equipment Loan Eligibility<br>and Overdue Fee Service</b></p>
<p class="meta">SWE411 Software Verification and Validation | Serdar Kaan Kesen | 220911810<br>
Dr. Osman Durmaz | {report_date}</p>
<h1>1. Introduction and Problem Definition</h1>
<p>A campus equipment desk needs consistent borrowing decisions, due dates and late-return fees.
This Java 17 console application evaluates an explicit borrower snapshot and return dates.
The educational rules are project assumptions. The scope excludes GUI, database, inventory,
payments and actual equipment issuance. A decision does not update a borrower's loan count.</p>
<p>Systematic tests check the specified behaviour; reviews, clear contracts and repeatable builds
also support quality assurance. Passing tests verify the implemented rules but do not validate
them as an actual university policy [1, 5].</p>
<h1>2. Requirements Specification</h1>
""" + table(["ID", "Required behaviour"], [
        ("FR-01", "Require STUDENT/STAFF role; reject missing role, negative loan count or negative debt."),
        ("FR-02", "Approve only with active membership, zero debt and count below 3 (student) or 5 (staff)."),
        ("FR-03", "Return all applicable rejection reasons; rejected decisions have no due date."),
        ("FR-04", "Requested days: student 1–7, staff 1–14 inclusive; otherwise input error."),
        ("FR-05", "Approved due date = checkout + requested calendar days; reject date overflow."),
        ("FR-06", "On-time/early fee = 0; late fee = 100 kurus/day, capped at 5,000 kurus per return."),
        ("FR-07", "Require checkout, due and return dates; due > checkout and return >= checkout."),
        ("FR-08", "Stateless evaluation; immutable borrower data and returned rejection reasons."),
        ("FR-09", "Console demo/help and loan/fee commands; malformed input produces exit code 2."),
    ], [15, 85]) + """
<p>A count at or above the limit and positive debt are valid inputs that cause normal rejection.
Negative values and out-of-range periods are invalid. Validate the complete request before evaluating
eligibility. One TL is 100 kurus; even one kurus of debt blocks approval. Dates include weekends
and leap days; no grace period or holiday adjustment applies.</p>
"""

    page2 = """
<h1>3. Implementation</h1>
<p>Role holds policy limits; Borrower validates an immutable snapshot; LoanDecision carries the
result and RejectionReason names the causes. LoanService and OverdueFeeService implement the
rules, while ConsoleApp handles parsing and output. Java 17, Maven, JUnit 5 and JaCoCo are configured
in the POM. Production code has no third-party runtime dependencies.</p>
<h2>Eligibility: LoanService.requestLoan excerpt</h2>
<p>Nulls, requested period and date overflow are validated before this block. The candidate date
is calculated with checkoutDate.plusDays(requestedDays). Separate checks preserve every reason.</p>
""" + code("""
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
        return new LoanDecision(
                reasons.isEmpty() ? candidateDueDate : null, reasons);
    """) + """
<h2>Fee: OverdueFeeService.calculateFeeCents excerpt</h2>
<p>Missing or inconsistent dates are rejected first. These lines then calculate lateness and apply
the cap. DAILY_FEE_CENTS is 100; MAXIMUM_FEE_CENTS is 5,000.</p>
""" + code("""
        long lateDays = ChronoUnit.DAYS.between(dueDate, returnDate);
        if (lateDays <= 0) {
            return 0;
        }
        return Math.min(lateDays * DAILY_FEE_CENTS, MAXIMUM_FEE_CENTS);
    """) + """
<p>Integer long values avoid fractional money arithmetic. LocalDate represents date-only values,
handles month/year and leap-day transitions, and avoids current-clock dependence [4]. The full
supported date span multiplied by 100 fits in long. Returned reasons use List.copyOf; a rejected
decision exposes an empty Optional for its due date.</p>
<p>Source excerpts are whitespace-formatted; the complete classes remain in src/main/java.
The console accepts integer kurus and ISO dates. Normal business rejection has exit code 0;
invalid input has exit code 2 and an error on stderr.</p>
"""

    page3 = """
<h1>4. Test Plan and Test Design</h1>
<p>Primary risks are incorrect approval, invalid input accepted as valid, calendar mistakes and
overcharging. Expected values come from requirements and literal examples. Unit tests target
services; component tests target console parsing/output; separate JAR checks cover process behaviour.</p>
""" + table(["Technique", "Application and selection rationale"], [
        ("Equivalence partitioning", "Debt: negative/zero/positive; count: below/at/above limit; return: early/on-time/late. Representatives exercise distinct behaviours."),
        ("Boundary value analysis", "Check neighbours of count, period, first late day and fee cap; these expose incorrect comparisons and off-by-one calculations."),
        ("Decision table", "All eight combinations of active membership, zero debt and available capacity; execute for both roles (16 cases)."),
        ("Negative testing", "Nulls, negative values, invalid periods, date ordering/overflow and malformed console tokens must be rejected deliberately."),
        ("Regression testing", "Rerun existing tests after each controlled fault is repaired and rerun the complete original suite after all experiments."),
    ], [27, 73]) + """
<h2>Selected boundary values</h2>
""" + table(["Input", "Values", "Expected distinction"], [
        ("Student / staff count", "2, 3, 4 / 4, 5, 6", "Below limit permits; at/above blocks."),
        ("Debt (kurus)", "-1, 0, 1", "Invalid / debt-free / blocked."),
        ("Student / staff days", "0, 1, 6, 7, 8 / 0, 1, 13, 14, 15", "Inclusive period ends and outside."),
        ("Days late", "-1, 0, 1; 49, 50, 51", "0, 0, 100; 4,900, 5,000, 5,000 kurus."),
    ], [26, 35, 39]) + """
<h2>Decision table</h2>
<p>A = active, Z = zero debt, C = capacity available. Other inputs are valid.</p>
""" + table(["A", "Z", "C", "Result / rejection reasons"], [
        ("T", "T", "T", "Approve; reasons empty; due date present."),
        ("T", "T", "F", "Reject: loan limit."),
        ("T", "F", "T", "Reject: debt."),
        ("T", "F", "F", "Reject: debt and loan limit."),
        ("F", "T", "T", "Reject: inactive membership."),
        ("F", "T", "F", "Reject: inactive membership and loan limit."),
        ("F", "F", "T", "Reject: inactive membership and debt."),
        ("F", "F", "F", "Reject: all three reasons."),
    ], [9, 9, 9, 73]) + """
<p>The table exhausts the Boolean eligibility model, not every date or integer. Calendar, representation
limits and state-isolation tests complement it. Invalid periods must raise an error even for an inactive borrower.</p>
"""

    page4 = """
<h1>5. Test Implementation and Results</h1>
<p>JUnit 5 @ParameterizedTest with @CsvSource/@MethodSource expresses related examples;
@Test covers distinct cases. Fresh fixtures and explicit dates make tests repeatable [1].
CaseEvidence records inputs, expected/actual values and requirement IDs, then calls assertEquals.
JUnit also checks complete reason lists, absent due dates, immutability and exception behaviour.</p>
<h2>Executed boundary test: OverdueFeeServiceTest</h2>
<p>Fields omitted below: CHECKOUT = 2026-11-01 and DUE = 2026-11-08. Each row is a separate execution.</p>
""" + code('''
        @ParameterizedTest(name = "FEE-{0}: {1} days after due")
        @CsvSource({"01, -7, 0", "02, -1, 0", "03, 0, 0",
                "04, 1, 100", "05, 2, 200", "06, 49, 4900",
                "07, 50, 5000", "08, 51, 5000", "09, 100, 5000"})
        void feeBoundary(String suffix, int offset, long expected) {
            LocalDate returned = DUE.plusDays(offset);
            CaseEvidence.check("FEE-" + suffix, "FR-06",
                    "Boundary value analysis",
                    "checkout=" + CHECKOUT + "; due=" + DUE
                            + "; return=" + returned,
                    expected,
                    service.calculateFeeCents(CHECKOUT, DUE, returned));
        }
    ''') + """
<h2>Executed state-isolation test</h2>
""" + code('''
        @Test
        void sameInstanceDoesNotCarryAnEarlierFee() {
            service.calculateFeeCents(CHECKOUT, DUE, DUE.plusDays(51));
            CaseEvidence.check("FEE-STATE-01", "FR-08",
                    "Regression testing",
                    "capped late return followed by an on-time return; "
                            + "checkout=" + CHECKOUT + "; due=" + DUE,
                    0L, service.calculateFeeCents(CHECKOUT, DUE, DUE));
        }
    ''') + table(["Test class", "Executions", "Failures / errors / skipped"], [
        (row["name"].rsplit(".", 1)[-1], row["tests"],
         f"{row['failures']} / {row['errors']} / {row['skipped']}")
        for row in summary["classes"]
    ], [48, 18, 34]) + f"""
<p><b>Total: {summary['tests']} passed.</b> No failures, errors or skipped cases in the correct version.
All cases have unique IDs and preserved Surefire results; the next page shows representative observations.</p>
"""

    selected = [
        ("CAP-03", "Student count = 3", "false", "false"),
        ("DEBT-02", "Debt = 1 kurus", "false", "false"),
        ("PERIOD-04", "2026-11-23 + 7 days", "2026-11-30", "2026-11-30"),
        ("DATE-03", "2024-02-28 + 1 day", "2024-02-29", "2024-02-29"),
        ("FEE-03", "Return on due date", "0 kurus", "0 kurus"),
        ("FEE-08", "51 days late", "5,000 kurus", "5,000 kurus"),
        ("FEE-NEG-06", "Return before checkout", "Input error", "Input error"),
    ]
    for case_id, *_ in selected:
        if by_id[case_id]["status"] != "PASS":
            raise ValueError("Representative case is not passing: " + case_id)
    page5 = """
<h2>5. Test Implementation and Results (continued)</h2>
<h2>Representative executed cases</h2>
""" + table(["Case", "Input summary", "Expected", "Actual"], selected, [19, 35, 23, 23]) + """
<p>The invalid-date example expects IllegalArgumentException, so its successful rejection is a passing
negative test. Literal dates and amounts form independent oracles. Full inputs and actual observations
for all 103 cases remain in evidence/test-cases.html and JSON; extra assertions are reflected in JUnit results.</p>
<h2>Student build and manual console checks</h2>
""" + f"""
<p>I ran the full build, which finished at {html.escape(student['build_finished_at'])}, then ran
the demo and two explicit scenarios. Terminal output was saved with tee.</p>
""" + code("""
        ./scripts/build.sh clean verify
        Tests run: 103, Failures: 0, Errors: 0, Skipped: 0
        BUILD SUCCESS
    """) + table(["Manual check", "Expected and observed outcome", "Result"], [
        (row["id"].removeprefix("STUDENT-"), row["summary"], "PASS" if row["passed"] else "FAIL")
        for row in student["manual_console_checks"]
    ], [20, 67, 13]) + code("""
        ./scripts/run.sh loan STUDENT true 3 0 2026-11-24 7
        REJECTED; reasons: [LOAN_LIMIT_REACHED]
        ./scripts/run.sh fee 2026-11-24 2026-12-01 2026-12-04
        Overdue fee: 3.00 TL (300 kurus)
    """) + """
<p>The student execution record contains four raw terminal logs, commands, complete expected/actual
outputs and checksums (evidence/student-run.json). These three manual checks are separate from the
103 JUnit executions. Eight automated packaged-JAR checks also passed, verifying stdout/stderr and
exit codes for approval, rejection, fees, invalid input and the demo.</p>
<p>Build command: ./scripts/build.sh clean verify. Test and coverage outputs are generated under
target/surefire-reports and target/site/jacoco. The public repository contains the complete source,
configuration and preserved evidence:<br>
<a href="https://github.com/kaanksn1/campus-equipment-loan-service">github.com/kaanksn1/campus-equipment-loan-service</a>.</p>
"""

    metrics = [("All production code", ratio(summary["coverage"]["LINE"]),
                ratio(summary["coverage"]["BRANCH"]))]
    for row in summary["production_classes"]:
        metrics.append((row["name"].rsplit("/", 1)[-1], ratio(row["counters"]["LINE"]),
                        ratio(row["counters"].get("BRANCH", {"covered": 0, "missed": 0}))))
    fault_rows = []
    for fault in faults:
        example = fault["failing_cases"][0]
        fault_rows.append((fault["id"], fault["title"],
                           str(fault["results"]["failures"]) + "/9",
                           example["expected"] + " / " + example["actual"]))
    page6 = """
<h1>6. Code Coverage and Defect Analysis</h1>
<p>JaCoCo measures all seven production types; no console or validation classes are excluded.
Instruction coverage is """ + ratio(summary["coverage"]["INSTRUCTION"]) + ".</p>" + table(
        ["Class", "Line coverage", "Branch coverage"], metrics, [38, 31, 31]) + """
<p>Both business services have 100% line/branch coverage. Missed overall lines and branches belong
to console entry/dispatch paths. Separate JVM smoke runs exercise the entry point but are not attached
to the JUnit JaCoCo agent. Exception handling is not counted as JaCoCo branches [2, 3].</p>
<h2>Controlled faults and real unsuccessful executions</h2>
<p>Each fault was deliberately seeded in a temporary copy. Existing expected values were unchanged;
these are controlled experiments, not claims about accidental student mistakes.</p>
""" + table(["Fault", "Change", "Failed", "Expected / faulty actual example"], fault_rows,
             [13, 34, 12, 41]) + """
<p>FI-01 uses > instead of >=, admitting a borrower at the limit. FI-02 adds one late day, charging
an on-time return. FI-03 removes the 5,000-kurus cap. The experiments produced 2, 4 and 2 genuine
assertion failures, respectively, with no test errors. After restoring each copy, all nine targeted
tests passed. The complete original suite also passed all 103 cases after the experiments.</p>
<p>Exact diffs, failing and repaired results, and logs are preserved under evidence/fault-injection.
Source checksums verify that the original Java files and POM were unchanged by the experiments.</p>
<h2>What coverage does and does not establish</h2>
<p>Execution coverage cannot prove correct requirements or assertions. A test must reach a fault,
produce an incorrect state, propagate it to an observable result and reveal it with a check (RIPR) [5].
The boundary tests reveal these selected faults; three experiments do not constitute comprehensive
mutation testing. High coverage therefore supports, rather than replaces, meaningful expected results.</p>
"""

    page7 = """
<h1>7. Discussion and Conclusion</h1>
<p>Decision tables cover combined eligibility conditions; boundaries expose comparison and fee-cap
mistakes; invalid-input tests enforce contracts; regression checks expose unintended changes.
JUnit makes these checks repeatable after edits and gives each concrete case an identifiable result [1].
The controlled failures show that assertions detect selected faults beyond merely executing code.</p>
<p>Implementation challenges included selecting Java 17 when the original machine used Java 8,
distinguishing invalid input from normal rejection, and consistent date/money semantics. Explicit dates,
integer kurus and a Maven Wrapper made the build and tests repeatable. Parameterized tests reduced
duplication while keeping separate records for each example.</p>
<h2>Personal contribution and reflection</h2>
<p>I selected the equipment-loan topic and small console scope, provided the proposal and emailed
the instructor to request approval. In the examples, I identified that a borrower already at the
loan limit must be rejected, while a negative debt value is invalid input. I checked that three late
days cost 300 kurus and that a longer delay cannot raise the fee above 50 TL. I ran the full build
and all 103 tests passed, then compared the demo and two console scenarios with their expected
outputs. These runs confirmed the rejection at three student loans and the 300-kurus fee for a
three-day delay; their terminal logs are preserved. ChatGPT explanations helped me study Java,
JUnit, test design and the difference between an expected result and the program's actual output.</p>
<p>The service trusts supplied snapshots and has no persistence or concurrent inventory control.
The policy has not been validated with an operating equipment desk; tests do not exhaust every date
or integer. Within scope, broader fault selection and additional calendar combinations could improve
the evidence. The tested rules pass the suite, with limits stated above.</p>
<p class="small"><b>Assistance:</b> OpenAI Codex supported implementation, test design, execution,
analysis and report preparation. ChatGPT supported concept study. External technical sources are cited below.</p>
<h1>8. References</h1>
<p class="small"><b>[1]</b> JUnit Team. <i>JUnit 5 User Guide, 5.13.4.</i> Assertions, fixtures and parameterized tests.<br>
<a href="https://docs.junit.org/5.13.4/user-guide/">https://docs.junit.org/5.13.4/user-guide/</a></p>
<p class="small"><b>[2]</b> JaCoCo. <i>Maven Plug-in.</i> Build pins 0.8.14; online trunk may differ.<br>
<a href="https://www.jacoco.org/jacoco/trunk/doc/maven.html">https://www.jacoco.org/jacoco/trunk/doc/maven.html</a></p>
<p class="small"><b>[3]</b> JaCoCo. <i>Coverage Counters.</i> Line/branch definitions and limitations.<br>
<a href="https://www.jacoco.org/jacoco/trunk/doc/counters.html">https://www.jacoco.org/jacoco/trunk/doc/counters.html</a></p>
<p class="small"><b>[4]</b> Oracle. <i>Java SE 17 API: LocalDate.</i><br>
<a href="https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/time/LocalDate.html">Java SE 17 LocalDate API documentation</a></p>
<p class="small"><b>[5]</b> O. Durmaz. <i>SWE411 lecture slides l0–l4 and SVV Research Assignment.</i>
Supplied course materials. Technical references consulted 23 November 2026.</p>
"""
    return [page1, page2, page3, page4, page5, page6, page7]
