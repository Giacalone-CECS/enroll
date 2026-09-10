#!/usr/bin/env bash
#
# test_enroll.sh: exercise scripts/enroll.py without touching GitHub.
#
# Stubs `gh` on PATH and records every call, so each branch can be asserted
# against what the script *would* have done. Run it before pushing a change to
# the enrolment logic; the real thing is hard to test because failures land in
# a student's issue rather than in front of you.
#
#   ./scripts/test_enroll.sh
set -uo pipefail
cd "$(dirname "$0")/.."

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
LOG="$TMP/gh.log"

cat > "$TMP/gh" <<'STUB'
#!/usr/bin/env bash
echo "$*" >> "$GH_LOG"
case "$1 $2 $3" in
  "teacher roster list") [ -n "${FAKE_ON_ROSTER:-}" ] && echo "$FAKE_ON_ROSTER"; exit 0 ;;
  "teacher roster add")  exit "${FAKE_ADD_RC:-0}" ;;
esac
exit 0
STUB
chmod +x "$TMP/gh"

CODES='{"CECS326-01-FA26-8QK2":"cecs-326-fa26-01"}'
PASS=0; FAIL=0

run() {  # run <body> [on_roster] [add_rc]
  : > "$LOG"
  env PATH="$TMP:$PATH" GH_LOG="$LOG" \
      ENROLL_CODES="$CODES" ORG=Giacalone-CECS \
      ISSUE_NUMBER=1 ISSUE_AUTHOR=studentx ISSUE_BODY="$1" \
      FAKE_ON_ROSTER="${2:-}" FAKE_ADD_RC="${3:-0}" \
      python3 scripts/enroll.py > "$TMP/out" 2>"$TMP/err"
  RC=$?
}

check() {  # check <description> <condition-cmd...>
  if "${@:2}"; then PASS=$((PASS+1)); printf '  PASS  %s\n' "$1"
  else FAIL=$((FAIL+1)); printf '  FAIL  %s\n' "$1"; sed 's/^/        /' "$LOG"; fi
}

log_has()  { grep -q -- "$1" "$LOG"; }
log_lacks(){ ! grep -q -- "$1" "$LOG"; }

echo "enrol tests"

run "### Enrolment code

CECS326-01-FA26-8QK2"
check "valid code adds to the roster"          log_has "teacher roster add Giacalone-CECS cecs-326-fa26-01 studentx"
check "valid code closes the issue"            log_has "issue close 1"
check "the reply names the accept command"     log_has "gh student accept"
check "exit status is 0"                       test "$RC" -eq 0

run "CECS326-01-FA26-WRONG"
check "unknown code does not add anyone"       log_lacks "roster add"
check "unknown code explains itself"           log_has "was not recognised"
check "unknown code still exits 0"             test "$RC" -eq 0

run "hi please add me to the class"
check "missing code does not add anyone"       log_lacks "roster add"
check "missing code explains itself"           log_has "could not find an enrolment code"

run "CECS326-01-FA26-8QK2" "studentx"
check "an existing member is not re-added"     log_lacks "roster add"
check "an existing member is told so"          log_has "already on the roster"

run "CECS326-01-FA26-8QK2" "" 1
check "a failed add blames the instructor"     log_has "my problem rather than"
check "a failed add still exits 0"             test "$RC" -eq 0

run "### Enrolment code

CECS326-01-FA26-8QK2

my id is 032571160"
check "a posted student ID is flagged"         log_has "This repository is public"
check "a posted student ID is not echoed"      log_lacks "032571160"
check "but enrolment still proceeds"           log_has "roster add"

run "### Enrolment code

CECS326-01-FA26-8QK2

reach me at me@student.csulb.edu"
check "a posted email is flagged"              log_has "This repository is public"
check "a posted email is not echoed"           log_lacks "me@student.csulb.edu"

# A student who retypes the issue by hand loses the form's headings.
run "CECS326-01-FA26-8QK2"
check "a hand-typed issue still works"         log_has "roster add"

echo
echo "$PASS passed, $FAIL failed."
[ "$FAIL" -eq 0 ]
