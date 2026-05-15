<!--
Title format: `type(scope): subject` or `type: subject`.
See RULES.md for the conventional commit rules. Subject is imperative, lowercase, no full stop.
-->

## Summary

<!-- One paragraph. What does this PR do, and why? Not a changelog of files touched. -->

## Linked issue

Closes #

## Type of change

<!-- Tick one. Must match the commit type. -->

- [ ] `feat` — new user-visible capability
- [ ] `fix` — bug fix
- [ ] `refactor` — internal change, no behaviour change
- [ ] `docs` — documentation only
- [ ] `test` — tests only
- [ ] `chore` — maintenance, dependencies
- [ ] `infra` — CI, deploy, tooling

## Multi-tenancy checklist

<!--
From CLAUDE.md. Tick every box or explain why it does not apply.
If this PR has no data access, write "N/A — no data access" under the list.
-->

- [ ] `business_id` is extracted from the verified Firebase token (API) or Firestore phone-number lookup (webhooks) — never from a request body.
- [ ] Every Elasticsearch query goes through `build_query(business_id, ...)`.
- [ ] Every Firestore read/write is scoped under `/businesses/{business_id}/`.
- [ ] A crafted request from another business cannot read or modify the data this PR touches.

## Branding alignment

<!-- For anything user-facing: copy, prompts, dashboard UI, marketing surfaces. -->

- [ ] Voice and tone match `BRANDING.md` (warm, straight-talking, no "AI" in customer-facing copy, contractions, no emojis in product surfaces).
- [ ] N/A — this PR has no user-facing surface.

## Testing

<!--
How was this verified? Be specific.
- For API: which pytest files cover this?
- For agent: did you run a real conversation end-to-end? Which channel?
- For dashboard: which page did you click through?
- For phone: did you verify response time stays under 3 seconds?
-->

## Observability

- [ ] New tool calls open a Dynatrace OTel span (`tool.<name>`) with `business_id`, `channel`, `conversation_id` attributes.
- [ ] N/A — no new tool calls or external integrations.

## Notes for the reviewer

<!-- Anything that won't be obvious from the diff. Trade-offs you considered. Things deliberately out of scope. -->
