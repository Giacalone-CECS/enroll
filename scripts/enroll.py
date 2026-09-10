#!/usr/bin/env python3
"""Add an issue's author to a Classroom 50 roster, given a valid section code.

Runs from .github/workflows/enroll.yml on `issues: opened`.

The design point: **the issue author is the identity.** GitHub tells us
`issue.user.login` and it cannot be spoofed or mistyped, so the form asks only
for a section code. Nothing identifying is ever posted publicly, which matters
because a public issue naming a student and a course is a FERPA disclosure.

Codes live in the ENROLL_CODES secret, not in this repository, as JSON:

    {"CECS326-01-FA26-8QK2": "cecs-326-fa26-01", ...}

Exit code is always 0: a student who typed the wrong code should get a comment
explaining it, not a red X on a workflow they cannot see.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

ORG = os.environ.get("ORG", "Giacalone-CECS")
CODE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{3,63}$")
# Anything that looks like it should not have been posted publicly.
PII_RE = re.compile(r"(\b\d{9}\b|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})")


def gh(*args: str, check: bool = False) -> tuple[int, str]:
    p = subprocess.run(["gh", *args], capture_output=True, text=True)
    if check and p.returncode != 0:
        raise SystemExit(f"gh {' '.join(args)} failed: {p.stderr.strip()}")
    return p.returncode, (p.stdout + p.stderr).strip()


def parse_code(body: str) -> str | None:
    """Pull the code out of an issue-form body.

    GitHub renders a form as `### Label` followed by the value. Rather than
    depend on that shape, take the first line that looks like a code, which
    survives a student retyping the issue by hand.
    """
    for raw in (body or "").splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", ">", "-", "_", "*")):
            continue
        if line.lower() in ("none", "n/a", "_no response_"):
            continue
        if CODE_RE.match(line):
            return line
    return None


def comment(issue: str, text: str) -> None:
    gh("issue", "comment", issue, "--body", text)


def main() -> int:
    issue = os.environ["ISSUE_NUMBER"]
    author = os.environ["ISSUE_AUTHOR"]
    body = os.environ.get("ISSUE_BODY", "")

    try:
        codes = json.loads(os.environ.get("ENROLL_CODES") or "{}")
    except json.JSONDecodeError:
        comment(issue, "Enrolment is misconfigured on my side. I have been notified; "
                       "nothing you did caused this.")
        print("::error::ENROLL_CODES is not valid JSON", file=sys.stderr)
        return 0

    # Warn about anything that should not be in a public issue. Do not echo it.
    if PII_RE.search(body):
        comment(
            issue,
            "Heads up: it looks like this issue contains a student ID or an email "
            "address. **This repository is public.** I do not need either one, so "
            "please edit the issue and take it out.\n\nCarrying on with your "
            "enrolment regardless."
        )

    code = parse_code(body)
    if not code:
        comment(issue,
                "I could not find an enrolment code in this issue.\n\nOpen a new one "
                "using the form and paste the code from your section's Canvas "
                "announcement. It looks like `CECS326-01-FA26-XXXX`.")
        gh("issue", "close", issue)
        return 0

    classroom = codes.get(code) or codes.get(code.upper())
    if not classroom:
        comment(issue,
                "That enrolment code was not recognised.\n\nCheck you copied it from "
                "the announcement for **your** section, exactly, with no extra "
                "spaces. Then open a new issue with the corrected code.")
        gh("issue", "close", issue)
        return 0

    rc, out = gh("teacher", "roster", "list", ORG, classroom, "--quiet")
    already = author.lower() in {ln.strip().lower() for ln in out.splitlines()} if rc == 0 else False

    if already:
        comment(issue,
                f"You are already on the roster for this section, @{author}.\n\n"
                "If you never got the invitation email, check spam. If it expired, "
                "say so here and I will send another.")
        gh("issue", "close", issue)
        return 0

    rc, out = gh("teacher", "roster", "add", ORG, classroom, author, "--section",
                 classroom.rsplit("-", 1)[-1])
    if rc != 0:
        comment(issue,
                "Something went wrong adding you, and it is my problem rather than "
                "yours. I will sort it out and follow up here.")
        print(f"::error::roster add failed for {author}: {out}", file=sys.stderr)
        return 0

    comment(issue, f"""Done, @{author}. You are on the roster for this section.

**GitHub has emailed you an invitation to the organization. Accept it.**
It expires in **7 days**. If you do not see it, check spam.

Once you have accepted, you can pick up assignments. The command for each one
goes out with its Canvas announcement, and looks like:

```
gh student accept {ORG} {classroom} <assignment>
```

You do not need to come back to this repository.""")
    gh("issue", "close", issue)
    print(f"enrolled {author} in {classroom}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
