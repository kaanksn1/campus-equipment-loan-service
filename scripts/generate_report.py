#!/usr/bin/env python3
"""Build the eight-section report from evidence using ReportLab and PyMuPDF."""
from pathlib import Path
from datetime import datetime
import html
import json
import re
from html.parser import HTMLParser
import pymupdf as fitz
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Table, TableStyle, Spacer, Preformatted, KeepTogether, PageBreak

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission"
SUMMARY = json.loads((ROOT / "evidence/summary.json").read_text())
REPORT_DATE = datetime.fromisoformat(SUMMARY["run_time_oslo"]).strftime("%d %B %Y")
CASES = json.loads((ROOT / "evidence/test-cases.json").read_text())
FAULTS = json.loads((ROOT / "evidence/fault-injection/summary.json").read_text())
BY_ID = {row["id"]: row for row in CASES}

CSS = """
body { font-family: sans-serif; font-size: 11pt; line-height: 1.10; color: #182430;
       max-width: 840px; margin: 32px auto; padding: 0 24px; }
p { margin-top: 0; margin-bottom: 6pt; }
h1 { font-size: 16pt; color: #2e74b5; margin-top: 16pt; margin-bottom: 8pt; }
h2 { font-size: 13pt; color: #2e74b5; margin-top: 12pt; margin-bottom: 6pt; }
h3 { font-size: 12pt; color: #1f4d78; margin-top: 8pt; margin-bottom: 4pt; }
.title { font-size: 22pt; color: #0b2545; line-height: 1.08; margin-bottom: 9pt; }
.subtitle { font-size: 12pt; color: #526273; margin-bottom: 10pt; }
.meta { font-size: 10pt; color: #526273; margin-bottom: 4pt; }
.lead { background-color: #f4f6f9; padding: 9pt; margin-top: 10pt; margin-bottom: 12pt; }
table { width: 100%; border-collapse: collapse; font-size: 9.5pt; margin-top: 6pt; margin-bottom: 10pt; }
th, td { border: 0.5pt solid #cbd3df; padding: 5pt; vertical-align: middle; text-align: left; }
th { background-color: #f2f4f7; font-weight: bold; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
pre { font-family: monospace; font-size: 8.6pt; line-height: 1.18; background-color: #f4f6f9; padding: 7pt; }
code { font-family: monospace; font-size: 9pt; }
ul, ol { margin-top: 2pt; margin-bottom: 8pt; padding-left: 20pt; }
li { margin-bottom: 4pt; }
a { color: #1f4d78; text-decoration: none; }
.small { font-size: 9.5pt; color: #526273; }
"""


def table(headers, rows, widths=None):
    cols = ""
    if widths:
        cols = "<colgroup>" + "".join('<col style="width:' + str(w) + '%">' for w in widths) + "</colgroup>"
    head = "<thead><tr>" + "".join("<th>" + html.escape(str(h)) + "</th>" for h in headers) + "</tr></thead>"
    body = "<tbody>" + "".join("<tr>" + "".join("<td>" + html.escape(str(c)) + "</td>" for c in r) + "</tr>" for r in rows) + "</tbody>"
    return "<table>" + cols + head + body + "</table>"


def counter_ratio(counter):
    covered = counter["covered"]
    total = covered + counter["missed"]
    return f"{covered}/{total} ({100 * covered / total:.2f}%)" if total else "Not applicable"


