# Requirements specification

The Campus Equipment Loan Eligibility and Overdue Fee Service implements the rules in `references/project_proposal.pdf`. These are educational rules, not an actual university policy. Instructor approval has not been confirmed; development is proceeding provisionally as requested by the student.

## Functional requirements

| ID | Requirement and acceptance condition |
| --- | --- |
| FR-01 | Accept a borrower snapshot containing STUDENT or STAFF role, active/inactive membership, current loan count and outstanding fees in integer kurus. Reject missing roles, negative counts and negative fees with `IllegalArgumentException`. Counts at or above a role limit remain valid input, allowing a meaningful eligibility rejection. |
| FR-02 | Approve a new loan if and only if membership is active, outstanding fees equal zero, and current loans are strictly below 3 for students or 5 for staff. One kurus of debt blocks approval. |
| FR-03 | Return every applicable rejection reason in the order INACTIVE_MEMBERSHIP, OUTSTANDING_FEES, LOAN_LIMIT_REACHED. An approved result has no reasons. A rejected result has no due date. |
| FR-04 | Accept requested periods of 1–7 calendar days for students and 1–14 for staff, inclusive. Reject all other integers. Validate the entire input before evaluating membership, debt or capacity. |
| FR-05 | Require an explicit checkout date and calculate an approved request's due date as checkout plus requested days. Use the ISO calendar, including weekends, month/year boundaries and leap days. Reject a request if the resulting due date is outside Java's supported date range. |
| FR-06 | Calculate 0 kurus for return on or before the due date; otherwise charge 100 kurus per late calendar day, capped at 5,000 kurus per return. A late day is the date difference, not an inclusive count. Membership and existing debt do not alter a return's fee. |
| FR-07 | Require checkout, due and return dates for fee calculation. Due date must be strictly after checkout; return must be on or after checkout. An early return is valid. Reject missing or inconsistent dates with `IllegalArgumentException`. |
| FR-08 | Keep evaluation stateless: do not issue equipment, reserve inventory, change a borrower's count, accumulate fees or persist data. Results must be independent of preceding calls, and returned rejection reasons must be immutable. |
| FR-09 | Provide a console demo, loan command, fee command and help. Commands use explicit ISO dates and integer kurus. Print approvals, complete rejections and two-decimal TL amounts. Reject malformed commands with a clear error, usage text and process exit code 2. Valid business rejections are successful evaluations and have exit code 0. |

## Policy and interpretation decisions

Students: loan limit 3, maximum period 7 days. Staff: loan limit 5, maximum period 14 days. Daily fee: 1.00 TL. Per-return cap: 50.00 TL. Money uses `long` integer kurus; loan counts and requested periods use `int`. Values beyond those representations are invalid console inputs.

The proposal requires inconsistent return dates to be rejected but does not define every ordering. FR-07 makes that precise: due date must be after checkout and an early return may occur on checkout day. This follows the minimum one-day loan period while allowing immediate return.

All service-level invalid inputs use `IllegalArgumentException`. Console parsing additionally handles malformed ISO dates and numbers. Valid requests are evaluated without short-circuiting the list of rejection reasons. All input validation occurs before eligibility checks, including for an inactive borrower.

`LocalDate` avoids clock and time-zone dependence. No current system date is consulted. No grace period, holiday adjustment, fee waiver, discount, renewal, authentication, equipment inventory, payment processing, GUI or database is included.

## Nonfunctional requirements

Java 17 source compatibility; Maven build; JUnit 5; JaCoCo instruction, line and branch coverage. Tests must be deterministic, independent and reproducible from the source. The production application has no third-party runtime dependencies. Coverage percentages are reported as measured, with no invented assignment threshold. Every documented test case links to a requirement and contains input, expected and actual outcomes.

## Acceptance evidence

Run `./scripts/build.sh clean verify`. Surefire XML and text results appear under `target/surefire-reports`; JaCoCo HTML/XML/CSV appear under `target/site/jacoco`. Preserved execution evidence is under `evidence`. The report uses the measured run, not a target percentage. Controlled injected faults are documented separately from final passing regression results.
