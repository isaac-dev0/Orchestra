# RULES.md

Non-negotiable rules for code in this repo. Both languages. Read before writing code.
Read `CLAUDE.md` first — this file assumes you know the project.

When in doubt, default to the stricter interpretation.

---

## Universal

- **No emojis in code, comments, commit messages, or UI copy.** Markdown documentation (`CLAUDE.md`, `BRANDING.md`, this file) may use emojis as table or list markers where they aid scanning — they must never reach a customer or a code surface.
- **No AI attribution in commit messages.** Never include "Generated with Claude", "Co-authored-by: Claude" or similar.
- **Conventional commits.** Format: `type: subject`, with an optional scope: `type(scope): subject`. Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `infra`. Scope (when used) is the app or feature (`api`, `web`, `agent`, `elastic`, `twilio`). Subject is imperative, lowercase, no full stop. Scope is encouraged on anything non-trivial but not mandatory — `feat: add twilio phone handler` is acceptable.
- **One concern per commit.** A change that touches both the agent and the Nuxt dashboard is two commits.
- **Files are 300 lines or fewer.** Split before exceeding. Agent tools especially — when `agent/tools.py` outgrows the limit, split into `agent/tools/` with one tool per file (see the Agents section below).
- **No commented-out code.** Delete it. Git remembers.
- **Comments answer "why", not "what".** The code says what. Comments explain why this approach, why not the obvious alternative, why this constraint exists.
- **Magic numbers and strings live in named constants.** Inline literals only for genuinely one-off values.
- **No `TODO` comments without an issue reference.** Format: `# TODO(#42): description`. Naked TODOs become tech debt nobody owns.
- **No mock data in production paths.** Fixtures live in `tests/fixtures/`. Seed scripts live in `scripts/seed-*.py`. Never in `apps/api/` or `apps/web/` proper.
- **Secrets never appear in code.** Loaded from GCP Secret Manager at runtime via environment injection. `.env.example` documents expected variables. `.env` is gitignored.

---

## Multi-tenancy — read this before writing any data access code

Every data operation is scoped to a `business_id`. This is not a suggestion.

- **`business_id` is always the Firebase Auth UID.** It is set at signup, never changes, never comes from a request body. Extract it from the verified Firebase ID token on every protected API route.
- **Firestore paths always start with `/businesses/{business_id}/`.** There is no legitimate read or write to a Firestore document outside this prefix (except the phone number → business_id lookup collection).
- **Every Elasticsearch query goes through `build_query(business_id, ...)` in `integrations/elastic.py`.** Never write a raw ES query inline. The wrapper is the enforcement layer — if you bypass it, one plumber can see another's data.
- **Twilio and 360dialog webhooks resolve `business_id` from the inbound phone/WhatsApp number, looked up in Firestore.** Never trust any identity claim in a webhook body.
- **Before shipping any new feature, run through the checklist in `CLAUDE.md`.** If Pete could read Dave's data through your new endpoint, fix it before merging.

---

## Python (`apps/api/`)

### Types and structure

- **`from __future__ import annotations` at the top of every file.** Forward references work without quotes.
- **Type hints on every function signature.** Public and private. Including return types. Including `-> None`.
- **Pydantic for all I/O.** Every FastAPI request body, response model, agent input, agent output, and Firestore document shape is a Pydantic model. No raw dicts crossing module boundaries.
- **No `Any`.** Use `object` if you genuinely cannot be more specific — but you usually can be.
- **Async-first.** All FastAPI endpoints are `async def`. All I/O is async: Firestore via the async Firebase Admin client, Elasticsearch via the async client, HTTP via `httpx.AsyncClient`. No `requests`. No blocking calls on the event loop.
- **No threads. No `asyncio.run()` inside an endpoint.** Async or nothing.

### Naming

- **Files: `snake_case.py`.** Should match the primary class or function inside.
- **Classes: `PascalCase`.** Pydantic models end in their semantic role: `InboundMessage`, `BookingConfirmation`, `BusinessConfig`, `CustomerMemory`.
- **Functions: `snake_case`, verb-first.** `build_prompt`, `resolve_business_id`, `book_calendar_slot`. Not `prompt_builder`, not `business_id_resolver`.
- **Constants: `UPPER_SNAKE_CASE` at module level.**
- **Private helpers prefixed with `_`.**

### Imports

- **Absolute imports only.** `from api.integrations.elastic import build_query`, never relative `from .elastic import ...`.
- **Order: stdlib → third-party → local.** Blank line between groups. `ruff` enforces this.
- **No wildcard imports.** Ever.

### Agents

All agent logic lives in `apps/api/agent/`. The structure is:

```
agent/
├── rosa.py          # LlmAgent definition — model, tools, description
├── prompts.py       # Prompt templates only. No logic.
└── tools.py         # All FunctionTools: calendar, elastic, escalation, whatsapp
```

