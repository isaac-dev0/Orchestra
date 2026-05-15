"""
Seed GitHub issues from PLAN.md.

One-shot script: parses task sections (### M{N}-{ROLE}-{NN} — Title) out of
PLAN.md and creates a GitHub issue for each, with milestone, labels, and
assignee derived from the metadata table below.

Usage:
    python scripts/seed-issues.py [--dry-run]

Run from repo root. Requires `gh` CLI authenticated.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "isaac-dev0/Orchestra"
ASSIGNEE_BE = "isaac-dev0"
ASSIGNEE_FE: str | None = None  # Dil's handle TBD; FE issues filed unassigned.

# Metadata per task. Order is the order issues are filed.
# Format: (id, milestone_title, type_label, scope_label, priority)
TASKS: list[tuple[str, str, str, str, str]] = [
    # ---- M0 (folded into M1 milestone) ----
    ("M0-INF-01", "M1 Foundations", "chore", "infra", "P1"),
    ("M0-INF-02", "M1 Foundations", "chore", "firebase", "P1"),
    ("M0-INF-03", "M1 Foundations", "chore", "elastic", "P1"),
    ("M0-INF-04", "M1 Foundations", "chore", "whatsapp", "P1"),
    ("M0-INF-05", "M1 Foundations", "chore", "twilio", "P2"),
    ("M0-INF-06", "M1 Foundations", "chore", "elevenlabs", "P2"),
    ("M0-INF-07", "M1 Foundations", "chore", "infra", "P1"),

    # ---- M1 Foundations ----
    ("M1-BE-01", "M1 Foundations", "feat", "api", "P1"),
    ("M1-BE-02", "M1 Foundations", "feat", "firebase", "P1"),
    ("M1-BE-03", "M1 Foundations", "feat", "api", "P1"),
    ("M1-BE-04", "M1 Foundations", "feat", "firebase", "P1"),
    ("M1-BE-05", "M1 Foundations", "feat", "elastic", "P1"),
    ("M1-BE-06", "M1 Foundations", "feat", "elastic", "P1"),
    ("M1-BE-07", "M1 Foundations", "feat", "firebase", "P1"),
    ("M1-BE-08", "M1 Foundations", "test", "api", "P1"),
    ("M1-BE-09", "M1 Foundations", "infra", "infra", "P1"),
    ("M1-FE-01", "M1 Foundations", "chore", "web", "P1"),
    ("M1-FE-02", "M1 Foundations", "feat", "web", "P1"),
    ("M1-FE-03", "M1 Foundations", "feat", "web", "P1"),
    ("M1-FE-04", "M1 Foundations", "feat", "web", "P1"),
    ("M1-FE-05", "M1 Foundations", "feat", "web", "P1"),
    ("M1-FE-06", "M1 Foundations", "feat", "web", "P1"),
    ("M1-FE-07", "M1 Foundations", "feat", "web", "P1"),

    # ---- M2 Rosa WhatsApp MVP ----
    ("M2-BE-01", "M2 Rosa WhatsApp MVP", "feat", "whatsapp", "P1"),
    ("M2-BE-02", "M2 Rosa WhatsApp MVP", "feat", "whatsapp", "P1"),
    ("M2-BE-03", "M2 Rosa WhatsApp MVP", "feat", "agent", "P1"),
    ("M2-BE-04", "M2 Rosa WhatsApp MVP", "feat", "agent", "P1"),
    ("M2-BE-05", "M2 Rosa WhatsApp MVP", "feat", "calendar", "P1"),
    ("M2-BE-06", "M2 Rosa WhatsApp MVP", "feat", "agent", "P1"),
    ("M2-BE-07", "M2 Rosa WhatsApp MVP", "feat", "agent", "P1"),
    ("M2-BE-08", "M2 Rosa WhatsApp MVP", "feat", "agent", "P1"),
    ("M2-BE-09", "M2 Rosa WhatsApp MVP", "feat", "agent", "P1"),
    ("M2-BE-10", "M2 Rosa WhatsApp MVP", "feat", "whatsapp", "P1"),
    ("M2-BE-11", "M2 Rosa WhatsApp MVP", "feat", "agent", "P1"),
    ("M2-BE-12", "M2 Rosa WhatsApp MVP", "test", "api", "P1"),
    ("M2-FE-01", "M2 Rosa WhatsApp MVP", "feat", "web", "P1"),
    ("M2-FE-02", "M2 Rosa WhatsApp MVP", "feat", "web", "P1"),
    ("M2-FE-03", "M2 Rosa WhatsApp MVP", "feat", "web", "P1"),
    ("M2-FE-04", "M2 Rosa WhatsApp MVP", "feat", "web", "P1"),
    ("M2-FE-05", "M2 Rosa WhatsApp MVP", "refactor", "web", "P1"),

    # ---- M3 Phone (cuttable) ----
    ("M3-BE-01", "M3 Phone channel", "feat", "twilio", "P2"),
    ("M3-BE-02", "M3 Phone channel", "feat", "twilio", "P2"),
    ("M3-BE-03", "M3 Phone channel", "feat", "elevenlabs", "P2"),
    ("M3-BE-04", "M3 Phone channel", "feat", "twilio", "P2"),
    ("M3-BE-05", "M3 Phone channel", "feat", "agent", "P2"),
    ("M3-BE-06", "M3 Phone channel", "feat", "api", "P2"),
    ("M3-BE-07", "M3 Phone channel", "feat", "agent", "P2"),
    ("M3-BE-08", "M3 Phone channel", "test", "twilio", "P2"),
    ("M3-FE-01", "M3 Phone channel", "feat", "web", "P2"),
    ("M3-FE-02", "M3 Phone channel", "feat", "web", "P2"),
    ("M3-FE-03", "M3 Phone channel", "feat", "web", "P2"),

    # ---- M4 Dashboard + onboarding ----
    ("M4-BE-01", "M4 Dashboard + onboarding", "feat", "api", "P1"),
    ("M4-BE-02", "M4 Dashboard + onboarding", "feat", "api", "P1"),
    ("M4-BE-03", "M4 Dashboard + onboarding", "feat", "elastic", "P1"),
    ("M4-BE-04", "M4 Dashboard + onboarding", "feat", "api", "P1"),
    ("M4-FE-01", "M4 Dashboard + onboarding", "feat", "web", "P1"),
    ("M4-FE-02", "M4 Dashboard + onboarding", "feat", "web", "P1"),
    ("M4-FE-03", "M4 Dashboard + onboarding", "feat", "web", "P1"),
    ("M4-FE-04", "M4 Dashboard + onboarding", "refactor", "web", "P1"),
    ("M4-FE-05", "M4 Dashboard + onboarding", "feat", "web", "P1"),
    ("M4-FE-06", "M4 Dashboard + onboarding", "feat", "web", "P1"),
    ("M4-FE-07", "M4 Dashboard + onboarding", "refactor", "web", "P1"),

    # ---- M5 Polish ----
    ("M5-BE-01", "M5 Polish", "refactor", "api", "P2"),
    ("M5-BE-02", "M5 Polish", "test", "api", "P1"),
    ("M5-BE-03", "M5 Polish", "test", "api", "P2"),
    ("M5-FE-01", "M5 Polish", "feat", "web", "P1"),
    ("M5-FE-02", "M5 Polish", "refactor", "web", "P2"),
    ("M5-FE-03", "M5 Polish", "feat", "web", "P2"),
    ("M5-FE-04", "M5 Polish", "refactor", "web", "P1"),

    # ---- M6 Submission ----
    ("M6-SH-01", "M6 Submission", "infra", "infra", "P1"),
    ("M6-SH-02", "M6 Submission", "infra", "infra", "P1"),
    ("M6-SH-03", "M6 Submission", "test", "api", "P1"),
    ("M6-SH-04", "M6 Submission", "docs", "infra", "P1"),
    ("M6-SH-05", "M6 Submission", "docs", "infra", "P1"),
    ("M6-SH-06", "M6 Submission", "chore", "infra", "P1"),
    ("M6-SH-07", "M6 Submission", "chore", "infra", "P1"),
]


def parse_plan(plan_path: Path) -> dict[str, tuple[str, str]]:
    """Return {task_id: (title, body)} parsed from PLAN.md task sections."""
    text = plan_path.read_text(encoding="utf-8")
    # Match: ### M1-BE-03 — Title (rest of line)\n<body>\n### or ## or end
    pattern = re.compile(
        r"^### ((?:M\d+-(?:BE|FE|SH|INF)-\d+)) — (.+?)$\n(.+?)(?=^### |\n^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    out: dict[str, tuple[str, str]] = {}
    for match in pattern.finditer(text):
        task_id = match.group(1).strip()
        title = match.group(2).strip()
        # Strip markdown italics around qualifiers like *(cuttable)* / *(stretch)*
        # because GitHub issue titles render as plain text.
        title = re.sub(r"\*\((\w+)\)\*", r"(\1)", title)
        body = match.group(3).strip()
        out[task_id] = (title, body)
    return out


def assignee_for(task_id: str) -> str | None:
    """BE and INF tasks go to me; FE tasks unassigned (Dil's handle TBD); SH tasks to me."""
    role = task_id.split("-")[1]
    if role in {"BE", "INF", "SH"}:
        return ASSIGNEE_BE
    return ASSIGNEE_FE


def build_body(task_id: str, body: str) -> str:
    return (
        body
        + "\n\n---\n\n"
        + f"Tracked in [PLAN.md](./PLAN.md) under `{task_id}`."
    )


def file_issue(
    task_id: str,
    title: str,
    body: str,
    milestone: str,
    type_label: str,
    scope_label: str,
    priority: str,
    assignee: str | None,
    dry_run: bool,
) -> None:
    full_title = f"{task_id}: {title}"
    labels = [
        f"type: {type_label}",
        f"scope: {scope_label}",
        f"priority: {priority}",
        "status: triage",
        "hackathon",
    ]
    label_arg = ",".join(labels)

    cmd = [
        "gh", "issue", "create",
        "-R", REPO,
        "--title", full_title,
        "--milestone", milestone,
        "--label", label_arg,
    ]
    if assignee:
        cmd += ["--assignee", assignee]

    # Body via temp file (avoids shell escaping issues).
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write(body)
        body_path = f.name
    cmd += ["--body-file", body_path]

    if dry_run:
        print(f"[dry-run] would create: {full_title}")
        print(f"          milestone={milestone}  labels={label_arg}  assignee={assignee or '(unassigned)'}")
        Path(body_path).unlink(missing_ok=True)
        return

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        url = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else "(no url)"
        print(f"  ok: {full_title}\n      {url}")
    except subprocess.CalledProcessError as e:
        print(f"  FAIL: {full_title}", file=sys.stderr)
        print(f"        stderr: {e.stderr.strip()}", file=sys.stderr)
        raise
    finally:
        Path(body_path).unlink(missing_ok=True)


def main() -> None:
    # Windows console defaults to cp1252; force utf-8 for task titles with arrows / em-dashes.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print what would be created without filing.")
    args = parser.parse_args()

    plan_path = Path(__file__).resolve().parent.parent / "PLAN.md"
    sections = parse_plan(plan_path)

    missing = [tid for tid, *_ in TASKS if tid not in sections]
    if missing:
        print(f"ERROR: PLAN.md is missing sections for: {missing}", file=sys.stderr)
        sys.exit(1)

    extra = sorted(set(sections) - {tid for tid, *_ in TASKS})
    if extra:
        print(f"WARNING: PLAN.md has task sections not in TASKS list: {extra}", file=sys.stderr)

    print(f"Filing {len(TASKS)} issues against {REPO}{' (dry-run)' if args.dry_run else ''}...")
    print()

    for task_id, milestone, type_label, scope_label, priority in TASKS:
        title, body = sections[task_id]
        full_body = build_body(task_id, body)
        file_issue(
            task_id=task_id,
            title=title,
            body=full_body,
            milestone=milestone,
            type_label=type_label,
            scope_label=scope_label,
            priority=priority,
            assignee=assignee_for(task_id),
            dry_run=args.dry_run,
        )

    print()
    print(f"Done. Filed {len(TASKS)} issues.")


if __name__ == "__main__":
    main()
