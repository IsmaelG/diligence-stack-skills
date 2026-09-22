#!/usr/bin/env bash
# compliance_selfrun.sh — technicaldd skill
# Checks for the presence of a few files, nothing more. Reads no
# content, just "does the file exist or not". Combine with the GDPR
# questionnaire (see references/gdpr_questionnaire.md) for the final
# report — this script only covers the verifiable half.
#
# STATUS: draft, not yet tested in real conditions.
REPO_DIR="${1:-.}"

has_security_md=false
[ -f "$REPO_DIR/SECURITY.md" ] && has_security_md=true

has_dependabot=false
[ -f "$REPO_DIR/.github/dependabot.yml" ] && has_dependabot=true

has_codeowners=false
{ [ -f "$REPO_DIR/CODEOWNERS" ] || [ -f "$REPO_DIR/.github/CODEOWNERS" ]; } && has_codeowners=true

cat <<EOF
{
  "security_md_present": $has_security_md,
  "dependabot_config_present": $has_dependabot,
  "codeowners_present": $has_codeowners
}
EOF