Rules:

- **Start with a single `tools.py`.** Keep all FunctionTools in one module while the surface is small (this matches `CLAUDE.md`'s structure). Once the file exceeds the 300-line limit, split into `tools/` with one tool per file — at that point, every file in `agent/tools/` must export exactly one `FunctionTool`.
- **Tools never call external services directly.** They call the adapters in `integrations/`. The tool is the ADK interface; the integration is the implementation. This makes testing possible.
- **Prompts live in `agent/prompts.py` as module-level constants.** Never inline a prompt in `rosa.py` or tool logic. Never f-string a prompt; use `.format()` with named placeholders.
- **Prompts are versioned.** When you change a prompt, increment the constant suffix: `ROSA_PROMPT_V1` → `ROSA_PROMPT_V2`. Keep the old version — it enables replay and debugging. Update `rosa.py` to use the new version.
- **Every tool call opens a Dynatrace OTel span.** Use `tracer.start_as_current_span("tool.<name>")`. Set `business_id`, `channel`, and `conversation_id` as span attributes. Record exceptions with `span.record_exception(e)`. This is how the Dynatrace hackathon track is demonstrated — don't skip it.
- **Phone channel responses have hard constraints.** If `channel == "phone"`, Rosa's response must be under 200 words, contain no markdown, no bullet points, no lists. Strip all formatting before passing to ElevenLabs. The tool that calls ElevenLabs enforces this — it is not Rosa's job to remember.

### Integrations (`apps/api/integrations/`)

Integrations are thin wrappers around external SDKs. They are not agents, not tools — they are called by tools.

```
integrations/
├── calendar.py    # Google Calendar SDK wrapper
├── elastic.py     # Elasticsearch async client + build_query()
├── firebase.py    # Firebase Admin — auth verification, Firestore reads/writes
├── elevenlabs.py  # ElevenLabs TTS
└── twilio.py      # Twilio TwiML generation, STT result parsing
```

- **`build_query()` in `integrations/elastic.py` is the only place raw ES queries are constructed.** It always injects the `business_id` filter. If you are writing a dict with `"query"` as a key anywhere else, you are doing it wrong.
- **Firebase ID token verification lives in `integrations/firebase.py`.** Every protected route uses `Depends(verify_firebase_token)`. Never decode a JWT manually elsewhere.
- **Calendar credentials are configured globally for the hackathon build.** `GOOGLE_SERVICE_ACCOUNT_JSON` and `GOOGLE_CALENDAR_ID` (see `CLAUDE.md`) are loaded from env vars at startup. The per-business calendar mapping lives in Firestore (`/businesses/{business_id}/config.calendar_id`) and overrides the global default when present. Per-business OAuth tokens are the post-hackathon target — don't refactor toward them yet, but never hardcode a calendar ID inline either.

### Errors

- **Catch specifically, never bare `except:` or `except Exception:` without re-raising.**
- **Re-raise with context.** `raise IntegrationError("elastic query failed") from err`.
- **Errors that affect a conversation write a structured error to Firestore.** The relevant document's `status` field becomes `"error"`. An `error` map is written with `code`, `message`, and `at` (timestamp).
- **Never silently swallow exceptions.** If you genuinely want to ignore one, log it with `logger.warning()` and add a comment explaining why.
- **OTel spans record exceptions before re-raising.** `span.record_exception(err)` then `raise`.

### Tests (`apps/api/tests/`)

- **Pytest with `pytest-asyncio`.** No `unittest`.
- **Mirror the source tree.** `tests/agent/test_tools.py` tests `agent/tools.py` while it is a single file; if it splits into `agent/tools/`, tests split correspondingly (`tests/agent/test_tools_calendar.py` tests `agent/tools/calendar.py`).
- **Test files: `test_<module>.py`.** Test functions: `test_<behaviour>` — describe what should happen, not what function is called.
- **No tests against live external services in CI.** Mock the integration layer (`integrations/`), not the SDK. The tool calls the integration; the test mocks the integration.
- **Multi-tenancy has dedicated tests.** `tests/test_tenancy.py` must cover: wrong `business_id` rejected, missing token rejected, phone number resolves to correct business, ES query always contains `business_id` filter.

---

## TypeScript (`apps/web/`)

### Types and structure

- **Strict mode on.** `tsconfig.json` has `"strict": true`. No exceptions.
- **Prefer `unknown` over `any`.** `any` is permitted only with an inline comment explaining why a real type is impossible (matches `CLAUDE.md`'s "no `any` without a comment" rule). In practice, almost every case can be `unknown` plus narrowing — reach for `any` last, not first.
- **No non-null assertions (`!`).** Narrow properly with conditionals or optional chaining.
- **Composables prefixed `use`.** `useConversations`, `useJobs`, `useBusinessConfig`, `useRosa`.
- **Stores in `stores/`, composables in `composables/`, components in `components/`.** Don't blur the lines.
- **No hand-written types that duplicate the API.** If FastAPI returns it, the type comes from the API response — define once in `types/api.ts` and import. Don't redefine the same shape in two places.

### Naming

- **Files: `kebab-case.vue` for components, `kebab-case.ts` for composables and stores.**
- **Components: `PascalCase`** in templates and `defineComponent` / `<script setup>`.
- **Composables: `camelCase`**, file name matches the composable name (`use-conversations.ts` exports `useConversations`).
- **Constants: `UPPER_SNAKE_CASE`** for true constants. `camelCase` for everything else.

### Vue / Nuxt patterns

- **`<script setup lang="ts">` everywhere.** No Options API. No `defineComponent` wrapper unless there is a specific reason.
- **`ref()` and `computed()` for reactivity.** No `reactive()` unless you have a documented reason — refs are predictable and easier to reason about.
- **`defineProps<{}>()` with a TypeScript interface.** No runtime prop validation — the type is the contract.
- **`defineEmits<{}>()` typed.** No string array shorthand.
- **No global state outside Pinia stores.** No event buses. No `provide`/`inject` for application state.
- **Auto-imports are fine.** Nuxt UI components, VueUse composables, VueFire composables (`useDocument`, `useCollection`, `useCurrentUser`) are all auto-imported. Do not manually import them.

### Data flow — VueFire and the API

This is important. Read it.

- **Reads use VueFire's `useDocument()` / `useCollection()`.** These subscribe to Firestore in real-time. The conversation feed, job log, and business config all update without polling.
- **All Firestore reads are scoped to the authenticated user's `business_id`.** Use `useCurrentUser()` to get the Firebase user, then construct the path: `/businesses/${user.value.uid}/conversations`. Never hardcode a business ID. Never read from a path you didn't derive from the current user.
- **Writes go through the FastAPI client, not direct Firestore writes from the frontend.** The one exception is the onboarding form, which POSTs to `/onboard` and lets the API write to Firestore. The frontend never writes directly.
- **`pending` refs are always handled.** Every `useDocument()` and `useCollection()` returns a `pending` ref. Render a skeleton or spinner while `pending.value` is true. Never render stale or empty UI while data loads.
- **`error` refs are always handled.** Surface via `useToast()`. Never `console.error` and carry on.

### Styling

- **Nuxt UI components first.** If a `UButton`, `UCard`, `UInput`, or `UTable` exists for the use case, use it. Do not build a bespoke component that duplicates one.
- **Semantic colour tokens only.** Use `bg-primary`, `text-error`, `border-default`, `text-muted`. Do not hardcode hex values or specific Tailwind shades like `bg-green-900` — they bypass theming and will break when the design system is updated.
- **Customise via the `ui` prop.** Nuxt UI's slot and `ui` prop system is the override mechanism. Do not wrap components in extra `<div>`s with scoped CSS to force layout.
- **Custom CSS only in `assets/css/main.css`** using `@theme` directives to extend the design token set. No `<style scoped>` blocks unless the component genuinely needs encapsulated styles that cannot be expressed with Tailwind.

### Errors

- **Try/catch around all API calls.** Catch, surface to user via `useToast()`, do not let unhandled rejections bubble.
- **Loading, empty, error, and success states are all first-class.** Every page that fetches data must render distinct UI for each state. Empty is not the same as error. Loading is not the same as empty.

### Tests (`apps/web/tests/`)

- **Vitest for unit tests.**
- **Mirror the source tree.**
- **No tests against live Firestore.** Use the Firebase emulator suite or mock VueFire composables.
- **Test composables, not components, for business logic.** Components are tested for rendering and interaction; composables are tested for data transformation and state.

---

## What does NOT apply from the old rules

Things that were in the previous `RULES.md` that do not apply to this project
and should not be reintroduced:

- **`BaseAgent` inheritance pattern** — we use Google ADK's `LlmAgent` directly. There is no custom base class.
- **Arize spans** — observability is Dynatrace via OTel. The span pattern is the same; the exporter is different.
- **`backend/partners/` adapter directory** — here it is `integrations/`.
- **OpenAPI codegen (`pnpm codegen`)** — we do not have a shared OpenAPI spec yet. Types in `types/api.ts` are maintained manually until the API stabilises.
- **`shared/openapi.yaml` PR coordination rule** — not applicable.
- **`FitReasoningAgent`, `GrantDocument`, etc.** — old project domain names. Ignore all examples from the previous project.
- **`pytest-asyncio` session-scoped event loop** — use the default function scope unless a specific test requires otherwise.