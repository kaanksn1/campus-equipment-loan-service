#!/usr/bin/env python3
"""Run real builds and controlled faults; preserve evidence without editing production source."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import argparse
import difflib
import hashlib
import html
import json
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_hashes():
    paths = sorted((ROOT / "src").rglob("*.java")) + [ROOT / "pom.xml"]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def run_build(root, log, arguments):
    log.parent.mkdir(parents=True, exist_ok=True)
    command = [str(root / "scripts/build.sh"), "-B", "-ntp", "-Dstyle.color=never"] + arguments
    with log.open("w", encoding="utf-8") as output:
        output.write("Command: " + " ".join(command) + "\n")
        output.flush()
        process = subprocess.Popen(command, cwd=root, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            output.write(line)
            if any(token in line for token in ("Tests run:", "BUILD SUCCESS", "BUILD FAILURE", "[ERROR]")):
                print(line.rstrip(), flush=True)
        return process.wait()


def read_results(directory):
    summary = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0, "classes": []}
    records = []
    for path in sorted(directory.glob("TEST-*.xml")):
        suite = ET.parse(path).getroot()
        counts = {key: int(suite.get(key, "0")) for key in ("tests", "failures", "errors", "skipped")}
        for key, value in counts.items():
            summary[key] += value
        summary["classes"].append({"name": suite.get("name"), **counts})
        for case in suite.findall("testcase"):
            state = "FAIL" if case.find("failure") is not None or case.find("error") is not None else "PASS"
            if case.find("skipped") is not None:
                state = "SKIPPED"
            for line in (case.findtext("system-out") or "").splitlines():
                if line.startswith("CASE\t"):
                    fields = line.split("\t")
                    if len(fields) != 7:
                        raise RuntimeError("Malformed case evidence: " + line)
                    records.append(dict(zip(("id", "requirements", "technique", "input", "expected", "actual"), fields[1:]),
                                        status=state, test_class=case.get("classname"), test_method=case.get("name")))
    if not summary["tests"]:
        raise RuntimeError("No test execution results found in " + str(directory))
    return summary, records


def copy_reports(source, dest):
    dest.mkdir(parents=True, exist_ok=True)
    for path in source.iterdir():
        if path.suffix in (".xml", ".txt"):
            shutil.copy2(path, dest / path.name)


FAULTS = [
    ("FI-01", "Loan limit off-by-one", "LoanService.java",
     "borrower.currentLoanCount() >= borrower.role().loanLimit()",
     "borrower.currentLoanCount() > borrower.role().loanLimit()",
     "LoanServiceTest#capacityBoundary"),
    ("FI-02", "On-time return charged as one day late", "OverdueFeeService.java",
     "long lateDays = ChronoUnit.DAYS.between(dueDate, returnDate);",
     "long lateDays = ChronoUnit.DAYS.between(dueDate, returnDate) + 1;",
     "OverdueFeeServiceTest#feeBoundary"),
    ("FI-03", "Per-return fee cap removed", "OverdueFeeService.java",
     "return Math.min(lateDays * DAILY_FEE_CENTS, MAXIMUM_FEE_CENTS);",
     "return lateDays * DAILY_FEE_CENTS;",
     "OverdueFeeServiceTest#feeBoundary"),
]


def inject_faults():
    experiments = []
    for fault_id, title, filename, before, after, selector in FAULTS:
        print("Controlled fault experiment:", fault_id, title, flush=True)
        destination = EVIDENCE / "fault-injection" / fault_id
        with tempfile.TemporaryDirectory(prefix="swe411-fault-") as temp:
            copy = Path(temp)
            for name in ("src", ".mvn", "scripts"):
                shutil.copytree(ROOT / name, copy / name, ignore=shutil.ignore_patterns("__pycache__"))
            for name in ("pom.xml", "mvnw", "mvnw.cmd"):
                shutil.copy2(ROOT / name, copy / name)
            source = copy / "src/main/java/edu/campus/loan" / filename
            original = source.read_text()
            if original.count(before) != 1:
                raise RuntimeError("Mutation must match exactly once: " + fault_id)
            mutated = original.replace(before, after, 1)
            source.write_text(mutated)
            destination.mkdir(parents=True, exist_ok=True)
            patch = difflib.unified_diff(original.splitlines(True), mutated.splitlines(True),
                                         fromfile="original/" + filename, tofile="injected/" + filename)
            (destination / "injected-fault.diff").write_text("".join(patch))
            status = run_build(copy, destination / "execution.log", ["-o", "-Dtest=" + selector, "clean", "test"])
            results, cases = read_results(copy / "target/surefire-reports")
            detected = status != 0 and results["failures"] > 0 and results["errors"] == 0
            experiment = {"id": fault_id, "title": title, "classification": "deliberately seeded fault",
                          "selector": selector, "exit_code": status, "detected": detected,
                          "results": results, "failing_cases": [c for c in cases if c["status"] == "FAIL"]}
            save_json(destination / "result.json", experiment)
            copy_reports(copy / "target/surefire-reports", destination / "surefire-reports")
            if not detected:
                raise RuntimeError("Fault was not detected as a test assertion failure: " + fault_id)
            source.write_text(original)
            repaired_status = run_build(copy, destination / "repaired-execution.log",
                                        ["-o", "-Dtest=" + selector, "clean", "test"])
            repaired_results, _ = read_results(copy / "target/surefire-reports")
            repaired = (repaired_status == 0 and repaired_results["failures"] == 0
                        and repaired_results["errors"] == 0 and repaired_results["skipped"] == 0)
            experiment.update(repair_exit_code=repaired_status, repair_results=repaired_results,
                              repair_verified=repaired)
            save_json(destination / "result.json", experiment)
            copy_reports(copy / "target/surefire-reports", destination / "repaired-surefire-reports")
            if not repaired:
                raise RuntimeError("Repaired copy did not pass its targeted regression: " + fault_id)
            experiments.append(experiment)
    save_json(EVIDENCE / "fault-injection/summary.json", experiments)
    return experiments


def smoke_test():
    cases = [
        ("SMOKE-01", ["loan", "STUDENT", "true", "2", "0", "2026-11-23", "7"], 0,
         "APPROVED; due date: 2026-11-30"),
        ("SMOKE-02", ["loan", "STAFF", "false", "5", "1", "2026-11-23", "14"], 0,
         "REJECTED; reasons: [INACTIVE_MEMBERSHIP, OUTSTANDING_FEES, LOAN_LIMIT_REACHED]"),
        ("SMOKE-03", ["fee", "2026-11-23", "2026-11-30", "2026-12-03"], 0,
         "Overdue fee: 3.00 TL (300 kurus)"),
        ("SMOKE-04", ["fee", "2026-11-23", "2026-11-30", "2027-03-01"], 0,
         "Overdue fee: 50.00 TL (5000 kurus)"),
        ("SMOKE-05", ["fee", "2026-11-23", "2026-11-30", "2026-11-23"], 0,
         "Overdue fee: 0.00 TL (0 kurus)"),
        ("SMOKE-06", ["loan", "STUDENT", "true", "0", "-1", "2026-11-23", "7"], 2,
         "Input error: Outstanding fees cannot be negative."),
        ("SMOKE-07", ["unknown"], 2, "Input error: Unknown command or incorrect argument count."),
        ("SMOKE-08", ["--demo"], 0, "Three days late: 3.00 TL"),
    ]
    results = []
    for case_id, args, expected_code, text in cases:
        completed = subprocess.run([str(ROOT / "scripts/run.sh")] + args, cwd=ROOT,
                                   capture_output=True, text=True, timeout=30)
        actual_text = completed.stderr if expected_code else completed.stdout
        passed = completed.returncode == expected_code and text in actual_text
        results.append({"id": case_id, "args": args, "expected_exit": expected_code,
                        "expected_output_contains": text, "actual_exit": completed.returncode,
                        "stdout": completed.stdout, "stderr": completed.stderr, "passed": passed})
    save_json(EVIDENCE / "console-smoke.json", results)
    if not all(row["passed"] for row in results):
        raise RuntimeError("Packaged JAR smoke test failed")
    return results


def preserve_final():
    summary, cases = read_results(ROOT / "target/surefire-reports")
    if summary["failures"] or summary["errors"] or summary["skipped"]:
        raise RuntimeError("Final test suite must pass without skipped cases")
    if len(cases) != summary["tests"] or len({row["id"] for row in cases}) != len(cases):
        raise RuntimeError("Each execution needs a unique case record")
    save_json(EVIDENCE / "test-cases.json", cases)
    copy_reports(ROOT / "target/surefire-reports", EVIDENCE / "surefire-reports")
    shutil.copytree(ROOT / "target/site/jacoco", EVIDENCE / "jacoco", dirs_exist_ok=True)
    jacoco = ET.parse(ROOT / "target/site/jacoco/jacoco.xml").getroot()
    counters = {counter.get("type"): {"missed": int(counter.get("missed")),
                                      "covered": int(counter.get("covered"))}
                for counter in jacoco.findall("counter")}
    for count in counters.values():
        total = count["covered"] + count["missed"]
        count["percent"] = round(count["covered"] / total * 100, 2) if total else None
    summary["coverage"] = counters
    summary["run_time_oslo"] = datetime.now(ZoneInfo("Europe/Oslo")).isoformat(timespec="seconds")
    summary["production_classes"] = []
    for package in jacoco.findall("package"):
        for cls in package.findall("class"):
            class_counts = {c.get("type"): {"missed": int(c.get("missed")), "covered": int(c.get("covered"))}
                            for c in cls.findall("counter")}
            summary["production_classes"].append({"name": cls.get("name"), "counters": class_counts})
    save_json(EVIDENCE / "summary.json", summary)
    headings = ["ID", "Requirements", "Technique", "Inputs", "Expected", "Actual", "Result"]
    keys = ["id", "requirements", "technique", "input", "expected", "actual", "status"]
    rows = ["<tr>" + "".join("<th>" + h + "</th>" for h in headings) + "</tr>"]
    for case in sorted(cases, key=lambda c: c["id"]):
        rows.append("<tr>" + "".join("<td>" + html.escape(case[key]) + "</td>" for key in keys) + "</tr>")
    body = """<!doctype html><html lang="en"><meta charset="utf-8"><title>Test case execution records</title>
