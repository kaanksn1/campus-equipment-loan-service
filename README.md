# Campus Equipment Loan Eligibility and Overdue Fee Service

SWE411 individual assignment — Serdar Kaan Kesen, 220911810.

A small Java 17 console application implementing the supplied project proposal. It evaluates loan eligibility, provides due dates and calculates capped calendar-day overdue fees. There is no GUI, database, equipment issuance, reservation or payment processing. The numeric policy is educational and does not claim to represent a real university. Topic approval has not yet been confirmed; development proceeded provisionally at the student's request.

## Build and run

Install JDK 17 and set `JAVA_HOME` if necessary. The included official Maven Wrapper downloads Maven 3.9.11 on its first run; the first build also downloads test/build dependencies. The Java application has no external runtime dependencies.

macOS / Linux:

```sh
./scripts/build.sh clean verify
./scripts/run.sh --demo
./scripts/run.sh loan STUDENT true 2 0 2026-11-23 7
./scripts/run.sh fee 2026-11-23 2026-11-30 2026-12-03
```

The helper scripts select `JAVA_HOME`, a JDK cached for this workspace, or a normally installed Java 17+ runtime. They make no permanent environment changes. On this computer a JDK 17 was cached because the original default runtime was Java 8.

With a correctly configured Java installation, the standard commands also work:

```sh
./mvnw clean verify
java -jar target/campus-equipment-loan.jar --demo
```

Windows (JDK 17 on `PATH`, or `JAVA_HOME` set):

```bat
mvnw.cmd clean verify
java -jar target\campus-equipment-loan.jar --demo
```

## Console contract

```text
loan <STUDENT|STAFF> <true|false> <currentLoans> <outstandingKurus> <YYYY-MM-DD> <days>
fee <checkoutDate> <dueDate> <returnDate>
--demo
--help
```

One TL = 100 kurus. Input `1` means one kurus, not one TL. Input `100` means 1.00 TL. Monetary inputs must be whole integers. Dates must be explicit ISO dates. A business rejection is a valid evaluation with exit code 0; malformed/invalid input produces exit code 2. Successful output uses stdout and input errors use stderr.

The sample student loan prints `APPROVED; due date: 2026-11-30`. The sample return prints `Overdue fee: 3.00 TL (300 kurus)`.

## Policy

| Rule | Student | Staff |
| --- | --- | --- |
| Maximum active loans | 3 | 5 |
| Valid requested days | 1–7 | 1–14 |
| Membership | Active required | Active required |
| Outstanding debt | Exactly zero required | Exactly zero required |

An applicant at the limit is rejected. Return every applicable rejection reason. An approved due date is checkout plus requested days. Return on/before the due date is free; a late return costs 100 kurus per calendar day, capped at 5,000 kurus. Reject due dates on/before checkout and returns before checkout. Evaluation is stateless and does not increment loan counts.

## Files and evidence

| Location | Purpose |
| --- | --- |
| `src/main/java/edu/campus/loan/` | Seven small production types |
| `src/test/java/edu/campus/loan/` | JUnit 5 parameterized and ordinary tests, plus evidence helper |
| `docs/requirements.md` | FR-01 through FR-09 and explicit interpretation decisions |
| `docs/test-plan.md` | Equivalence classes, boundaries, complete decision table and regression plan |
| `docs/student-guide-tr.md` | Turkish explanation and demonstration guide |
| `docs/report.html` | Editable eight-section report generated from measured evidence |
| `submission/SWE411_Report.pdf` | Rendered report |
| `evidence/test-cases.html` | All recorded test inputs, expected and actual results |
| `evidence/summary.json` | Exact execution and coverage counts |
| `evidence/jacoco/index.html` | Preserved full JaCoCo coverage report |
| `evidence/surefire-reports/` | Preserved JUnit XML/text results |
| `evidence/fault-injection/` | Three deliberately seeded faults, failing logs, diffs and results |
| `evidence/console-smoke.json` | Packaged-JAR output and exit-code checks |
| `references/` | Unchanged supplied proposal and assignment |

Fresh build reports are also available at `target/surefire-reports` and `target/site/jacoco/index.html`. No production classes are excluded from coverage. Coverage alone is not proof of correct requirements or assertions.

## Reproduce the complete evidence workflow

Python 3.9+ is needed only for evidence collection and packaging, not for the Java application or JUnit suite.

```sh
python3 scripts/verify.py
```

This runs the correct baseline, three fault experiments in temporary copies, a final complete regression suite and eight packaged-JAR smoke tests. It preserves real logs and checks that the original Java sources and POM remain unchanged. Deliberately failing fault experiments are expected; the original suite must pass. The experiments are a demonstration of fault detection, not a comprehensive mutation-testing score.

For the optional PDF report builder, install `requirements-docs.txt` in a Python virtual environment and run `python scripts/generate_report.py`. The report builder requires existing final evidence. It does not invent test outcomes.

To recreate the submission archive after building and generating the report:

```sh
python3 scripts/package.py
```

The report PDF and preserved test evidence are versioned. Compiled JARs, submission ZIPs, their generated manifests/checksums and local QA images are generated locally and are excluded from Git.

## Versions and acknowledgement

Java release 17; Maven 3.9.11; JUnit Jupiter 5.13.4; JaCoCo 0.8.14. Other plugin versions are pinned in `pom.xml`. JUnit 5 is used even though some lecture examples show JUnit 4 syntax.

Implementation, test design, execution orchestration, analysis and report drafting were assisted by OpenAI Codex. This is an AI-assisted project for student review. The student must verify the work, understand and explain the decisions, and acknowledge assistance according to the instructor's guidelines. No instructor approval or independent student review is asserted by these files. External technical references appear in the report.
