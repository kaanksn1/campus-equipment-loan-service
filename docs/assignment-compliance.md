# Assignment compliance map

This map connects the supplied SWE411 assignment and original proposal to concrete project materials. Instructor approval is unconfirmed; implementation proceeded provisionally at the student's request. Original PDFs are preserved in `references`.

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
