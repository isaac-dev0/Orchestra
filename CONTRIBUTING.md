# Contributing

How work happens in this repo. Read `CLAUDE.md` for what we're building and
`RULES.md` for code-level rules. This file covers the process around the code:
branching, issues, labels, milestones, reviews, and merging.

---

## The flow

1. **Every change starts as a GitHub issue.** No "drive-by" PRs. If it's worth
   building, it's worth tracking. The issue captures the why; the PR captures the how.
2. **Pick the right template** when opening the issue — Bug, Feature, or Task.
   Templates pre-fill the `type:` and `status: triage` labels and prompt you for
   scope, priority, and a multi-tenancy / branding check.
3. **Issues land in `status: triage` by default.** The triage step is: confirm
   it's well-defined, add a milestone if it's hackathon-scope, set priority,
   move it to `status: ready` (or `status: in-progress` if you're starting now).
4. **Branch from `main`** using the naming below. Open a PR early — draft is fine
   while work is in flight.
5. **PR template enforces the multi-tenancy and branding checklists.** Both must
   be ticked or explicitly marked N/A before merge.
6. **Squash-merge to `main`.** The squash commit message must be a conventional
   commit (`type(scope): subject` or `type: subject`) — see `RULES.md`.
7. **Linked issue closes automatically** via the `Closes #N` line in the PR body.

---

## Branching

**Trunk-based.** `main` is always deployable. Everything else is a short-lived
branch that exists only long enough to land its PR.

### Branch naming

```
<type>/<scope>-<short-description>
```

- `type` matches the conventional commit types in `RULES.md`:
  `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `infra`.
- `scope` is the area: `api`, `web`, `agent`, `elastic`, `twilio`, `firebase`,
  `dynatrace`, `calendar`, `whatsapp`, `elevenlabs`, `infra`.
- `short-description` is kebab-case, imperative, under ~5 words.

Examples:

```
feat/agent-phone-handler
fix/elastic-memory-empty-on-new-customer
refactor/api-extract-prompt-builder
chore/infra-add-renovate-config
docs/branding-clarify-emoji-rule
```

### Lifetime

- Branches are short. A branch that hasn't merged in a week is a signal that the
  PR is too big or the work has stalled. Split it or close it.
- Rebase onto `main` rather than merging `main` in. The history stays linear.
- Delete the branch after merge. GitHub's "auto-delete head branches" repo setting
  should be on.

### Protected `main`

Required before merging to `main`:
- PR opened (no direct pushes — `main` is protected).
- At least one approving review (self-review counts during solo development, but
  prefer a second pair of eyes once the team grows).
- CI green (`ci.yml`).
- PR template checklists ticked or N/A-justified.

---

## Issues

### Templates

Three templates live in `.github/ISSUE_TEMPLATE/`:

| Template | Use for | Default title prefix |
|---|---|---|
| Bug | Something is broken | `fix:` |
| Feature | New user-visible capability | `feat:` |
| Task / chore | Internal work (refactor, docs, tests, infra) | `chore:` |

Blank issues are disabled — pick a template. If your work doesn't fit, file a
Task and override the type in the form.

### Lifecycle

```
status: triage  →  status: ready  →  status: in-progress  →  status: needs review  →  closed
                                                        ↘
                                                          status: blocked
```

- **triage** — needs a human to decide it's well-defined, prioritise it, attach
  a milestone. Auto-applied by the triage workflow when an issue opens.
- **ready** — agreed, prioritised, can be picked up.
- **in-progress** — someone is actively working on it. Branch and (ideally) draft
  PR exist.
- **needs review** — PR is open and waiting on a reviewer.
- **blocked** — waiting on something external (a credential, a decision, a
  dependent issue). Add a comment explaining what unblocks it.

Only one `status:` label per issue at a time.

### Assignment

Issues auto-assign to their creator via the triage workflow. Reassign manually
if someone else is going to do the work. The assignee is the single owner —
never leave an in-progress issue unassigned.

PRs auto-assign to their author too, so "who owns this" is always answerable
from the assignee column.

---

## Labels

Labels are grouped by prefix. An issue typically has one `type:`, one `scope:`,
one `priority:`, and one `status:` label, plus optional special labels.

### `type:` (matches commit conventional types)

`type: feat`, `type: fix`, `type: refactor`, `type: docs`, `type: test`,
`type: chore`, `type: infra`.

### `scope:` (matches commit scopes in RULES.md)

`scope: api`, `scope: web`, `scope: agent`, `scope: elastic`, `scope: twilio`,
`scope: firebase`, `scope: dynatrace`, `scope: calendar`, `scope: whatsapp`,
`scope: elevenlabs`, `scope: infra`.

### `priority:`

- `priority: P0` — production-breaking. Drop everything.
- `priority: P1` — blocks the current milestone. Fix this week.
- `priority: P2` — fix within this milestone.
- `priority: P3` — backlog. Nice to have.

### `status:`

`status: triage`, `status: ready`, `status: in-progress`, `status: blocked`,
`status: needs review`.

### Special

- `hackathon` — must ship by 2026-06-11.
- `post-hackathon` — explicitly deferred until after submission.
- `good first issue` — well-scoped, low context required.
- `dependencies` — applied automatically by Renovate.

---

## Milestones

Six hackathon-phase milestones, due dates leading up to the 2026-06-11 submission.

| Milestone | Due | What it covers |
|---|---|---|
| M1 Foundations | 2026-05-22 | FastAPI scaffold, Firebase Auth wired, Firestore tenancy structure, Elastic index setup, Dynatrace SDK wired |
| M2 Rosa WhatsApp MVP | 2026-05-29 | 360dialog webhook end-to-end, agent answers, books to Calendar, logs to Elastic |
| M3 Phone channel | 2026-06-03 | Twilio inbound, ElevenLabs outbound, under-3-second response budget met |
| M4 Dashboard + onboarding | 2026-06-05 | Nuxt dashboard with conversation feed and job log, onboarding form seeds a tenant |
| M5 Observability | 2026-06-08 | Dynatrace dashboard demonstrable, OTel spans on every tool, span attributes correct |
| M6 Submission | 2026-06-11 | Demo video recorded, deployed to GCP, public README, both tracks submitted |

Every hackathon-scoped issue gets a milestone at triage. Post-hackathon issues
get the `post-hackathon` label instead.

---

## Commit and PR messages

`RULES.md` is the source of truth — the short version:

- Format: `type: subject` or `type(scope): subject`. Subject imperative,
  lowercase, no full stop.
- One concern per commit. A change to both the agent and the dashboard is two
  commits (and probably two PRs).
- No AI attribution. No "Co-authored-by: Claude".
- Squash-merging means the PR title becomes the commit message — make the PR
  title a valid conventional commit.

---

## Automation

- **`.github/workflows/ci.yml`** — lint and typecheck on push.
- **`.github/workflows/triage.yml`** — assigns new issues to their creator,
  applies `status: triage`, assigns new PRs to their author.
- **Renovate** (`renovate.json`) — keeps dependencies fresh, applies the
  `dependencies` label.
