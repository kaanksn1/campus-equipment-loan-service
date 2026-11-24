# Assignment compliance map

This map connects the supplied SWE411 assignment and original proposal to concrete project materials. Instructor approval is unconfirmed; implementation proceeded provisionally at the student's request. Original PDFs are preserved in `references`.

## Later instructor submission update

The later email takes precedence over the original delivery instructions. Its text is preserved in `references/instructor-submission-update.txt`.

| Updated condition | Current status |
| --- | --- |
| Word or PDF report only | PDF prepared; the ZIP remains supporting material. |
| `STUDENTNUMBER_FIRSTNAME_LASTNAME.pdf` | `220911810_SerdarKaan_Kesen.pdf`; both given names are combined. |
| At most seven pages | Seven pages total, including title information and references; the generator rejects longer output. |
| Relevant code and testing sections only | Selected eligibility, fee and JUnit excerpts, with requirements, results and analysis under the original eight headings. |
| Blackboard: Assignment 1 - File Upload | Not submitted by this workspace; the final upload and receipt remain to be completed. |
| Deadline: 24 November; no late reports | The deadline is recorded. Preparing or pushing the report is not submission. |
| Student's own sentences and code | Not established: substantial implementation and report preparation used Codex. Accurate acknowledgement and recorded student runs do not alone satisfy this separate condition. |

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
| 7 | Duration and Individual Work | Report section 7 describes topic/scope decisions, proposal submission, worked examples, Java/testing study with ChatGPT, and the student's full build and three manual console checks. Raw execution logs are preserved. |
| 8 | Evaluation Criteria | A rubric, not a separate task. All seven criteria have supporting materials; marks depend on the instructor's assessment of their quality. |
| 9 | Academic Integrity | Actual student contributions and AI assistance are documented and sources cited. The later own-sentences/code condition remains unresolved, as recorded above. |

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
| Student build and manual console execution | Report sections 5 and 7; `evidence/student-run.json` and four `student-*.log` files |
| Successful and unsuccessful executions | Passing baseline/final runs; actual failing runs in `evidence/fault-injection` |
| Defect analysis | Report section 6; three exact injected diffs and failures, explicitly labelled controlled experiments |
| Coverage measurement and limitations | Full JaCoCo HTML/XML/CSV; all production classes included; report section 6 |
| Testing in SQA and automated-unit-test benefits | Report sections 1 and 7 |
| JUnit 5 features and application | Report section 5; ordinary/parameterized tests, assertions, fresh fixtures |
| Techniques and project-specific justification | Report section 4 and detailed test plan |
| Java/testing challenges | Report section 7; actual setup/version and data-contract challenges; no invented personal experiences |
| At least three credible sources | Four official technical references and supplied course materials in report section 8 |
| Required eight-section individual report | `submission/220911810_SerdarKaan_Kesen.pdf`; editable `docs/report.html` |
| Source, tests, build configuration and reports | Submission ZIP contains all of these and the executable JAR |
| Learning and ability to explain choices | Report section 7 and `docs/student-guide-tr.md`; design explanations and worked examples |
| Acknowledgement of external/AI assistance | Report section 7, README and original proposal |

No mandatory minimum test count, numerical coverage threshold, GUI or database was added. The later email sets the seven-page maximum and report filename. The proposal's exact role limits, date periods, money representation, fee rate and cap were retained. Clarifications of unspecified date ordering and error behaviour are identified in the requirements.