def build_sections():
    s = SUMMARY
    intro = f"""
<p class="title"><b>Campus Equipment Loan Eligibility<br>and Overdue Fee Service</b></p>
<p class="subtitle">SWE411 Software Verification and Validation<br>Implementation and automated testing report</p>
<p class="meta"><b>Student:</b> Serdar Kaan Kesen &nbsp; | &nbsp; <b>Number:</b> 220911810</p>
<p class="meta"><b>Instructor:</b> Dr. Osman Durmaz &nbsp; | &nbsp; <b>Date:</b> {REPORT_DATE}</p>
<p class="meta"><b>Status:</b> AI-assisted report</p>
<p class="lead"><b>Measured result:</b> {s['tests']} JUnit 5 executions passed, with no failures, errors or skipped tests.
All {s['console_smoke_tests']} packaged-console checks passed. Three deliberately seeded faults were detected.
Overall line coverage is {s['coverage']['LINE']['percent']:.2f}% and branch coverage is {s['coverage']['BRANCH']['percent']:.2f}%.</p>
<h1>1. Introduction and Problem Definition</h1>
<p>A campus equipment desk needs a consistent way to assess whether a borrower can receive a new loan,
set its due date and calculate the fee when equipment is returned late. Manual evaluation can confuse
student and staff limits, overlook a small debt or charge an additional day on an on-time return.
The proposed solution is a small Java console service with explicit inputs and testable rules.</p>
<p>The educational policy allows students up to three active loans and staff up to five. Approval also
requires active membership and zero outstanding debt. The requested period is role-dependent, and a
late return incurs a daily fee with a per-return ceiling. These rules offer Boolean combinations,
numeric boundaries and invalid-input classes suitable for systematic testing.</p>
<p>The scope follows the supplied proposal: no GUI, database, authentication, inventory reservation or
payment processing. Evaluation does not actually issue equipment or update stored borrower data.
Policy values are project assumptions, not claims about a real university. Development proceeded
provisionally at the student's request while instructor topic approval remained unconfirmed.</p>
<h2>Testing within quality assurance</h2>
<p>Testing provides repeatable evidence that implemented behaviour agrees with specified requirements.
It supports quality control by exposing failures; clear requirements, reviews and reproducible builds
also support the broader quality-assurance process. Verification of these rules is distinct from
validation with a real equipment desk: passing the suite cannot establish that the educational
policy satisfies actual campus needs. The lecture material emphasises early detection, traceable
tests and the limitations of testing as a proof of correctness [6].</p>
"""

    requirements = """
<h1>2. Requirements Specification</h1>
<p>The proposal is the policy baseline [8]. The full specification is in <code>docs/requirements.md</code>.
The following identifiers are used in the executable case records.</p>
""" + table(["ID", "Required behaviour"], [
        ("FR-01", "Validate borrower role, nonnegative current loan count and nonnegative integer-kurus debt."),
        ("FR-02", "Approve only when membership is active, debt equals zero and current loans are below the role limit."),
        ("FR-03", "Return all rejection reasons; an approved result has none, and a rejected result has no due date."),
        ("FR-04", "Accept 1–7 requested calendar days for students or 1–14 for staff, inclusive."),
        ("FR-05", "Require checkout date; approved due date = checkout + requested days; reject calendar overflow."),
        ("FR-06", "Charge zero on/before due date, otherwise 100 kurus per late day, capped at 5,000 kurus."),
        ("FR-07", "Require all return-related dates; due must follow checkout and return cannot precede checkout."),
        ("FR-08", "Keep evaluation stateless and borrower snapshots and returned reasons immutable."),
        ("FR-09", "Provide console demo, loan/fee commands, help, readable results and controlled input-error handling."),
    ], [15, 85]) + """
<h2>Policy values and input interpretation</h2>
""" + table(["Policy", "Student", "Staff"], [
        ("Active-loan limit", "3", "5"), ("Requested days", "1–7", "1–14"),
        ("Eligibility", "Active; zero debt; below limit", "Active; zero debt; below limit"),
        ("Late-return fee", "100 kurus/day; cap 5,000", "100 kurus/day; cap 5,000"),
    ], [34, 33, 33]) + """
<p>One TL equals 100 kurus. A debt of one kurus blocks approval; a negative amount is invalid rather
than a normal rejection. Counts at or above a limit are valid data that produce a rejection.
Role and membership inputs are case-insensitive in the console; membership tokens must be true or false.</p>
<p>The proposal's requirement to reject inconsistent return dates is made precise: due date must be
strictly after checkout, and return may occur on checkout day or later. This permits early return and
agrees with the minimum one-day loan period. The whole request is validated before eligibility,
including when the borrower is already inactive.</p>
<p>Dates are explicit ISO calendar dates; weekends and leap days count. There is no grace period,
holiday adjustment, renewal or fee waiver. There is no dependence on today's clock or a time zone.
Java 17, JUnit 5, Maven and JaCoCo fulfil the technical approach. The assignment specifies neither a
minimum test count nor a mandatory coverage percentage [7].</p>
"""

    implementation = """
<h1>3. Implementation</h1>
<p>The application separates console parsing from deterministic business services. The only production
dependency is the Java runtime. Maven defines Java release 17 and pins dependency/plugin versions.</p>
""" + table(["Type", "Responsibility"], [
        ("Role", "Holds the student/staff loan-count and maximum-period policy."),
        ("Borrower", "An immutable Java record; validates role, count and debt in its constructor."),
        ("LoanService", "Validates a request, calculates a candidate due date and collects every eligibility rejection."),
        ("RejectionReason", "Names inactive membership, outstanding fees and reached loan limit."),
        ("LoanDecision", "Exposes approval, immutable reasons and an optional due date."),
        ("OverdueFeeService", "Validates dates and calculates the capped fee from late calendar days."),
        ("ConsoleApp", "Implements help, demo, loan/fee commands, formatting and input errors."),
    ], [30, 70]) + """
<h2>Key design choices</h2>
<p>The loan service validates missing data and the role-specific period first. It then uses
<code>checkoutDate.plusDays(requestedDays)</code>, translating date-range overflow into an input error.
Three independent checks collect all applicable rejection reasons instead of returning after the first.
Only an approved decision exposes the calculated due date.</p>
<p>Money is represented as <code>long</code> integer kurus, avoiding fractional binary arithmetic in
debt comparisons and fee totals. Fee calculation uses the calendar-day difference between due and
return. Nonpositive differences cost zero; positive differences are multiplied by 100 and limited
to 5,000. Even the full supported date span multiplied by 100 fits within a long.</p>
<p><code>LocalDate</code> represents an immutable date without a time or time zone [4]. Its calendar
arithmetic handles month and year transitions and leap years. Explicit dates also make tests stable
across machines and days. The service has no mutable fields and does not change counts or accumulate debt.</p>
<h2>Console and reproducible build</h2>
<pre>./scripts/build.sh clean verify
./scripts/run.sh loan STUDENT true 2 0 2026-11-23 7
./scripts/run.sh fee 2026-11-23 2026-11-30 2026-12-03</pre>
<p>A business rejection returns exit code 0 because evaluation succeeded. Invalid input returns code 2
and prints an error and usage to stderr. Amounts are formatted in TL with two decimal places.</p>
<p>The measured environment was macOS ARM64, Eclipse Adoptium Java 17.0.21.1, Maven 3.9.11 [5],
JUnit Jupiter 5.13.4, Surefire 3.5.4 and JaCoCo 0.8.14. Maven Wrapper scripts support repeatable builds.
The machine's original default Java was version 8; the helper scripts select the separately cached JDK 17
without changing permanent system settings. Details are preserved in <code>evidence/environment.txt</code>.</p>
"""

    plan = """
<h1>4. Test Plan and Test Design</h1>
<p>The highest-priority risks are approving a blocked borrower, rejecting an eligible borrower and
charging the wrong fee. Tests derive expected values from the requirements, not from production
helper methods. Business logic is tested directly; console parsing/output is tested as a component;
the packaged executable receives separate process-level smoke checks.</p>
<h2>Equivalence partitioning</h2>
""" + table(["Input", "Selected partitions", "Examples"], [
        ("Role", "Student, staff; missing/unknown", "DT rows; MODEL-05; CLI-NEG-01"),
        ("Loan count", "Below, at and above limit; negative", "CAP-01–09; MODEL-01–02"),
        ("Debt", "Zero, positive; negative or malformed", "DEBT-01–04; MODEL-03–04"),
        ("Period", "Within role range; outside or malformed", "PERIOD-01–12; CLI-NEG-14"),
        ("Return date", "Early, on-time, late; missing/inconsistent", "FEE-01–09; FEE-NEG-01–06"),
    ], [20, 43, 37]) + """
<p>These classes distinguish invalid input from valid rejection. Zero debt and positive debt cannot
be treated as one class; otherwise the one-kurus blocking rule could remain untested. Early return is
valid and must not be confused with a return before checkout.</p>
<h2>Boundary value analysis</h2>
""" + table(["Boundary", "Values", "Required distinction"], [
        ("Student count", "2, 3, 4", "Only 2 leaves capacity."),
        ("Staff count", "4, 5, 6", "Only 4 leaves capacity."),
        ("Debt, in kurus", "-1, 0, 1", "Invalid; eligible on debt; blocked."),
        ("Student days", "0, 1, 6, 7, 8", "Both inclusive ends and outside."),
        ("Staff days", "0, 1, 13, 14, 15", "Both inclusive ends and outside."),
        ("Late days", "-1, 0, 1", "Free early/on time; first charge."),
        ("Cap, late days", "49, 50, 51", "4,900; 5,000; 5,000 kurus."),
    ], [28, 26, 46]) + """
<p>Additional calendar cases cross month/year boundaries and leap/non-leap February. Numeric extremes
and date-range endpoints test representation and overflow handling. Ordinary examples ensure boundary
tests are supplemented by representative valid behaviour.</p>
<h2>Eight-rule decision table</h2>
<p>A = active membership, Z = zero debt, C = current count below the role limit. Other inputs are valid.
The complete Boolean model has eight rules. Each is executed once for each role, producing 16 cases.</p>
""" + table(["Rule", "A", "Z", "C", "Expected decision"], [
        ("1", "T", "T", "T", "Approve; due date present; no reasons"),
        ("2", "T", "T", "F", "Reject: loan limit"),
        ("3", "T", "F", "T", "Reject: outstanding debt"),
        ("4", "T", "F", "F", "Reject: debt and loan limit"),
        ("5", "F", "T", "T", "Reject: inactive membership"),
        ("6", "F", "T", "F", "Reject: inactive and loan limit"),
        ("7", "F", "F", "T", "Reject: inactive and debt"),
        ("8", "F", "F", "F", "Reject: all three reasons"),
    ], [12, 9, 9, 9, 61]) + """
<p>Every rejected result must have no due date. Checking the complete reason list catches an
implementation that stops after the first failure. Exhausting this small Boolean model does not
exhaust all numeric and calendar inputs.</p>
<h2>Negative testing and regression</h2>
<p>Negative tests cover null roles/borrowers/dates, negative numbers, invalid periods, impossible dates,
unsupported console tokens and numeric overflow. State tests attempt to mutate returned reasons and
make unrelated successive calls. After each controlled fault experiment, the unmodified project is
available for regression; after all experiments, the entire original suite is rerun and its results
are preserved separately. The full design is in <code>docs/test-plan.md</code>.</p>
"""

    class_rows = [(row["name"].rsplit(".", 1)[-1], row["tests"], row["failures"], row["errors"], row["skipped"])
                  for row in s["classes"]]
    representative = []
    short_inputs = {
        "CAP-03": "Student; active; zero debt; count 3",
        "DEBT-02": "Student; active; count 0; debt 1 kurus",
        "PERIOD-04": "Student; checkout 2026-11-23; 7 days",
        "DATE-03": "Checkout 2024-02-28; 1 day",
        "FEE-03": "Return exactly on due date",
        "FEE-08": "Return 51 days after due date",
        "FEE-NEG-06": "Return before checkout",
    }
    for key, short in short_inputs.items():
        row = BY_ID[key]
        representative.append((key, short, row["expected"], row["actual"], row["status"]))
    results = f"""
<h1>5. Test Implementation and Results</h1>
<p>JUnit 5 provides the test runner and assertion framework. Ordinary tests handle distinct behaviours;
parameterized tests express related examples through CsvSource and MethodSource. Assertions compare
actual values with explicit expected values; exception assertions also check immutability. Fresh test
instances keep fixtures independent [1]. JUnit is test-scoped and is not shipped as an application dependency.</p>
<p>Evidence from the final passing Maven verify run was collected at {html.escape(s['run_time_oslo'])}. It contains {s['tests']} cases:
{s['tests'] - s['failures'] - s['errors'] - s['skipped']} passed, {s['failures']} failed,
{s['errors']} errored and {s['skipped']} were skipped.</p>
""" + table(["Test class", "Cases", "Failures", "Errors", "Skipped"], class_rows, [48, 13, 13, 13, 13]) + """
<p>The baseline before injected faults also passed all 103 cases. The final regression reproduces that
result after the experiments. Baseline and regression logs are separate files.</p>
<h2>Examples from the executed case records</h2>
""" + table(["Case", "Input summary", "Expected", "Actual", "Result"], representative, [18, 33, 20, 20, 9]) + """
<p>Amounts in fee rows are integer kurus. An expected input exception is a successful negative test,
not a test failure. Each of the 103 executions has a unique case record with requirement, technique,
input, expected and actual result in <code>evidence/test-cases.html</code> and its JSON equivalent.
The JUnit result also includes any additional assertions beyond the recorded principal comparison.</p>
<h2>Console demonstration and process checks</h2>
<pre>APPROVED; due date: 2026-11-30
REJECTED; reasons: [INACTIVE_MEMBERSHIP,
                   OUTSTANDING_FEES, LOAN_LIMIT_REACHED]
Three days late: 3.00 TL</pre>
<p>The wrapped rejection above is for readability; the console prints it on one line. Eight separate
JAR process checks passed, covering approval, complete rejection, normal/zero/capped fees, invalid data,
unknown command and the demo. They verify output and exit codes; exact stdout/stderr are preserved in
<code>evidence/console-smoke.json</code>. Deliberately unsuccessful test executions are documented next.</p>
"""

    metrics = [(name.title(), counter_ratio(s["coverage"][name])) for name in ("INSTRUCTION", "LINE", "BRANCH")]
    class_metrics = []
    for row in s["production_classes"]:
        class_metrics.append((row["name"].rsplit("/", 1)[-1],
                              counter_ratio(row["counters"]["LINE"]),
                              counter_ratio(row["counters"].get("BRANCH", {"covered": 0, "missed": 0}))))
    faults_table = []
    for fault in FAULTS:
        example = fault["failing_cases"][0]
        faults_table.append((fault["id"], fault["title"], fault["results"]["failures"],
                             example["id"] + ": " + example["expected"] + " vs " + example["actual"]))
    coverage = """
<h1>6. Code Coverage and Defect Analysis</h1>
<p>JaCoCo attaches its agent to the JUnit process and creates a report during Maven verify [2].
All seven production types are included; no console or validation code is excluded. The preserved
HTML report opens at <code>evidence/jacoco/index.html</code>, with XML and CSV alongside it.</p>
""" + table(["Overall metric", "Covered / total"], metrics, [35, 65]) + table(
        ["Production type", "Line coverage", "Branch coverage"], class_metrics, [34, 33, 33]) + """
<p>Both business services achieved 100% measured line and branch coverage. Overall coverage is lower
because ConsoleApp has an unmeasured main entry point and some command-dispatch branches. The eight
external JAR runs exercise the real process but do not use the JUnit process's JaCoCo agent.
No-branch enum/accessor classes show not applicable for that metric.</p>
<h2>Controlled defect detection</h2>
<p>Three faults were deliberately injected into isolated temporary copies after the correct baseline.
They are seeded experimental defects, not claims about accidental student development mistakes.
Existing relevant tests were run without changing their expected results.</p>
""" + table(["ID", "Injected defect", "Failing cases", "Expected vs actual example"], faults_table, [12, 35, 14, 39]) + """
<p>FI-01 changes the capacity comparison from greater-than-or-equal to greater-than, incorrectly allowing
an applicant exactly at the limit. Restoring the original comparison prevents that approval. FI-02 adds
one to the late-day count; keeping the plain date difference restores free on-time return. FI-03 removes
the cap; restoring the minimum of calculated fee and 5,000 kurus prevents overcharging.</p>
<p>Each faulty version ran nine relevant cases. FI-01 caused two assertion failures, FI-02 four and FI-03 two,
with no test errors. After restoring each copy's correct source, all nine targeted cases passed again.
Raw failure and repaired-run logs, Surefire results, exact diffs and expected/actual values are preserved
under <code>evidence/fault-injection</code>. Source hashes confirm that original Java source and POM were
unchanged by verification. The final full regression passed all 103 cases.</p>
<h2>Interpretation and limits of coverage</h2>
<p>The lecture's RIPR model explains the evidence: a test reaches the faulty comparison/calculation,
produces an incorrect decision or fee, propagates it into the returned value and reveals it through an
assertion [6]. Merely executing the same line would not necessarily reveal the fault.</p>
<p>JaCoCo instruction counts measure executed bytecode, line counts measure executed source lines, and
branch counts cover decision outcomes; exception handling is not counted as branches [3]. These metrics
cannot prove that requirements, assertions or all input combinations are correct. The three selected
faults demonstrate detection of specific mistakes, not a comprehensive mutation score.</p>
"""

    discussion = """
<h1>7. Discussion and Conclusion</h1>
<h2>Effectiveness of the approach</h2>
<p>The small scope made it possible to connect every requirement to executable evidence. Decision-table
tests establish all combinations of the three eligibility conditions for both roles, while boundaries
target the comparisons that distinguish valid periods, available capacity, first late day and fee cap.
Negative cases ensure invalid data is reported deliberately. Calendar examples check behaviours that
simple integer inputs would miss.</p>
<p>Automated unit testing makes these checks repeatable and inexpensive to rerun after changes. A single
build runs the suite and generates coverage. Independent expected examples and the fault experiments
provide evidence of assertion effectiveness beyond a high coverage value. Reviewing requirements and
code also supports early defect prevention, consistent with the lecture's review practices [6]. No
multi-person formal review is claimed for this individual project.</p>
<h2>Implementation and learning challenges</h2>
<p>The actual setup exposed a Java-version mismatch: the machine defaulted to Java 8, while the proposal
specified Java 17. A separate JDK and Maven Wrapper resolved the build environment. Some lecture examples
use JUnit 4 imports and lifecycle annotations; the implementation instead follows the required JUnit 5 API.</p>
<p>The main design challenges were distinguishing a normal rejection from invalid input, returning every
applicable reason, preserving integer money semantics and defining consistent date ordering. Parameterized
tests reduced repetitive test code while preserving a separate, identifiable record for each concrete
scenario. The source and accompanying guide explain these choices and support student review of
the Java and testing concepts.</p>
<h2>Student contribution and learning</h2>
<p>I selected the project topic and small console scope, provided the proposal and course materials,
and sent the topic approval email. I participated in a guided review of requirement examples,
including rejection at the loan limit, invalid requested periods and late-fee calculations.</p>
<p>I studied the Java and testing concepts with explanations from ChatGPT.
This study covered classes, objects and methods; parameters and return values;
integer money representation and LocalDate; JUnit 5 annotations, assertions and parameterized tests;
the five required test techniques; and interpretation of code coverage. I learned how to derive
expected results from requirements and compare them with program output, and why execution coverage
alone does not establish that a test detects an incorrect result.</p>
<p>A worked example clarified the distinction between a due date and the actual return date:
a return on 11 December with a due date of 8 December is three days late and costs 300 kurus.
Another example showed why a borrower exactly at the limit must be rejected: changing the comparison
from greater-than-or-equal to greater-than allows an incorrect approval. These examples connect
the business rules to explicit expected values and boundary tests.</p>
<p>I also learned to distinguish the expected value in an assertion from the actual result returned
by the application. For a three-day delay, the correct fee is 300 kurus. If the application returns
300 but the test expects 400, the test expectation must be corrected using the requirement.
A failing test therefore requires checking both the application behaviour and the expected value.</p>
<h2>Limitations and possible improvements</h2>
<p>The service trusts a caller-supplied borrower snapshot. Without storage or inventory integration it
cannot prevent simultaneous requests from exceeding a real equipment pool, update counts or collect fees.
The chosen numeric policy has not been validated with an operating campus desk. Tests do not exhaust all
possible dates and integers. No performance benchmark, real stakeholder acceptance study or comprehensive
mutation analysis was performed.</p>
<p>Future work could validate policy with stakeholders, add persistent loan records and transactional
inventory control, and broaden property-based or mutation tests. These extensions are outside the submitted
proposal's small console scope. Within the defined scope, the final implementation satisfies the tested
rules and the original suite passes after the controlled defect experiments.</p>
<h2>AI assistance and authorship</h2>
<p>OpenAI Codex assisted implementation, test design, execution orchestration, evidence analysis and report
drafting. ChatGPT was used to study the Java and testing concepts described above.
The student is responsible for verifying the submitted material and explaining and demonstrating
the implementation and testing decisions in accordance with the instructor's guidelines.
The original proposal also acknowledges drafting assistance [8].</p>
"""

    references = """
<h1>8. References</h1>
<p>Official technical references were consulted on 23 November 2026. Source numbering is used in the text.</p>
<p><b>[1]</b> JUnit Team. <i>JUnit 5 User Guide, version 5.13.4.</i> Annotations, assertions, fixtures,
parameterized tests and execution.<br><a href="https://docs.junit.org/5.13.4/user-guide/">docs.junit.org/5.13.4/user-guide/</a></p>
<p><b>[2]</b> JaCoCo Project. <i>Maven Plug-in.</i> Agent configuration and report generation. The build pins
version 0.8.14; the online trunk documentation may describe a newer development version.<br>
<a href="https://www.jacoco.org/jacoco/trunk/doc/maven.html">jacoco.org — Maven plug-in documentation</a></p>
<p><b>[3]</b> JaCoCo Project. <i>Coverage Counters.</i> Definitions and limitations of instruction,
line and branch metrics.<br><a href="https://www.jacoco.org/jacoco/trunk/doc/counters.html">jacoco.org — Coverage counter documentation</a></p>
<p><b>[4]</b> Oracle. <i>Java Platform, Standard Edition 17 API Specification: LocalDate.</i> Date-only
representation and calendar arithmetic.<br>
<a href="https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/time/LocalDate.html">docs.oracle.com — Java 17 LocalDate API</a></p>
<p><b>[5]</b> Apache Software Foundation. <i>Apache Maven 3.9.11 Release Notes.</i><br>
<a href="https://maven.apache.org/docs/3.9.11/release-notes.html">maven.apache.org — Maven 3.9.11 release notes</a></p>
<p><b>[6]</b> Durmaz, O. <i>SWE411 Software Verification and Validation lecture slides.</i> Supplied course
materials: l0 (course introduction), l1 (software engineering and testing foundations), l2 (quality,
MDTD, RIPR and coverage), l3 (practice and test automation), and l4 (reviews and inspections). Undated.</p>
<p><b>[7]</b> Durmaz, O. <i>SVV Research Assignment: Software Development and Automated Testing with JUnit.</i>
Supplied assignment, four pages; <code>references/Assignment.pdf</code>.</p>
<p><b>[8]</b> Kesen, S. K. <i>Campus Equipment Loan Eligibility and Overdue Fee Service: Project proposal for
instructor approval.</i> 21 November 2026. Supplied proposal;
<code>references/project_proposal.pdf</code>. Drafting assistance acknowledged as OpenAI Codex.</p>
<h2>Supporting submission materials</h2>
<p>Java production and test sources; pinned Maven configuration and wrapper; requirement specification;
test plan; all 103 case records; baseline/final execution logs; Surefire XML/text; JaCoCo HTML/XML/CSV;
three controlled fault-experiment records; eight console smoke records; source checksums; environment
details; English build instructions and Turkish demonstration guide.</p>
<p class="small">Traceability and raw evidence remain in the accompanying project rather than being
replaced by the report's representative tables.</p>
"""
    return [intro, requirements, implementation, plan, results, coverage, discussion, references]