<style>body{font:14px Arial,sans-serif;margin:32px;color:#182430}table{border-collapse:collapse;width:100%}
th,td{border:1px solid #ccd4df;padding:8px;text-align:left;vertical-align:top}th{background:#e8eef5}
tr:nth-child(even){background:#f8fafc}td{overflow-wrap:anywhere}h1{font-size:24px}</style>
<h1>Test case execution records</h1><p>Generated from actual JUnit 5 Surefire XML. Amounts are integer kurus.
The result covers all assertions in the test, including any additional checks beyond the recorded principal comparison.</p>
<p>Run: """ + html.escape(summary["run_time_oslo"]) + "</p><table>" + "".join(rows) + "</table></html>"
    (EVIDENCE / "test-cases.html").write_text(body, encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("all", "baseline", "faults", "regression", "collect"), default="all")
    stage = parser.parse_args().stage
    original_hashes = source_hashes()
    save_json(EVIDENCE / "source-sha256.json", original_hashes)
    if stage in ("all", "baseline"):
        status = run_build(ROOT, EVIDENCE / "baseline.log", ["clean", "verify"])
        if status:
            raise SystemExit(status)
        counts, _ = read_results(ROOT / "target/surefire-reports")
        save_json(EVIDENCE / "baseline-summary.json", counts)
    if stage in ("all", "faults"):
        inject_faults()
    if stage in ("all", "regression"):
        status = run_build(ROOT, EVIDENCE / "regression.log", ["clean", "verify"])
        if status:
            raise SystemExit(status)
    if stage in ("all", "regression", "collect"):
        summary = preserve_final()
        smokes = smoke_test()
        summary["console_smoke_tests"] = len(smokes)
        summary["console_smoke_passed"] = sum(c["passed"] for c in smokes)
        save_json(EVIDENCE / "summary.json", summary)
        print(json.dumps(summary, indent=2), flush=True)
    if source_hashes() != original_hashes:
        raise RuntimeError("Verification must not change original Java source or pom.xml")
    print("Source hashes unchanged.", flush=True)


if __name__ == "__main__":
    main()
