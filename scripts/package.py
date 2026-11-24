#!/usr/bin/env python3
"""Create a self-contained source/evidence/report submission archive."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    summary = json.loads((ROOT / "evidence/summary.json").read_text())
    if summary["tests"] != 103 or summary["failures"] or summary["errors"] or summary["skipped"]:
        raise RuntimeError("Expected final passing regression evidence")
    if summary["console_smoke_passed"] != summary["console_smoke_tests"]:
        raise RuntimeError("Console smoke tests must pass")
    faults = json.loads((ROOT / "evidence/fault-injection/summary.json").read_text())
    if len(faults) != 3 or not all(fault["detected"] and fault["repair_verified"] for fault in faults):
        raise RuntimeError("All three seeded faults must be detected and their repairs verified")
    originals = json.loads((ROOT / "evidence/source-sha256.json").read_text())
    for name, checksum in originals.items():
        if digest(ROOT / name) != checksum:
            raise RuntimeError("Source changed since evidence collection: " + name)
    files = []
    for name in ("src", "scripts", "docs", "evidence", "references", ".mvn"):
        files.extend(path for path in (ROOT / name).rglob("*")
                     if path.is_file() and "__pycache__" not in path.parts)
    files.extend(ROOT / name for name in ("pom.xml", "mvnw", "mvnw.cmd", ".gitignore", "README.md", "requirements-docs.txt"))
    files.extend([ROOT / "target/campus-equipment-loan.jar", OUT / "SWE411_Report.pdf"])
    files = sorted(set(files))
    for path in files:
        if not path.exists():
            raise RuntimeError("Missing deliverable: " + str(path))
    manifest = {"project": "Campus Equipment Loan Eligibility and Overdue Fee Service",
                "student": "Serdar Kaan Kesen", "student_number": "220911810",
                "status": "AI-assisted report with student contribution and learning statement; instructor approval unconfirmed",
                "final_tests": summary["tests"], "console_smoke_tests": summary["console_smoke_tests"],
                "detected_controlled_faults": len(faults), "coverage": summary["coverage"],
                "files": {str(path.relative_to(ROOT)): digest(path) for path in files}}
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    files.append(OUT / "MANIFEST.json")
    destination = OUT / "SWE411_Campus_Equipment_Loan_220911810.zip"
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in files:
            bundle.write(path, Path("campus-equipment-loan") / path.relative_to(ROOT))
    with zipfile.ZipFile(destination) as bundle:
        if bundle.testzip() is not None:
            raise RuntimeError("Submission archive failed integrity verification")
    shutil.copy2(ROOT / "target/campus-equipment-loan.jar", OUT / "campus-equipment-loan.jar")
    (OUT / "checksums.sha256").write_text("".join(digest(path) + "  " + path.name + "\n" for path in
                                                  (destination, OUT / "SWE411_Report.pdf", OUT / "campus-equipment-loan.jar")))
    print(json.dumps({"archive": str(destination), "files": len(files), "bytes": destination.stat().st_size}, indent=2))


if __name__ == "__main__":
    main()