class HtmlNode:
    def __init__(self, tag="root", attrs=()):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []


class FragmentParser(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = HtmlNode()
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = HtmlNode(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in ("br", "col", "meta", "hr"):
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in ("br", "col", "meta", "hr"):
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def inline(node, plain=False):
    if isinstance(node, str):
        return node if plain else html.escape(node)
    content = "".join(inline(child, plain) for child in node.children)
    if plain:
        return "\n" if node.tag == "br" else content
    if node.tag in ("b", "i", "u"):
        return f"<{node.tag}>" + content + f"</{node.tag}>"
    if node.tag == "br":
        return "<br/>"
    if node.tag == "code":
        return '<font name="Courier" size="9">' + content + '</font>'
    if node.tag == "a":
        return '<a href="' + html.escape(node.attrs["href"], quote=True) + '" color="#1f4d78">' + content + '</a>'
    return content


def render(sections):
    OUT.mkdir(exist_ok=True)
    html_document = ('<!doctype html><html lang="en"><meta charset="utf-8">'
                     '<title>SWE411 Equipment Loan Report</title><style>' + CSS
                     + 'section+section{break-before:page;page-break-before:always}</style>'
                     + ''.join('<section>' + section + '</section>' for section in sections) + '</html>')
    (ROOT / "docs/report.html").write_text(html_document, encoding="utf-8")
    # PDF-specific preset: standard_business_brief, Helvetica substitution for Calibri,
    # with 1-inch margins and a compact 9.3-point repeated-data table style.
    body = ParagraphStyle("Body", fontName="Helvetica", fontSize=11, leading=12.1,
                          spaceBefore=0, spaceAfter=6, alignment=TA_LEFT, allowWidows=0, allowOrphans=0)
    styles = {"p": body}
    styles["h1"] = ParagraphStyle("H1", parent=body, fontName="Helvetica-Bold", fontSize=16,
                                  leading=18, textColor=colors.HexColor("#2e74b5"),
                                  spaceBefore=16, spaceAfter=8, keepWithNext=True)
    styles["h2"] = ParagraphStyle("H2", parent=body, fontName="Helvetica-Bold", fontSize=13,
                                  leading=15, textColor=colors.HexColor("#2e74b5"),
                                  spaceBefore=12, spaceAfter=6, keepWithNext=True)
    styles["title"] = ParagraphStyle("Title", parent=body, fontName="Helvetica-Bold", fontSize=22,
                                     leading=24, textColor=colors.HexColor("#0b2545"), spaceAfter=9)
    styles["subtitle"] = ParagraphStyle("Subtitle", parent=body, fontSize=12, leading=14,
                                        textColor=colors.HexColor("#526273"), spaceAfter=10)
    styles["meta"] = ParagraphStyle("Metadata", parent=body, fontSize=10, leading=12,
                                    textColor=colors.HexColor("#526273"), spaceAfter=4)
    styles["lead"] = ParagraphStyle("Lead", parent=body, backColor=colors.HexColor("#f4f6f9"),
                                    borderPadding=8, spaceBefore=10, spaceAfter=12)
    styles["small"] = ParagraphStyle("Small", parent=body, fontSize=9.5, leading=11.2)
    cell_style = ParagraphStyle("Cell", parent=body, fontSize=9.3, leading=11,
                                spaceBefore=0, spaceAfter=0)
    header_style = ParagraphStyle("HeaderCell", parent=cell_style, fontName="Helvetica-Bold")
    code_style = ParagraphStyle("Code", fontName="Courier", fontSize=8.5, leading=10.3,
                                backColor=colors.HexColor("#f4f6f9"), borderPadding=6,
                                spaceBefore=3, spaceAfter=10)
    flow = []
    for section_index, section in enumerate(sections):
        # Keep the reference list and supporting-material summary together on a fresh page.
        if section_index == len(sections) - 1:
            flow.append(PageBreak())
        blocks = [node for node in FragmentParser(section).root.children if isinstance(node, HtmlNode)]
        for index, node in enumerate(blocks):
            if node.tag in ("p", "h1", "h2", "h3"):
                chosen = styles.get(node.attrs.get("class", node.tag), body)
                if node.tag == "p" and index + 1 < len(blocks) and blocks[index + 1].tag == "table":
                    chosen = ParagraphStyle("TableIntro", parent=chosen, keepWithNext=True)
                flow.append(Paragraph(inline(node), chosen))
            elif node.tag == "pre":
                flow.append(Preformatted(inline(node, plain=True), code_style))
            elif node.tag == "table":
                data, widths = [], []
                for group in node.children:
                    if isinstance(group, str):
                        continue
                    if group.tag == "colgroup":
                        for col in group.children:
                            if isinstance(col, HtmlNode) and col.tag == "col":
                                widths.append(float(re.search(r"width:([0-9.]+)%", col.attrs["style"]).group(1)))
                    elif group.tag in ("thead", "tbody"):
                        for row in group.children:
                            if isinstance(row, HtmlNode) and row.tag == "tr":
                                data.append([Paragraph(inline(cell), header_style if cell.tag == "th" else cell_style)
                                             for cell in row.children if isinstance(cell, HtmlNode)])
                geometry = [468 * width / 100 for width in widths] if widths else None
                grid = Table(data, colWidths=geometry, repeatRows=1, hAlign="LEFT", splitByRow=1)
                grid.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f4f7")),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd3df")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                # Move the table's heading/introduction with the complete table, avoiding
                # an isolated heading or a single table row at the end of a page.
                prefix = []
                if index > 0 and blocks[index - 1].tag in ("p", "h1", "h2"):
                    prefix.insert(0, flow.pop())
                    if (blocks[index - 1].tag == "p" and index > 1
                            and blocks[index - 2].tag in ("h1", "h2")):
                        prefix.insert(0, flow.pop())
                flow.append(KeepTogether(prefix + [grid, Spacer(1, 8)]))

    destination = OUT / "SWE411_Report.pdf"
    document = BaseDocTemplate(str(destination), pagesize=(612, 792),
                                  leftMargin=72, rightMargin=72, topMargin=64, bottomMargin=64,
                                  title="Campus Equipment Loan Eligibility and Overdue Fee Service",
                                  author="Serdar Kaan Kesen",
                                  subject="SWE411 implementation and JUnit 5 testing report")
    frame = Frame(72, 64, 468, 664, leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0, id="body")
    document.addPageTemplates(PageTemplate(id="Report", frames=[frame]))
    document.build(flow)
    pdf = fitz.open(destination)
    for i, page in enumerate(pdf):
        page.wrap_contents()
        shade = (0.32, 0.38, 0.45)
        page.insert_text((72, 35), "SWE411 | Campus Equipment Loan Service", fontsize=8, color=shade)
        page.insert_text((72, 755), f"Serdar Kaan Kesen | 220911810 | {REPORT_DATE}", fontsize=8, color=shade)
        label = f"{i + 1} / {len(pdf)}"
        page.insert_text((540 - fitz.get_text_length(label, fontsize=8), 755), label, fontsize=8, color=shade)
    final_pdf = destination.with_suffix(".tmp.pdf")
    pdf.save(final_pdf, garbage=4, deflate=True)
    pdf.close()
    final_pdf.replace(destination)
    pdf = fitz.open(destination)
    qa = ROOT / ".qa/report"
    qa.mkdir(parents=True, exist_ok=True)
    for old in qa.glob("page-*.png"):
        old.unlink()
    for i, page in enumerate(pdf):
        page.get_pixmap(matrix=fitz.Matrix(1.4, 1.4)).save(qa / f"page-{i+1}.png")
    print(json.dumps({"report": str(destination), "pages": len(pdf)}, indent=2))
    pdf.close()


if __name__ == "__main__":
    render(build_sections())
