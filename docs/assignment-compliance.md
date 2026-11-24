# Assignment compliance map

This map connects the supplied SWE411 assignment and original proposal to concrete project materials. Instructor approval is unconfirmed; implementation proceeded provisionally at the student's request. Original PDFs are preserved in `references`.

## Status by the assignment's original section numbers

The following numbers are the instructor's nine section headings, not a separate development checklist. "Materials ready" describes available artifacts; it is not a grade prediction or a claim of independent student authorship. At the student's request, development continues without waiting for a reply to the proposal email; no actual approval is asserted.

| Section | Instructor's heading | Current status |
| --- | --- | --- |
| 1 | Objective | Application and systematic testing evidence are ready; individual understanding is addressed under sections 7 and 9. |
| 2 | Project Proposal | Proposal prepared and emailed by the student; development continues as requested. |
| 3 | Technical Requirements | Java, JUnit 5, requirements, test plan, case records, defect experiments and coverage materials are ready. |
| 4 | Required Testing Techniques | All five required techniques are implemented and explained. |
| 5 | Research Component | Required discussion topics and credible technical references are included; the student's personal learning reflection remains to be supplied. |
| 6 | Required Deliverables | Eight-section report and supporting source, tests, results, coverage and build configuration are prepared locally; this is not confirmation of submission to the instructor. |
| 7 | Duration and Individual Work | Java/JUnit/build setup is ready. Independent student learning, contribution and ability to explain the work have not yet been verified. The stated 3–4 weeks is a scope/duration expectation, not evidence of time actually spent. |
| 8 | Evaluation Criteria | A rubric, not a separate task. All seven criteria have supporting materials; marks depend on the instructor's assessment of their quality. |
| 9 | Academic Integrity | AI assistance and external sources are acknowledged. This alone does not establish compliance with the own-work requirement; the student's actual contribution, explanation and applicable instructor rules still need review. |

See `docs/student-guide-tr.md` for the explanation exercises and contribution record. A Codex-assisted technical review must not be recorded as the student's independent review.

## Requirement-to-evidence map

| Assignment expectation | Evidence |
| --- | --- |
| Clearly defined real-world problem and small individual scope | Report section 1; original proposal; no GUI/database or external campus-policy claim |
| Explicit, testable functional requirements | `docs/requirements.md`, FR-01 through FR-09; report section 2 |
| Java implementation | Seven production types under `src/main/java`; compiler release 17 |
| JUnit 5 automated tests | Four test classes under `src/test/java`; pinned JUnit Jupiter 5.13.4 |
| Requirements-based test plan | `docs/test-plan.md`; report section 4; case records contain requirement IDs |
| Equivalence partitioning | Test plan partition table; MODEL, DEBT, calendar-fee and console cases |
| Boundary value analysis | CAP, PERIOD, DATE and FEE cases; test plan boundary table |
| Decision table where applicable | Eight Boolean rules for each of two roles; 16 DT cases |
| Negative testing | Invalid borrower data, date ordering, periods, malformed CLI and immutable result checks |
| Regression testing after modifications | Three seeded changes tested in isolated copies; complete original suite rerun; `evidence/regression.log` |
| Inputs, expected and actual results | All 103 records in `evidence/test-cases.html` and JSON; Surefire XML/text |
| Successful and unsuccessful executions | Passing baseline/final runs; actual failing runs in `evidence/fault-injection` |
| Defect analysis | Report section 6; three exact injected diffs and failures, explicitly labelled controlled experiments |
| Coverage measurement and limitations | Full JaCoCo HTML/XML/CSV; all production classes included; report section 6 |
| Testing in SQA and automated-unit-test benefits | Report sections 1 and 7 |
| JUnit 5 features and application | Report section 5; ordinary/parameterized tests, assertions, fresh fixtures |
| Techniques and project-specific justification | Report section 4 and detailed test plan |
| Java/testing challenges | Report section 7; actual setup/version and data-contract challenges; no invented personal experiences |
| At least three credible sources | Five official technical reference pages plus supplied course/assignment/proposal sources in report section 8 |
| Required eight-section individual report | `submission/SWE411_Report.pdf`; editable `docs/report.html` |
| Source, tests, build configuration and reports | Submission ZIP contains all of these and the executable JAR |
| Learning and ability to explain choices | `docs/student-guide-tr.md`; student must review and understand the code and report |
| Acknowledgement of external/AI assistance | Report section 7, README and original proposal; no independent-authorship claim |

No mandatory minimum test count, numerical coverage threshold, GUI, database or specified report length was added. The proposal's exact role limits, date periods, money representation, fee rate and cap were retained. Clarifications of unspecified date ordering and error behaviour are identified in the requirements.
