#!/usr/bin/env bash
# sbom_selfrun.sh — technicaldd skill
# Run this INSIDE your own repo. Nothing leaves your machine except
# sbom_report.json at the end — review it before sending it.
#
# STATUS: draft, not yet tested in real conditions. Review before the
# first send to a real target.
set -euo pipefail

REPO_DIR="${1:-.}"

command -v syft >/dev/null || curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
command -v grype >/dev/null || curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin
command -v gitleaks >/dev/null || echo "install gitleaks: https://github.com/gitleaks/gitleaks"

echo "Generating dependency inventory..."
syft "$REPO_DIR" -o json > sbom.json

echo "Checking for known CVEs..."
grype sbom:sbom.json -o json > vulns.json

echo "Classifying licenses..."
python3 <<'PY'
import json
sbom = json.load(open("sbom.json"))
HIGH = {"GPL-2.0", "GPL-3.0", "AGPL-3.0", "AGPL-1.0"}
MED = {"LGPL-2.1", "LGPL-3.0", "MPL-2.0", "MPL-1.1"}
counts = {"high": 0, "medium": 0, "low_or_unknown": 0}
flagged = []
for pkg in sbom.get("artifacts", []):
    lic = pkg.get("licenses") or [{}]
    lic_id = lic[0].get("value") if isinstance(lic[0], dict) else lic[0]
    if lic_id in HIGH:
        counts["high"] += 1
        flagged.append({"name": pkg.get("name"), "license": lic_id})
    elif lic_id in MED:
        counts["medium"] += 1
    else:
        counts["low_or_unknown"] += 1
json.dump({"license_counts": counts, "high_risk_packages": flagged}, open("license_report.json", "w"), indent=2)
PY

echo "Scanning git history for secrets (count only)..."
gitleaks detect --source "$REPO_DIR" --report-format json --report-path gitleaks_raw.json -v || true
python3 <<'PY'
import json
try:
    findings = json.load(open("gitleaks_raw.json"))
except Exception:
    findings = []
json.dump({"secrets_found": len(findings)}, open("secrets_report.json", "w"), indent=2)
PY

echo "Assembling the final aggregated report (the ONLY file to send back)..."
python3 <<'PY'
import json
vulns = json.load(open("vulns.json"))
by_sev = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Negligible": 0, "Unknown": 0}
for m in vulns.get("matches", []):
    sev = m.get("vulnerability", {}).get("severity", "Unknown")
    by_sev[sev] = by_sev.get(sev, 0) + 1
licenses = json.load(open("license_report.json"))
secrets = json.load(open("secrets_report.json"))
sbom = json.load(open("sbom.json"))
report = {
    "total_dependencies": len(sbom.get("artifacts", [])),
    "cve_by_severity": by_sev,
    "license_risk": licenses["license_counts"],
    "high_risk_licenses": licenses["high_risk_packages"],
    "secrets_found_count": secrets["secrets_found"],
}
json.dump(report, open("sbom_report.json", "w"), indent=2)
print(open("sbom_report.json").read())
PY

echo ""
echo "Done. Review sbom_report.json, then send back ONLY that file."
echo "sbom.json, vulns.json, gitleaks_raw.json stay on your machine."
