# Test plan and design

## Objective and scope

Verify FR-01 through FR-09 against the approved-for-development working specification in `requirements.md`. Business policies come from the proposal; the instructor's actual approval is still unconfirmed. The primary risk is an incorrect eligibility decision or an incorrect daily fee. Test design starts from those requirements and independent expected values, rather than copying service calculations.

Automated unit tests cover borrower validation, complete eligibility decisions, due dates and overdue fees. Console component tests cover parsing, output and error handling. Packaged-JAR smoke tests cover the main entry point and process exit codes. Equipment issuance, persistence, real campus policies and concurrent inventory control are outside scope.

## Equivalence partitioning

| Input | Valid classes | Invalid classes | Representative cases |
| --- | --- | --- | --- |
| Role | STUDENT; STAFF | missing; unrecognised console token | MODEL-05; DT-STUDENT-1; DT-STAFF-1; CLI-NEG-01 |
| Membership | active; inactive | malformed console token | DT rules 1–8; CLI-NEG-02 |
| Current loans | below limit; at limit; above limit | negative; console numeric overflow | CAP-01–09; MODEL-01–02; CLI-NEG-08 |
| Outstanding fees | zero; positive | negative; fractional console input; overflow | DEBT-01–04; MODEL-03–04; CLI-NEG-07/09 |
| Period | within role-specific interval | zero; negative; above maximum; non-integer | PERIOD-01–12; CLI-NEG-14 |
| Return date | early; on time; late below cap; at/above cap | missing; before checkout; malformed | FEE-01–09; FEE-NEG-01–06; CLI-NEG-05 |

These partitions distinguish invalid input from a valid but rejected request. At-limit and indebted borrowers belong to valid input partitions. Invalid tests verify the contract's exception type, while decision tests verify rejection reasons and the absence of a due date.

## Boundary value analysis

| Boundary | Values chosen | Rationale |
| --- | --- | --- |
| Current-loan lower bound | -1, 0 | Separate invalid negative data from a valid empty account. |
| Student capacity | 2, 3, 4 | Check below, at and above the blocking threshold of 3. |
| Staff capacity | 4, 5, 6 | Check below, at and above the blocking threshold of 5. |
| Debt | -1, 0, 1 kurus | A single kurus must block approval; negative fees are invalid. |
| Student period | 0, 1, 6, 7, 8 | Both inclusive ends of 1–7 and immediately outside. |
| Staff period | 0, 1, 13, 14, 15 | Both inclusive ends of 1–14 and immediately outside. |
| Lateness | -1, 0, 1 days | Prevent charging early or on-time returns and missing the first late day. |
| Fee cap | 49, 50, 51 late days | Expect 4,900, 5,000 and 5,000 kurus respectively. |
| Calendar | month end; year end; leap and non-leap February; LocalDate endpoints | Verify calendar arithmetic and range handling. |
| Numeric representations | INT_MIN/MAX; LONG_MIN/MAX; console overflow | Check input representation and safe fee calculation. |

## Decision table

All inputs are otherwise valid. A = active membership, Z = zero outstanding debt, C = count below the role limit. Rules are executed for both STUDENT and STAFF. Each checks approval, the complete reason list and the due-date contract.

| Rule | A | Z | C | Outcome and rejection reasons |
| --- | --- | --- | --- | --- |
| 1 | T | T | T | Approve; no reasons; due date present. |
| 2 | T | T | F | Reject: LOAN_LIMIT_REACHED. |
| 3 | T | F | T | Reject: OUTSTANDING_FEES. |
| 4 | T | F | F | Reject: OUTSTANDING_FEES, LOAN_LIMIT_REACHED. |
| 5 | F | T | T | Reject: INACTIVE_MEMBERSHIP. |
| 6 | F | T | F | Reject: INACTIVE_MEMBERSHIP, LOAN_LIMIT_REACHED. |
| 7 | F | F | T | Reject: INACTIVE_MEMBERSHIP, OUTSTANDING_FEES. |
| 8 | F | F | F | Reject: INACTIVE_MEMBERSHIP, OUTSTANDING_FEES, LOAN_LIMIT_REACHED. |

The 8 combinations exhaust the Boolean model, not every possible application input. They complement boundary and invalid-input tests. Two roles produce 16 concrete decision-table executions.

## Negative testing and state isolation

Reject null roles, borrowers and dates; negative amounts and counts; invalid periods; date overflow; inconsistent return dates; and malformed CLI input. Verify input validation precedes business evaluation. Attempting to mutate returned reasons must fail. Calling an eligible evaluation after a blocked one must not inherit the prior result; an on-time fee after a capped fee must be zero.

## Oracles, organisation and records

Expected dates, amounts and decision-table outputs are literal examples derived from the specification. They do not call production helpers. JUnit 5 parameterized tests express related examples without duplicating test bodies. Each test class gets fresh service fixtures; no test depends on execution order, external services or the current clock. `CaseEvidence` writes a case ID, requirement, technique, input, expected result and observed result into the captured Surefire output before comparing expected with actual. Some cases include additional assertions; the recorded comparison is the principal oracle, and the JUnit result is authoritative for overall pass/fail.

No minimum count or coverage percentage is imposed by the assignment. Completion requires a passing full suite, coverage inspection, all requirements linked to cases, all three fault-injection experiments detected, and an honest account of remaining limitations.

## Regression and defect experiments

First run the unmodified suite. In temporary copies, inject exactly one known fault per experiment: (1) allow a borrower at the loan limit, (2) count an on-time return as one late day, (3) remove the fee cap. Run the relevant existing tests and preserve failures. These are deliberately seeded faults, not claimed accidental development mistakes, and this small set is not a comprehensive mutation score. Keep production source intact, then run the complete original suite again and preserve that final regression output.

## Student execution checks

The student ran the complete Maven/JUnit build and then manually compared the demo, a student loan request at the count limit of 3, and a return three days after its due date with the expected console outputs. The recorded build passed all 103 JUnit executions; all three manual checks matched their expectations. Commands, full expected and actual outputs, raw log locations and log checksums are in `evidence/student-run.json`. The four raw terminal logs are preserved alongside it. Manual checks complement the automated suite and the eight packaged-JAR process checks; they are not counted as additional JUnit executions.

## Coverage and limitations

Measure instruction, line and branch coverage with JaCoCo after `verify`. Include every production class in the report; do not silently exclude console or validation code. Distinguish service coverage from overall coverage if useful. A covered line can still use the wrong comparison or calculation. Coverage does not establish correct assertions, complete requirements, all date combinations or actual campus suitability. The eight-rule decision table and injected faults provide behavioural evidence beyond execution counts.
