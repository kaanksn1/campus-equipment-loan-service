# Assignment compliance map

This map connects the supplied SWE411 assignment and original proposal to concrete project materials. Instructor approval is unconfirmed; implementation proceeded provisionally at the student's request. Original PDFs are preserved in `references`.

## Status by the assignment's original section numbers

The following numbers are the instructor's nine section headings. The table maps each heading to the project materials. Development continues without waiting for a reply to the proposal email, as requested by the student.

| Section | Instructor's heading | Current status |
| --- | --- | --- |
| 1 | Objective | Application and systematic testing evidence are ready; individual understanding is addressed under sections 7 and 9. |
| 2 | Project Proposal | Proposal prepared and emailed by the student; development continues as requested. |
| 3 | Technical Requirements | Java, JUnit 5, requirements, test plan, case records, defect experiments and coverage materials are ready. |
| 4 | Required Testing Techniques | All five required techniques are implemented and explained. |
| 5 | Research Component | Required discussion topics, credible technical references and a personal learning reflection are included. The reflection covers Java/testing study and worked examples. |
| 6 | Required Deliverables | Eight-section report and supporting source, tests, results, coverage and build configuration are prepared locally; this is not confirmation of submission to the instructor. |
| 7 | Duration and Individual Work | Java/JUnit/build setup is ready. Report section 7 describes topic/scope decisions, proposal submission, worked examples and the student's study of Java/testing with ChatGPT. |
| 8 | Evaluation Criteria | A rubric, not a separate task. All seven criteria have supporting materials; marks depend on the instructor's assessment of their quality. |
| 9 | Academic Integrity | Report section 7 describes student contributions, learning outcomes and AI assistance. External technical sources are cited in the report and listed in section 8. |

See `docs/student-guide-tr.md` for explanations, worked examples and the contribution record.

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
| Learning and ability to explain choices | Report section 7 and `docs/student-guide-tr.md`; design explanations and worked examples |
| Acknowledgement of external/AI assistance | Report section 7, README and original proposal |

No mandatory minimum test count, numerical coverage threshold, GUI, database or specified report length was added. The proposal's exact role limits, date periods, money representation, fee rate and cap were retained. Clarifications of unspecified date ordering and error behaviour are identified in the requirements.
