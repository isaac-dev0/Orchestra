# PLAN — Road to Hackathon Submission (2026-06-11)

The phased plan to ship Rosa for the Google Cloud Rapid Agent Hackathon. Maps
1:1 to the six GitHub milestones (M1–M6), with a pre-milestone M0 for accounts
and credentials.

---

## How to read this

Every task has an ID of the form `M{phase}-{role}-{seq}`:

- **Phase:** `M0`–`M6`.
- **Role:** `BE` (backend, You), `FE` (frontend, Dil), `SH` (shared), `INF` (infrastructure / accounts).
- **Sequence:** zero-padded counter within the role + phase.

Examples: `M0-INF-03`, `M1-BE-04`, `M4-FE-02`, `M6-SH-01`.

Each phase begins with a **Progress** checklist of every task ID in that phase
so you can tick things off and see what's left at a glance. Below the checklist
are detailed task cards — Claude Code (or any agent) should be able to pick up
a card and implement it without needing the rest of this document.

Each task card contains:

- **Goal** — what this task achieves and why.
- **Acceptance criteria** — testable conditions that must all be true before the box is ticked.
- **Files** — paths to create or modify.
- **Depends on** — other task IDs that must be completed first (hard dependencies).
- **Refs** — sections of `CLAUDE.md` / `RULES.md` / `BRANDING.md` that govern this work.
- **Estimate** — rough effort in hours.

`(cuttable)` means the task is currently in scope but is the first to drop if
the timeline slips. `(stretch)` means it's only done if there's runway.

---

## Track decisions

- **Elastic is the sole partner-track commitment.** The product narrative is
  Rosa's memory and Dave's plain-English job search — that *is* the Elastic
  demo. No OTel / Dynatrace work in any phase.
- **Phone channel (M3) is cuttable.** Credentials still get provisioned in M0
  so the option stays open, but if M2 slips by more than three days we skip M3
  and ship WhatsApp + dashboard only.
- **GCP / Firebase / Firestore stay** — we're not pivoting to MongoDB.
- **GitHub Actions stay off.** Local checks plus PR template are the contract
  for the duration of the hackathon.

---

## M0 — Credentials and accounts (dev tenant)

Not a numbered GitHub milestone; folded into the start of M1 in practice. Lives
here so it doesn't get forgotten. Block M1-BE work until M0-INF-01 through 04
and 07 are done. M0-INF-05 and 06 are blockers only for M3.

**Scope: dev tenant only.** Production credentials are provisioned later as
part of M6-SH-01 / M6-SH-02 so they don't block the build. Through M5, every
service runs against the dev tenant — separate Firebase project, separate
Twilio number, `dev-` prefixed Elastic indices, separate 360dialog number if
cheap (else shared with index/path prefixing).

### Progress

- [ ] M0-INF-01 — Create GCP project and enable APIs
- [ ] M0-INF-02 — Create Firebase project, enable Auth and Firestore
- [ ] M0-INF-03 — Provision Elastic Cloud deployment
- [ ] M0-INF-04 — Provision 360dialog WhatsApp account
- [ ] M0-INF-05 — Provision Twilio account and UK number *(cuttable)*
- [ ] M0-INF-06 — Provision ElevenLabs account and pick Rosa's voice *(cuttable)*
- [ ] M0-INF-07 — Store every credential in GCP Secret Manager

### M0-INF-01 — Create GCP project and enable APIs

**Goal:** Stand up the dev cloud project Rosa runs in so every downstream service has somewhere to land.

**Acceptance criteria:**
- A new GCP project (`orchestra-dev` or similar) exists with billing attached.
- The following APIs are enabled: Cloud Run, Secret Manager, Firestore, Calendar API, IAM Credentials.
- A service account `rosa-service@<project>.iam.gserviceaccount.com` is created with roles for Firestore, Secret Manager, and Cloud Run invocation. This same account is what plumbers later share their Google Calendar with — its email is shown in the onboarding form (M4-FE-03).
- `gcloud config get-value project` returns the project ID locally.

**Files:** none — console / `gcloud` operations only.

**Depends on:** nothing.

**Refs:** `CLAUDE.md` §Tech stack, §Environment variables. `RULES.md` §Integrations — "Calendar credentials are configured globally..."

**Estimate:** 1h.

### M0-INF-02 — Create Firebase project, enable Auth and Firestore

**Goal:** Wire Firebase to the same GCP project so Auth UIDs become our `business_id`s and Firestore is the per-tenant data store.

**Acceptance criteria:**
- Firebase project is attached to the GCP project from M0-INF-01.
- Google sign-in is enabled as an Auth provider.
- Firestore is provisioned in **native mode** in `europe-west2` (matches `GCP_REGION`).
- A test Google account can sign in via the Firebase Auth web SDK and produces a verifiable ID token.

**Files:** none — console operations.

**Depends on:** M0-INF-01.

**Refs:** `CLAUDE.md` §Multi-tenancy, §Environment variables.

**Estimate:** 1h.

### M0-INF-03 — Provision Elastic Cloud deployment

**Goal:** A running Elastic Cloud cluster Rosa can write to and search. Single deployment used for both dev and prod, separated by `dev-` / `prod-` index prefixes (cheaper than running two deployments).

**Acceptance criteria:**
- Elastic Cloud deployment exists, region `gcp-europe-west2` (or closest available).
- `cloud_id` and a deployment-scoped API key are captured.
- A `curl` from local against the deployment's `_cluster/health` endpoint returns `green`.
- Settings file documents the `dev-`/`prod-` index prefix convention.

**Files:** none — Elastic Cloud console.

**Depends on:** nothing (parallel with M0-INF-01).

**Refs:** `CLAUDE.md` §Tech stack, §Environment variables.

**Estimate:** 1h.

### M0-INF-04 — Provision 360dialog WhatsApp account

**Goal:** A WhatsApp Business number Rosa can receive messages on.

**Acceptance criteria:**
- 360dialog sandbox or production account active.
- WhatsApp Business number assigned, `phone_number_id` captured.
- 360dialog API key captured.
- A test message sent to the number reaches the 360dialog console (we don't have a webhook yet — visual confirmation in 360dialog UI is enough).

**Files:** none — 360dialog console.

**Depends on:** nothing.

**Refs:** `CLAUDE.md` §Tech stack.

**Estimate:** 2h (verification can be slow).

### M0-INF-05 — Provision Twilio account and UK number *(cuttable)*

**Goal:** A UK phone number Rosa can answer voice calls on.

**Acceptance criteria:**
- Twilio account active.
- A UK number purchased.
- Account SID and auth token captured.
- A test call to the number reaches Twilio's default response (we don't have a webhook yet).

**Files:** none — Twilio console.

**Depends on:** nothing.

**Refs:** `CLAUDE.md` §Tech stack, §Phone call flow.

**Estimate:** 1h.

### M0-INF-06 — Provision ElevenLabs account and pick Rosa's voice *(cuttable)*

**Goal:** Rosa has a voice that matches her brand personality.

**Acceptance criteria:**
- ElevenLabs account active with API access.
- Voice ID selected — must be **warm, British, female** to match Rosa's three-word brand (Warm / Efficient / Reassuring).
- A sample TTS generation runs successfully from the console.
- API key + voice ID captured.

**Files:** none — ElevenLabs console.

**Depends on:** nothing.

**Refs:** `BRANDING.md` §Rosa — Receptionist, §Voice and tone. `CLAUDE.md` §Phone call flow.

**Estimate:** 1–2h (auditioning voices takes time).

### M0-INF-07 — Store every credential in GCP Secret Manager

**Goal:** No credential lives in `.env` files or shell history in production.

**Acceptance criteria:**
- Secrets stored in Secret Manager for every env var listed in `CLAUDE.md` §Environment variables: `ELASTIC_API_KEY`, `ELASTIC_CLOUD_ID`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`, `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`, `WHATSAPP_API_KEY`, `WHATSAPP_PHONE_NUMBER_ID`, `GOOGLE_CALENDAR_ID`, `GOOGLE_SERVICE_ACCOUNT_JSON`, `GEMINI_API_KEY` (if used outside Vertex).
- A `.env.example` file is committed at `apps/api/.env.example` listing every variable with empty values.
- A local `.env` (gitignored) is populated for development.

**Files:** `apps/api/.env.example` (new).

**Depends on:** M0-INF-01 through M0-INF-06 inclusive.

**Refs:** `RULES.md` §Universal — "Secrets never appear in code."

**Estimate:** 2h.

---

## M1 — Foundations (due 2026-05-22)

Goal: scaffolds run end-to-end with auth, tenancy, and one round-trip per integration. No Rosa logic yet — that's M2.

### Progress

**BE (You):**
- [ ] M1-BE-01 — Initialise FastAPI app, settings module, health check
- [ ] M1-BE-02 — Wire Firebase Admin SDK and `verify_firebase_token` dependency
- [ ] M1-BE-03 — Define Pydantic Firestore document models
- [ ] M1-BE-04 — Write and deploy `firestore.rules` enforcing tenant isolation
- [ ] M1-BE-05 — Build `integrations/elastic.py` with `build_query()` wrapper
- [ ] M1-BE-06 — Write `config/elastic_setup.py` to create all three indices
- [ ] M1-BE-07 — Build `integrations/firebase.py` (Firestore async client + token verifier)
- [ ] M1-BE-08 — Write `tests/test_tenancy.py` covering the four required cases
- [ ] M1-BE-09 — Dockerfile + Cloud Run smoke deploy

**FE (Dil):**
- [ ] M1-FE-01 — Confirm Nuxt 3 + Nuxt UI + Tailwind scaffold runs on `bun run dev`
- [ ] M1-FE-02 — Install and configure `nuxt-vuefire` pointing at the Firebase project
- [ ] M1-FE-03 — Build login page with Google sign-in
- [ ] M1-FE-04 — Apply branding colour tokens to Tailwind config
- [ ] M1-FE-05 — Load Fraunces, Inter, JetBrains Mono and wire the type scale
- [ ] M1-FE-06 — Build app shell (top bar, side nav, auth guard)
- [ ] M1-FE-07 — Build empty dashboard layout with placeholder cards

### M1-BE-01 — Initialise FastAPI app, settings module, health check

**Goal:** A FastAPI app boots locally and on Cloud Run with environment-driven settings. Foundation for every other BE task.

**Acceptance criteria:**
- `apps/api/app/main.py` exposes a FastAPI app with `GET /health` returning `{"status":"ok"}` and `200`.
- `apps/api/app/config/settings.py` defines a Pydantic `Settings` class reading every env var from `CLAUDE.md` §Environment variables.
- `from __future__ import annotations` at the top of every Python file (per `RULES.md`).
- `bun run dev` (or `uvicorn app.main:app --reload` inside `apps/api/`) serves the health check.

**Files:**
- `apps/api/app/main.py`
- `apps/api/app/config/settings.py`
- `apps/api/app/config/__init__.py`
- `apps/api/pyproject.toml` (add fastapi, uvicorn, pydantic-settings, httpx)

**Depends on:** M0-INF-01, M0-INF-07.

**Refs:** `CLAUDE.md` §apps/api, §Environment variables. `RULES.md` §Python.

**Estimate:** 4h.

### M1-BE-02 — Wire Firebase Admin SDK and `verify_firebase_token` dependency

**Goal:** Every protected route extracts `business_id` from a verified Firebase ID token. No request body is ever trusted for tenancy.

**Acceptance criteria:**
- `apps/api/app/integrations/firebase.py` exposes `get_firebase_admin()` initialised from `GOOGLE_APPLICATION_CREDENTIALS`.
- A FastAPI dependency `verify_firebase_token(authorization: str = Header(...))` returns the verified `uid` (= `business_id`) or raises `401`.
- A throw-away `/whoami` route uses the dependency and returns `{"business_id": uid}` when called with a valid token; returns `401` with an invalid one.
- Unit test in `apps/api/tests/test_auth.py` covers valid token, missing header, invalid token.

**Files:**
- `apps/api/app/integrations/firebase.py`
- `apps/api/app/dependencies.py`
- `apps/api/tests/test_auth.py`

**Depends on:** M1-BE-01, M0-INF-02.

**Refs:** `CLAUDE.md` §Multi-tenancy — "FastAPI — `business_id` comes from the verified Firebase token". `RULES.md` §Multi-tenancy.

**Estimate:** 5h.

### M1-BE-03 — Define Pydantic Firestore document models

**Goal:** Define the document shapes for Business, Conversation, Job, Customer so every read/write crosses module boundaries as a typed model, not a raw dict.

**Acceptance criteria:**
- `apps/api/app/models/firestore.py` exports `Business`, `Conversation`, `Job`, `Customer` Pydantic models matching the Firestore paths in `CLAUDE.md` §Multi-tenancy.
- Every model has a `business_id: str` field and `model_config = ConfigDict(extra="forbid")`.
- Unit test asserts `model_dump()` round-trips without losing tenancy field.

**Files:**
- `apps/api/app/models/__init__.py`
- `apps/api/app/models/firestore.py`
- `apps/api/tests/test_models.py`

**Depends on:** M1-BE-01.

**Refs:** `CLAUDE.md` §Multi-tenancy — Firestore section. `RULES.md` §Python — Types and structure.

**Estimate:** 4h.

### M1-BE-04 — Write and deploy `firestore.rules` enforcing tenant isolation

**Goal:** Make it physically impossible for Dave to read Pete's data at the database level. Defence in depth — even if API auth is bypassed, Firestore rejects the read.

**Acceptance criteria:**
- `firestore.rules` at repo root contains exactly the rule shape in `CLAUDE.md` §Multi-tenancy — Firestore section.
- Rules deployed via `firebase deploy --only firestore:rules`.
- Manual verification: a curl against Firestore REST API with Pete's ID token attempting to read `/businesses/{daves-uid}` returns `403`.

**Files:**
- `firestore.rules`
- `firebase.json` (Firestore rules config)

**Depends on:** M0-INF-02.

**Refs:** `CLAUDE.md` §Multi-tenancy — Firestore. `RULES.md` §Multi-tenancy.

**Estimate:** 3h.

### M1-BE-05 — Build `integrations/elastic.py` with `build_query()` wrapper

**Goal:** The single chokepoint through which every Elastic query passes. Hard-injects the `business_id` filter so cross-tenant reads are impossible.

**Acceptance criteria:**
- `apps/api/app/integrations/elastic.py` exports an async `ElasticClient` wrapper around the official `elasticsearch[async]` library.
- Module-level `build_query(business_id: str, query: dict) -> dict` matches the implementation in `CLAUDE.md` §Multi-tenancy.
- The wrapper's `search()` / `index()` / `update()` methods always go through `build_query()` — no raw query construction is possible from outside this module.
- A docstring on the module says "If you are writing a raw ES query outside this file, you are doing it wrong."

**Files:**
- `apps/api/app/integrations/elastic.py`
- `apps/api/app/integrations/__init__.py`

**Depends on:** M1-BE-01, M0-INF-03, M0-INF-07.

**Refs:** `CLAUDE.md` §Multi-tenancy — Elasticsearch. `RULES.md` §Integrations.

**Estimate:** 5h.

### M1-BE-06 — Write `config/elastic_setup.py` to create all three indices

**Goal:** A repeatable script that provisions `rosa-conversations`, `rosa-jobs`, `rosa-customers` with explicit mappings. No "auto-mapping" — we want deterministic field types.

**Acceptance criteria:**
- `apps/api/app/config/elastic_setup.py` runnable as `python -m app.config.elastic_setup`.
- Creates three indices if they do not exist; reports "already exists" otherwise (idempotent).
- Each mapping includes a `business_id` keyword field, `doc_type` keyword field, and the document-specific fields per `CLAUDE.md`.
- Mappings include `dense_vector` fields on `rosa-jobs.description_embedding` and `rosa-conversations.message_embedding` for semantic search.
- Running the script from a clean Elastic Cloud deployment produces all three indices and prints their status.

**Files:**
- `apps/api/app/config/elastic_setup.py`

**Depends on:** M1-BE-05.

**Refs:** `CLAUDE.md` §Elasticsearch indices.

**Estimate:** 5h.

### M1-BE-07 — Build `integrations/firebase.py` (Firestore async client + token verifier)

**Goal:** Single module for all Firebase interactions: token verification (from M1-BE-02) plus async Firestore reads/writes scoped under `/businesses/{business_id}/`.

**Acceptance criteria:**
- Extends the file created in M1-BE-02 with: `get_firestore_client()`, plus helpers `get_business_doc(business_id)`, `write_conversation(business_id, conversation)`, `write_job(business_id, job)`.
- Every helper takes `business_id` as its first argument and constructs the path from it; no helper accepts a free-form path.
- Helpers raise if `business_id` is empty or `None`.

**Files:**
- `apps/api/app/integrations/firebase.py` (extend from M1-BE-02)

**Depends on:** M1-BE-02, M1-BE-03.

**Refs:** `CLAUDE.md` §Multi-tenancy — Firestore. `RULES.md` §Integrations.

**Estimate:** 5h.

### M1-BE-08 — Write `tests/test_tenancy.py` covering the four required cases

**Goal:** The four scenarios `RULES.md` mandates: wrong `business_id` rejected, missing token rejected, phone-number lookup resolves correctly, ES query always contains the filter.

**Acceptance criteria:**
- `apps/api/tests/test_tenancy.py` exists with four test functions, names match the bullets in `RULES.md` §Tests.
- All four pass via `pytest apps/api/tests/test_tenancy.py`.
- No test hits live Elastic or Firestore — `integrations/` is mocked.

**Files:**
- `apps/api/tests/test_tenancy.py`
- `apps/api/tests/conftest.py` (fixtures for mocked integrations)

**Depends on:** M1-BE-02, M1-BE-05, M1-BE-07.

**Refs:** `RULES.md` §Tests — "Multi-tenancy has dedicated tests."

**Estimate:** 6h.

### M1-BE-09 — Dockerfile + Cloud Run smoke deploy

**Goal:** Prove the FastAPI app deploys to Cloud Run with credentials wired from Secret Manager. Catches deploy-time issues before M2 piles work on top.

**Acceptance criteria:**
- `apps/api/Dockerfile` builds an image that runs the health check on `$PORT`.
- A Cloud Run service `rosa-api-dev` is deployed in `europe-west2`.
- Service env vars reference Secret Manager (no plaintext secrets in the Cloud Run config).
- `curl https://<service-url>/health` returns `{"status":"ok"}`.

**Files:**
- `apps/api/Dockerfile`
- `apps/api/.dockerignore`

**Depends on:** M1-BE-01, M0-INF-07.

**Refs:** `CLAUDE.md` §Tech stack — Hosting.

**Estimate:** 4h.

### M1-FE-01 — Confirm Nuxt 3 + Nuxt UI + Tailwind scaffold runs

**Goal:** Sanity-check that the existing scaffold boots, and that the scaffold runs under `bun`.

**Acceptance criteria:**
- `apps/web/node_modules` removed and `bun install` succeeds from repo root.
- `bun run dev` (Turbo) starts the Nuxt dev server on `http://localhost:3000`.
- The starter page renders without console errors.

**Files:** none new — clean install only.

**Depends on:** nothing.

**Refs:** `CLAUDE.md` §apps/web.

**Estimate:** 2h.

### M1-FE-02 — Install and configure `nuxt-vuefire`

**Goal:** Wire the Nuxt app to Firebase Auth and Firestore so VueFire composables are available throughout the app.

**Acceptance criteria:**
- `nuxt-vuefire` added to `apps/web/package.json` and registered in `apps/web/nuxt.config.ts`.
- VueFire `auth` and `appCheck: false` configured.
- `FIREBASE_*` runtime env vars wired via `runtimeConfig.public`.
- Calling `useCurrentUser()` in a test page returns `null` when signed out.

**Files:**
- `apps/web/nuxt.config.ts`
- `apps/web/.env.example`

**Depends on:** M1-FE-01, M0-INF-02.

**Refs:** `CLAUDE.md` §apps/web — Nuxt config. `RULES.md` §TypeScript — Data flow.

**Estimate:** 3h.

### M1-FE-03 — Build login page with Google sign-in

**Goal:** Dave can log in with one click. No password, no friction.

**Acceptance criteria:**
- `apps/web/app/pages/login.vue` renders a Sign-in-with-Google button using Nuxt UI's `UButton`.
- Clicking the button opens the Firebase Google popup and authenticates.
- Successful sign-in redirects to `/dashboard`.
- If already signed in, the page redirects away from `/login` automatically.
- Copy on the page follows `BRANDING.md` voice (warm, no "AI", contractions).

**Files:**
- `apps/web/app/pages/login.vue`
- `apps/web/app/middleware/auth.ts` (route guard)

**Depends on:** M1-FE-02.

**Refs:** `BRANDING.md` §Voice and tone, §Copy examples. `RULES.md` §Vue / Nuxt patterns.

**Estimate:** 4h.

### M1-FE-04 — Apply branding colour tokens to Tailwind config

**Goal:** The whole app uses semantic colour names (`bg-primary`, `text-error`) that map to the brand palette, not hardcoded hexes.

**Acceptance criteria:**
- `apps/web/app/assets/css/main.css` defines CSS variables for every colour in `BRANDING.md` §Visual identity — Colours.
- Nuxt UI's primary colour is set to a name that resolves to `Deep Green #1B3A2D`.
- Secondary / accent maps to Coral `#C8624A`.
- `bg-primary`, `text-primary`, `border-default`, `text-muted`, `bg-error`, `bg-success` all render correctly in a smoke component.
- Body background is Warm Off-White `#F5F0E8`, body text is Warm Almost-Black `#1A1A18`.

**Files:**
- `apps/web/app/assets/css/main.css`
- `apps/web/app/app.config.ts`

**Depends on:** M1-FE-01.

**Refs:** `BRANDING.md` §Visual identity — Colours. `RULES.md` §Styling.

**Estimate:** 4h.

### M1-FE-05 — Load Fraunces, Inter, JetBrains Mono and wire the type scale

**Goal:** Typography matches the brand — Fraunces for display, Inter for body, JetBrains Mono for data.

**Acceptance criteria:**
- `@nuxt/fonts` loads the three families with the weights specified in `BRANDING.md` §Typography.
- Tailwind `font-display`, `font-sans` (default body), `font-mono` resolve to Fraunces / Inter / JetBrains Mono respectively.
- A type-scale demo page renders the eight steps (Display through Mono) at the sizes in `BRANDING.md`.

**Files:**
- `apps/web/nuxt.config.ts`
- `apps/web/app/assets/css/main.css` (font-family rules)

**Depends on:** M1-FE-01.

**Refs:** `BRANDING.md` §Typography.

**Estimate:** 3h.

### M1-FE-06 — Build app shell (top bar, side nav, auth guard)

**Goal:** The consistent chrome every dashboard page lives inside. Navigation works; signed-out users can't see it.

**Acceptance criteria:**
- Top bar: logo (placeholder OK), signed-in user's avatar (Google photo) + name, sign-out button.
- Side nav: Dashboard, Conversations, Jobs, Settings — each routes to a placeholder page.
- Layout (`apps/web/app/layouts/default.vue`) wraps every dashboard route.
- Route middleware redirects unauthenticated users to `/login`.
- All copy passes the no-"AI" rule.

**Files:**
- `apps/web/app/layouts/default.vue`
- `apps/web/app/components/AppShell.vue` (or inline)
- `apps/web/app/middleware/auth.global.ts`

**Depends on:** M1-FE-03, M1-FE-04.

**Refs:** `CLAUDE.md` §apps/web — Pages.

**Estimate:** 5h.

### M1-FE-07 — Build empty dashboard layout with placeholder cards

**Goal:** `/dashboard` renders the shape of the final page so M2 FE can drop real data into the slots.

**Acceptance criteria:**
- `apps/web/app/pages/dashboard/index.vue` shows three placeholder cards: "Today's bookings", "Recent conversations", "Anything urgent".
- Cards use Nuxt UI's `UCard`.
- No data wiring — static placeholders only.
- Loading / empty / error visual states are sketched in (even if not wired).

**Files:**
- `apps/web/app/pages/dashboard/index.vue`

**Depends on:** M1-FE-06.

**Refs:** `CLAUDE.md` §apps/web — Pages.

**Estimate:** 3h.

---

## M2 — Rosa WhatsApp MVP (due 2026-05-29)

Goal: a real customer can WhatsApp Dave's number, have a conversation with Rosa, and get booked into his calendar. Dashboard updates live. Returning customers are recognised.

### Progress

**BE (You):**
- [ ] M2-BE-01 — 360dialog webhook handler with `business_id` resolution
- [ ] M2-BE-02 — Pydantic models for inbound/outbound WhatsApp payloads
- [ ] M2-BE-03 — Define Rosa as an ADK `LlmAgent` in `agent/rosa.py`
- [ ] M2-BE-04 — Write `agent/prompts.py` with `ROSA_PROMPT_V1`
- [ ] M2-BE-05 — Build `integrations/calendar.py` (Google Calendar async wrapper)
- [ ] M2-BE-06 — Tool: `get_customer_memory` (Elastic lookup by phone)
- [ ] M2-BE-07 — Tool: `get_available_slots` (Calendar read, next 7 days)
- [ ] M2-BE-08 — Tool: `book_calendar_slot` (Calendar write + Firestore job)
- [ ] M2-BE-09 — Tool: `log_conversation` (write each turn to Elastic + Firestore)
- [ ] M2-BE-10 — Tool: `send_whatsapp_reply` (360dialog outbound)
- [ ] M2-BE-11 — Tool: `escalate_to_plumber` (record + WhatsApp Dave)
- [ ] M2-BE-12 — End-to-end WhatsApp booking test

**FE (Dil):**
- [ ] M2-FE-01 — `ConversationFeed` component (real-time via VueFire)
- [ ] M2-FE-02 — Conversation detail page (transcript view)
- [ ] M2-FE-03 — `JobCard` component + jobs list page
- [ ] M2-FE-04 — Dashboard index wired to real data
- [ ] M2-FE-05 — Loading / empty / error states pass

### M2-BE-01 — 360dialog webhook handler with `business_id` resolution

**Goal:** Accept inbound WhatsApp messages, resolve which plumber's number was messaged, hand off to Rosa.

**Acceptance criteria:**
- `POST /webhook/whatsapp` accepts the 360dialog payload shape.
- Signature verification against `WHATSAPP_API_KEY` rejects forged requests with `401`.
- Looks up `/whatsapp_numbers/{wa_phone_number_id}` in Firestore to resolve `business_id`; `404` if not found.
- Loads `/businesses/{business_id}/config` and passes it to the agent runner (stub for now — agent comes in M2-BE-03).
- Logs the inbound message turn via `log_conversation` (stub OK for now).
- Returns `200` quickly so 360dialog doesn't retry.

**Files:**
- `apps/api/app/channels/whatsapp.py`
- `apps/api/app/main.py` (route registration)
- `apps/api/tests/test_whatsapp_webhook.py`

**Depends on:** M1-BE-02, M1-BE-07, M0-INF-04.

**Refs:** `CLAUDE.md` §Multi-tenancy — 360dialog webhook, §Routes. `RULES.md` §Multi-tenancy.

**Estimate:** 5h.

### M2-BE-02 — Pydantic models for inbound/outbound WhatsApp payloads

**Goal:** No raw dict ever crosses the channel boundary.

**Acceptance criteria:**
- `apps/api/app/models/whatsapp.py` defines `InboundWhatsAppMessage` and `OutboundWhatsAppReply`.
- Field shapes match the 360dialog API spec.
- All fields typed; no `Any`.
- Models reused by the webhook handler (M2-BE-01) and the outbound tool (M2-BE-10).

**Files:**
- `apps/api/app/models/whatsapp.py`
- `apps/api/tests/test_models_whatsapp.py`

**Depends on:** M1-BE-01.

**Refs:** `RULES.md` §Python — "Pydantic for all I/O."

**Estimate:** 3h.

### M2-BE-03 — Define Rosa as an ADK `LlmAgent` in `agent/rosa.py`

**Goal:** The agent definition itself — model, tools list, channel-agnostic.

**Acceptance criteria:**
- `apps/api/app/agent/rosa.py` defines an ADK `LlmAgent` named `rosa`.
- Model = `gemini-2.0-flash` from settings.
- Tools list references all M2 tools (imports from `agent/tools.py`).
- A `run_rosa(business_config, channel, message, conversation_history)` async function is the single entrypoint webhooks call.
- `channel` arg accepted: `"whatsapp"` or `"phone"`. Channel attribute passed through to every tool span (when M5 spans land — for now just a metadata field).

**Files:**
- `apps/api/app/agent/__init__.py`
- `apps/api/app/agent/rosa.py`

**Depends on:** M2-BE-04, M2-BE-06 through M2-BE-11 (the tools).

**Refs:** `CLAUDE.md` §apps/api — Agent design. `RULES.md` §Agents.

**Estimate:** 5h.

### M2-BE-04 — Write `agent/prompts.py` with `ROSA_PROMPT_V1`

**Goal:** A single prompt template, versioned, with named placeholders filled per-business at runtime.

**Acceptance criteria:**
- `apps/api/app/agent/prompts.py` exports `ROSA_PROMPT_V1` as a module-level constant string.
- Placeholders use `.format()` style: `{business_name}`, `{owner_name}`, `{service_area}`, `{base_prices}`, `{working_hours}`, `{escalation_rules}`, `{channel}`.
- A `build_rosa_prompt(business_config, channel)` helper formats the template from a `Business` Pydantic model.
- Prompt embeds the safety rules from `CLAUDE.md` §Rosa's ADK agent (gas smells, flooding, complaints → escalate).
- Tone in the prompt matches `BRANDING.md` §Rosa — Receptionist.
- No prompt strings live anywhere else in the codebase.

**Files:**
- `apps/api/app/agent/prompts.py`

**Depends on:** M1-BE-03.

**Refs:** `CLAUDE.md` §Rosa's ADK agent — System prompt is per-customer. `BRANDING.md` §Rosa. `RULES.md` §Agents — "Prompts live in `agent/prompts.py`".

**Estimate:** 6h.

### M2-BE-05 — Build `integrations/calendar.py` (Google Calendar async wrapper)

**Goal:** Async wrapper over the Google Calendar Python SDK so tool code is clean.

**Acceptance criteria:**
- `apps/api/app/integrations/calendar.py` exposes async `list_events(calendar_id, time_min, time_max)`, `find_free_slots(calendar_id, duration_minutes, days_ahead)`, `create_event(calendar_id, event)`.
- Uses the service account credentials from `GOOGLE_SERVICE_ACCOUNT_JSON`.
- `calendar_id` is resolved per-business: looks up `/businesses/{business_id}/config.calendar_id` in Firestore, falls back to the global `GOOGLE_CALENDAR_ID` env var.
- Every method wraps the SDK call in `try`/`except` and re-raises as a typed `CalendarError`.

**Files:**
- `apps/api/app/integrations/calendar.py`
- `apps/api/app/integrations/errors.py` (CalendarError, ElasticError, etc.)

**Depends on:** M1-BE-07.

**Refs:** `CLAUDE.md` §Tech stack — Calendar. `RULES.md` §Integrations — "Calendar credentials are configured globally..."

**Estimate:** 6h.

### M2-BE-06 — Tool: `get_customer_memory`

**Goal:** Rosa can look up whether a phone number belongs to a returning customer and recall context.

**Acceptance criteria:**
- Function in `apps/api/app/agent/tools.py` (single file per the current `agent/tools.py` rule) decorated as an ADK `FunctionTool`.
- Takes `business_id` and `customer_phone`, returns a `CustomerMemory` model (last interactions, jobs, preferences) or `None`.
- Queries `rosa-customers` index via `ElasticClient.search(build_query(business_id, {...}))`.
- Tool never calls Elastic SDK directly — only through `integrations/elastic.py`.

**Files:**
- `apps/api/app/agent/tools.py` (extend)

**Depends on:** M1-BE-05, M2-BE-04.

**Refs:** `CLAUDE.md` §Multi-tenancy — Elasticsearch. `RULES.md` §Agents — Tools.

**Estimate:** 4h.

### M2-BE-07 — Tool: `get_available_slots`

**Goal:** Rosa can offer real free time from Dave's actual calendar.

**Acceptance criteria:**
- FunctionTool in `agent/tools.py` taking `business_id`, `duration_minutes`, `days_ahead`.
- Returns a list of free slot start times in the business's working hours (from Firestore config).
- Excludes weekends if config says so.
- Returns at most 5 slots so the LLM doesn't spam the customer.

**Files:**
- `apps/api/app/agent/tools.py` (extend)

**Depends on:** M2-BE-05, M2-BE-06.

**Refs:** `CLAUDE.md` §Rosa's ADK agent — Phone-specific constraints (still applies for WhatsApp: keep responses short).

**Estimate:** 4h.

### M2-BE-08 — Tool: `book_calendar_slot`

**Goal:** Rosa writes the booking to Google Calendar and to Firestore atomically (well, sequentially with compensation if one fails).

**Acceptance criteria:**
- FunctionTool taking `business_id`, `customer_name`, `customer_phone`, `job_description`, `slot_start`, `duration_minutes`, `address`.
- Writes a calendar event and a `/businesses/{business_id}/jobs/{job_id}` Firestore doc.
- If Firestore write fails after calendar succeeds, deletes the calendar event (compensation) and raises.
- Returns a `BookingConfirmation` Pydantic model.

**Files:**
- `apps/api/app/agent/tools.py` (extend)

**Depends on:** M2-BE-05, M2-BE-07, M1-BE-07.

**Refs:** `CLAUDE.md` §Multi-tenancy — Firestore. `RULES.md` §Errors.

**Estimate:** 6h.

### M2-BE-09 — Tool: `log_conversation`

**Goal:** Every message Rosa sends or receives lands in `rosa-conversations` (Elastic, for search) and `/businesses/{id}/conversations/{conv_id}` (Firestore, for real-time dashboard).

**Acceptance criteria:**
- FunctionTool taking `business_id`, `conversation_id`, `direction` ("inbound"|"outbound"), `channel`, `customer_phone`, `text`, `timestamp`.
- Writes to both Elastic and Firestore in parallel via `asyncio.gather`.
- Firestore doc structure: append-only sub-collection `messages` under each conversation doc, so VueFire `useCollection` updates in real time.

**Files:**
- `apps/api/app/agent/tools.py` (extend)

**Depends on:** M1-BE-05, M1-BE-07.

**Refs:** `CLAUDE.md` §Elasticsearch indices, §Multi-tenancy.

**Estimate:** 4h.

### M2-BE-10 — Tool: `send_whatsapp_reply`

**Goal:** Rosa's response gets sent back to the customer via 360dialog.

**Acceptance criteria:**
- FunctionTool taking `business_id`, `customer_phone`, `text`.
- POSTs to 360dialog using `httpx.AsyncClient` with `WHATSAPP_API_KEY` auth.
- Calls `log_conversation` with direction=outbound after a successful send.
- Wraps the network call in `try`/`except`; re-raises as `WhatsAppError`.

**Files:**
- `apps/api/app/agent/tools.py` (extend)
- `apps/api/app/integrations/whatsapp.py` (HTTP wrapper)

**Depends on:** M2-BE-09, M0-INF-04.

**Refs:** `CLAUDE.md` §Tech stack — Inbound WhatsApp.

**Estimate:** 4h.

### M2-BE-11 — Tool: `escalate_to_plumber`

**Goal:** When Rosa is unsure (gas leak, flooding, complaint), she safely escalates to Dave instead of guessing.

**Acceptance criteria:**
- FunctionTool taking `business_id`, `customer_phone`, `reason`, `urgency` ("emergency"|"unsure"|"complaint").
- Writes an escalation doc to Firestore under `/businesses/{business_id}/escalations/`.
- Sends a WhatsApp message to Dave's personal number (from business config) with customer phone and reason.
- For `urgency == "emergency"` AND the reason mentions gas → message includes "Tell the customer to call 0800 111 999 first."

**Files:**
- `apps/api/app/agent/tools.py` (extend)

**Depends on:** M2-BE-10, M1-BE-07.

**Refs:** `CLAUDE.md` §Rosa's ADK agent — "Escalation is always safe."

**Estimate:** 5h.

### M2-BE-12 — End-to-end WhatsApp booking test

**Goal:** Prove the whole loop works before declaring M2 done.

**Acceptance criteria:**
- Manual test: send a WhatsApp from a real phone to Dave's number; Rosa responds; a slot is offered; you accept; a calendar event appears in Dave's Google Calendar; a Firestore job doc exists.
- A returning customer scenario: send a second WhatsApp from the same number; Rosa references something from the first conversation.
- Test results documented in a short Loom or screenshots attached to the closing PR.

**Files:** none — verification only.

**Depends on:** M2-BE-01 through M2-BE-11.

**Refs:** `CLAUDE.md` §Hackathon submission checklist.

**Estimate:** 3h.

### M2-FE-01 — `ConversationFeed` component (real-time via VueFire)

**Goal:** The dashboard's flagship live element — Dave sees Rosa's conversations as they happen.

**Acceptance criteria:**
- `apps/web/app/components/ConversationFeed.vue` uses `useCollection` on `/businesses/{currentUser.uid}/conversations`.
- Each item shows: customer name / phone, channel badge (WhatsApp), last message preview, timestamp, status pill.
- Sorted by latest activity descending.
- Renders loading / empty / error states distinctly per `RULES.md`.
- No hardcoded `business_id` — derived from `useCurrentUser()`.

**Files:**
- `apps/web/app/components/ConversationFeed.vue`

**Depends on:** M1-FE-06.

**Refs:** `CLAUDE.md` §apps/web — Data flow. `RULES.md` §Vue / Nuxt — Data flow.

**Estimate:** 5h.

### M2-FE-02 — Conversation detail page (transcript view)

**Goal:** Click a conversation in the feed and see the full transcript with both sides.

**Acceptance criteria:**
- Route `/dashboard/conversations/[id].vue` reads the conversation doc + messages sub-collection via `useCollection`.
- Messages rendered with inbound on the left, Rosa on the right (or vice versa — pick one and document).
- Customer info card sticky at the top: name, phone, returning-customer badge.
- "Jump in" button placeholder (functionality is post-hackathon).

**Files:**
- `apps/web/app/pages/dashboard/conversations/[id].vue`

**Depends on:** M2-FE-01.

**Refs:** `CLAUDE.md` §apps/web — Pages.

**Estimate:** 5h.

### M2-FE-03 — `JobCard` component + jobs list page

**Goal:** Dave sees every booking Rosa has made.

**Acceptance criteria:**
- `apps/web/app/components/JobCard.vue` shows: customer name, address (truncated), job description, slot start/duration, status badge.
- `apps/web/app/pages/dashboard/jobs/index.vue` lists upcoming jobs sorted by slot ascending, past jobs in a collapsible section.
- VueFire `useCollection` on `/businesses/{uid}/jobs`.
- Empty state copy: warm, follows `BRANDING.md` voice.

**Files:**
- `apps/web/app/components/JobCard.vue`
- `apps/web/app/pages/dashboard/jobs/index.vue`

**Depends on:** M1-FE-06.

**Refs:** `CLAUDE.md` §apps/web — Pages.

**Estimate:** 5h.

### M2-FE-04 — Dashboard index wired to real data

**Goal:** The placeholder cards from M1-FE-07 show real numbers.

**Acceptance criteria:**
- "Today's bookings" card: live count of jobs where slot_start is today.
- "Recent conversations" card: last 5 conversations.
- "Anything urgent" card: shows escalations from the last 24h, or a calm empty state.
- All numbers driven by VueFire — no polling.

**Files:**
- `apps/web/app/pages/dashboard/index.vue`

**Depends on:** M2-FE-01, M2-FE-03.

**Refs:** `CLAUDE.md` §apps/web — Pages.

**Estimate:** 4h.

### M2-FE-05 — Loading / empty / error states pass

**Goal:** No page renders a confusing blank state or a raw error. Every page handles all four states.

**Acceptance criteria:**
- Every page using `useCollection` / `useDocument` shows a skeleton while `pending`.
- Empty state copy is friendly and on-brand.
- Errors surface via Nuxt UI's `useToast()` (not `console.error`).
- A self-review pass through every page documented in the PR description.

**Files:** touches every existing page.

**Depends on:** M2-FE-01 through M2-FE-04.

**Refs:** `RULES.md` §Errors, §Data flow.

**Estimate:** 4h.

---

## M3 — Phone channel *(cuttable)* (due 2026-06-03)

Goal: customer rings Dave's Twilio number, Rosa answers in ElevenLabs voice, books a slot. Under-3-second response budget end-to-end.

**Cut criterion:** if M2 closes more than three days late, cut M3 entirely and roll its time into M4/M5 polish. The M3 issues stay open and labelled `post-hackathon`.

### Progress

**BE (You):**
- [ ] M3-BE-01 — Twilio inbound webhook returning TwiML `<Gather>`
- [ ] M3-BE-02 — Twilio transcription webhook → Rosa with `channel="phone"`
- [ ] M3-BE-03 — Build `integrations/elevenlabs.py`
- [ ] M3-BE-04 — Stream ElevenLabs audio back through Twilio
- [ ] M3-BE-05 — Enforce phone-channel constraints in the tool wrapper
- [ ] M3-BE-06 — Latency instrumentation (p50/p95 logged)
- [ ] M3-BE-07 — Phone-channel conversations logged identically to WhatsApp
- [ ] M3-BE-08 — End-to-end phone call booking test

**FE (Dil):**
- [ ] M3-FE-01 — `ConversationFeed` renders phone conversations distinctly
- [ ] M3-FE-02 — Phone conversation detail view
- [ ] M3-FE-03 — Settings page surfaces Twilio number + voice preview

### M3-BE-01 — Twilio inbound webhook returning TwiML `<Gather>`

**Goal:** When a customer rings, Twilio gets the prompt to start speech-to-text.

**Acceptance criteria:**
- `POST /webhook/call/inbound` accepts Twilio's webhook params.
- Resolves `business_id` from `phone_numbers/{To}` Firestore lookup (per `CLAUDE.md` pattern).
- Returns TwiML `<Response><Gather input="speech" action="/webhook/call/transcribe" speechTimeout="auto"/></Response>` with a friendly opening prompt from `BRANDING.md` ("Hi! You've reached Dave's Plumbing — I'm Rosa. What can I help you with today?").
- Test by ringing the Twilio number — call connects and prompt plays.

**Files:**
- `apps/api/app/channels/phone.py`
- `apps/api/app/main.py` (route registration)

**Depends on:** M0-INF-05, M1-BE-07.

**Refs:** `CLAUDE.md` §Phone call flow, §Multi-tenancy — Twilio webhook. `BRANDING.md` §Rosa — "What Rosa sounds like."

**Estimate:** 5h.

### M3-BE-02 — Twilio transcription webhook → Rosa with `channel="phone"`

**Goal:** Customer speech → text → Rosa → text reply (audio comes in M3-BE-04).

**Acceptance criteria:**
- `POST /webhook/call/transcribe` accepts Twilio's transcription params.
- Calls `run_rosa(business_config, channel="phone", message=transcription, ...)`.
- Returns Rosa's reply text (the audio conversion happens in the next task).
- Maintains conversation continuity across multiple `<Gather>` cycles via a `CallSid`-keyed Firestore conversation doc.

**Files:**
- `apps/api/app/channels/phone.py` (extend)

**Depends on:** M3-BE-01, M2-BE-03.

**Refs:** `CLAUDE.md` §Phone call flow.

**Estimate:** 5h.

### M3-BE-03 — Build `integrations/elevenlabs.py`

**Goal:** Async text-to-speech wrapper returning audio bytes.

**Acceptance criteria:**
- `apps/api/app/integrations/elevenlabs.py` exposes `async synthesise(text: str, voice_id: str) -> bytes`.
- Strips markdown / bullet points / lists from input before sending.
- Uses streaming endpoint if available to reduce latency.
- Voice ID is resolved per-business from Firestore config, falling back to `ELEVENLABS_VOICE_ID`.
- Wrapped in try/except, raises `ElevenLabsError`.

**Files:**
- `apps/api/app/integrations/elevenlabs.py`

**Depends on:** M0-INF-06.

**Refs:** `CLAUDE.md` §Tech stack, §Phone call flow.

**Estimate:** 4h.

### M3-BE-04 — Stream ElevenLabs audio back through Twilio

**Goal:** The customer hears Rosa, not a robot.

**Acceptance criteria:**
- The transcription endpoint returns TwiML `<Response><Play>` with an audio URL or `<Stream>`, depending on what Twilio supports for this latency budget.
- The audio served has the right mime type for Twilio (`audio/mpeg` or whatever Twilio prefers).
- End-to-end: ringing the number, speaking, getting Rosa's audible reply works.

**Files:**
- `apps/api/app/channels/phone.py` (extend)

**Depends on:** M3-BE-03.

**Refs:** `CLAUDE.md` §Phone call flow.

**Estimate:** 6h.

### M3-BE-05 — Enforce phone-channel constraints in the tool wrapper

**Goal:** Rosa physically cannot generate markdown / bullet lists / >200 words on a phone call.

**Acceptance criteria:**
- A wrapper around `send_whatsapp_reply` and any future "send to channel" tool detects `channel == "phone"` and strips/truncates text.
- If Rosa generates more than 200 words for a phone reply, truncate at the nearest sentence boundary and log a warning.
- Markdown chars (`*`, `_`, `#`, bullet glyphs) stripped before ElevenLabs.

**Files:**
- `apps/api/app/agent/tools.py` (extend, add helper)

**Depends on:** M2-BE-10.

**Refs:** `CLAUDE.md` §Phone-specific constraints. `RULES.md` §Agents — phone constraints.

**Estimate:** 3h.

### M3-BE-06 — Latency instrumentation (p50/p95 logged)

**Goal:** Know whether we're hitting the 3-second budget before demo day.

**Acceptance criteria:**
- Each `/webhook/call/transcribe` request logs total elapsed time and per-step elapsed time (Rosa think time, calendar lookup, ElevenLabs synth).
- A simple `GET /admin/phone-latency` returns the last 100 calls' p50, p95, max.
- If p95 exceeds 3.5s the endpoint marks itself "over budget" in the response.

**Files:**
- `apps/api/app/channels/phone.py` (extend)
- `apps/api/app/middleware/timing.py`

**Depends on:** M3-BE-04.

**Refs:** `CLAUDE.md` §Phone call flow — "Phone-specific constraints."

**Estimate:** 4h.

### M3-BE-07 — Phone-channel conversations logged identically to WhatsApp

**Goal:** Same `log_conversation` tool, just with `channel="phone"`. Dashboard sees them in one feed.

**Acceptance criteria:**
- Every `/webhook/call/transcribe` invocation calls `log_conversation(channel="phone", ...)`.
- Phone conversations appear in `/businesses/{id}/conversations/` with `channel: "phone"`.

**Files:** none new — verification of M3-BE-02 integration.

**Depends on:** M3-BE-02, M2-BE-09.

**Refs:** `CLAUDE.md` §Phone call flow — "Rosa's agent code is channel-agnostic."

**Estimate:** 1h.

### M3-BE-08 — End-to-end phone call booking test

**Goal:** Prove the phone loop works before declaring M3 done.

**Acceptance criteria:**
- Manual test: ring the Twilio number, have a 30-second conversation with Rosa, get a slot booked.
- Calendar event present. Firestore job doc present. Conversation appears in dashboard with `channel: "phone"`.
- p95 latency from `/admin/phone-latency` is under 3.5s for the test calls.
- Test documented in the closing PR.

**Files:** none — verification only.

**Depends on:** M3-BE-01 through M3-BE-07.

**Refs:** `CLAUDE.md` §Hackathon submission checklist.

**Estimate:** 3h.

### M3-FE-01 — `ConversationFeed` renders phone conversations distinctly

**Goal:** Dave can tell at a glance whether a customer rang or messaged.

**Acceptance criteria:**
- A phone icon + "Phone call" badge replaces the WhatsApp badge for phone conversations.
- Sort order unchanged.

**Files:**
- `apps/web/app/components/ConversationFeed.vue` (extend)

**Depends on:** M2-FE-01.

**Refs:** `CLAUDE.md` §apps/web — Components.

**Estimate:** 2h.

### M3-FE-02 — Phone conversation detail view

**Goal:** The transcript view shows audio + text for phone calls.

**Acceptance criteria:**
- Phone conversation transcript shows each turn with a small play button if audio is available (post-hackathon enrichment OK).
- Total call duration shown.
- Customer info card identical to WhatsApp.

**Files:**
- `apps/web/app/pages/dashboard/conversations/[id].vue` (extend)

**Depends on:** M2-FE-02.

**Refs:** `CLAUDE.md` §apps/web — Pages.

**Estimate:** 3h.

### M3-FE-03 — Settings page surfaces Twilio number + voice preview

**Goal:** Dave can see what number customers call and hear Rosa's voice.

**Acceptance criteria:**
- `/dashboard/settings` shows the Twilio number from `/businesses/{uid}/config.twilio_number`.
- "Preview Rosa's voice" button POSTs to an API endpoint that returns a short audio sample.
- Audio plays inline.

**Files:**
- `apps/web/app/pages/dashboard/settings.vue`

**Depends on:** M1-FE-06.

**Refs:** `BRANDING.md` §Rosa.

**Estimate:** 4h.

---

## M4 — Dashboard + onboarding (due 2026-06-05)

Goal: a new plumber can sign up, fill in an onboarding form, and have Rosa live for their customers within 5 minutes. Dave can search his whole job history in plain English.

### Progress

**BE (You):**
- [ ] M4-BE-01 — `/onboard` endpoint (atomic tenant creation)
- [ ] M4-BE-02 — `/business/{id}` GET + PATCH
- [ ] M4-BE-03 — `/jobs/search` endpoint (semantic Elastic query)
- [ ] M4-BE-04 — `/conversations` list + detail endpoints

**FE (Dil):**
- [ ] M4-FE-01 — `OnboardingForm` step 1 (business details)
- [ ] M4-FE-02 — `OnboardingForm` step 2 (WhatsApp / Twilio connect)
- [ ] M4-FE-03 — `OnboardingForm` step 3 (Calendar / hours / pricing)
- [ ] M4-FE-04 — Onboarding flow polish (validation, save-as-you-go, progress)
- [ ] M4-FE-05 — Settings page editable
- [ ] M4-FE-06 — Job search UI
- [ ] M4-FE-07 — Mobile responsive pass

### M4-BE-01 — `/onboard` endpoint (atomic tenant creation)

**Goal:** One request creates a complete tenant — Auth user, Firestore docs, phone/whatsapp mappings, Elastic business config. All-or-nothing.

**Acceptance criteria:**
- `POST /onboard` accepts a `BusinessOnboardingRequest` Pydantic model (business name, owner name, address, hours, base prices, etc.).
- Requires a valid Firebase ID token; `business_id` = the verified `uid`.
- In sequence with compensation on failure:
  1. Write `/businesses/{uid}/config` doc.
  2. Write `/phone_numbers/{twilio_number}` → `{business_id: uid}` mapping (if Twilio number assigned).
  3. Write `/whatsapp_numbers/{wa_id}` → `{business_id: uid}` mapping.
  4. Index a `doc_type: business_config` document in `rosa-customers`.
- Returns the created business config.
- If any step fails, previously-written docs are deleted before raising.

**Files:**
- `apps/api/app/main.py` (route)
- `apps/api/app/models/onboarding.py`
- `apps/api/app/services/onboarding.py`

**Depends on:** M1-BE-02, M1-BE-05, M1-BE-07.

**Refs:** `CLAUDE.md` §Multi-tenancy — Onboarding.

**Estimate:** 7h.

### M4-BE-02 — `/business/{id}` GET + PATCH

**Goal:** Dave can read and update his business config.

**Acceptance criteria:**
- `GET /business/{business_id}` returns the `Business` Pydantic model.
- `PATCH /business/{business_id}` updates fields and re-indexes the Elastic `business_config` doc.
- Both require `verify_firebase_token`; assert `uid == business_id` else `403`.

**Files:**
- `apps/api/app/main.py`
- `apps/api/app/services/business.py`

**Depends on:** M4-BE-01.

**Refs:** `CLAUDE.md` §Routes, §Multi-tenancy.

**Estimate:** 4h.

### M4-BE-03 — `/jobs/search` endpoint (semantic Elastic query)

**Goal:** Dave types "leaky boiler in March" and gets the right jobs back. The headline Elastic demo.

**Acceptance criteria:**
- `POST /jobs/search` accepts `{ "query": "..." }`.
- Builds a semantic search against `rosa-jobs` combining keyword + vector similarity on the `description_embedding` field.
- All queries go through `build_query(business_id, ...)`.
- Returns up to 20 jobs ranked by relevance.
- Latency under 500ms p95 on a corpus of 1000 seeded jobs.

**Files:**
- `apps/api/app/main.py`
- `apps/api/app/services/search.py`

**Depends on:** M1-BE-05, M1-BE-06.

**Refs:** `CLAUDE.md` §Hackathon submission checklist — "Dave can search jobs in plain English via Elastic."

**Estimate:** 6h.

### M4-BE-04 — `/conversations` list + detail endpoints

**Goal:** Server-side conversation queries for the dashboard (Firestore handles live updates, this handles search/filter).

**Acceptance criteria:**
- `GET /conversations?channel=&status=&q=` returns paginated conversation summaries from Elastic.
- `GET /conversations/{conversation_id}` returns the full conversation doc + messages.
- All scoped by `business_id` via `build_query`.

**Files:**
- `apps/api/app/main.py`
- `apps/api/app/services/conversations.py`

**Depends on:** M2-BE-09.

**Refs:** `CLAUDE.md` §Routes.

**Estimate:** 4h.

### M4-FE-01 — `OnboardingForm` step 1 (business details)

**Goal:** First step of the wizard — who is this business?

**Acceptance criteria:**
- Fields: business name, owner name, business address, service area (postcode list or radius from postcode).
- Validation: required fields, postcode format.
- Progress bar shows step 1 of 3.
- Submit advances to step 2; state survives a page refresh (localStorage or signed-in user draft doc).
- Copy follows `BRANDING.md` voice.

**Files:**
- `apps/web/app/components/onboarding/StepBusinessDetails.vue`
- `apps/web/app/pages/onboarding/index.vue`

**Depends on:** M1-FE-06.

**Refs:** `CLAUDE.md` §apps/web — Pages, Onboarding. `BRANDING.md` §Voice and tone.

**Estimate:** 5h.

### M4-FE-02 — `OnboardingForm` step 2 (WhatsApp / Twilio connect)

**Goal:** Hook the plumber's WhatsApp and (optionally) Twilio numbers up to Rosa.

**Acceptance criteria:**
- WhatsApp section: pasted `phone_number_id` + 360dialog API key (validated against 360dialog).
- Twilio section: dropdown of available numbers (or paste-in for now).
- Both clearly marked optional vs required.

**Files:**
- `apps/web/app/components/onboarding/StepChannels.vue`

**Depends on:** M4-FE-01.

**Refs:** `CLAUDE.md` §Multi-tenancy — Onboarding.

**Estimate:** 5h.

### M4-FE-03 — `OnboardingForm` step 3 (Calendar / hours / pricing)

**Goal:** Last step — calendar connect (via service account share), working hours, base prices. Full Google Calendar OAuth is deferred to post-hackathon.

**Acceptance criteria:**
- Calendar section presents a two-step inline guide:
  1. "Share your calendar with `rosa-service@<project>.iam.gserviceaccount.com`" — show the email with a "Copy" button, link to Google's "share a calendar" docs.
  2. "Paste your Calendar ID here" — input field for the calendar ID (looks like an email), validated client-side as an email-shaped string.
- The service-account email is read from runtime config so it's correct in dev and prod.
- Working hours grid (mon–sun, start/end times, "closed" toggle per day).
- Base prices: simple list of `{job type, price}` rows with add/remove.
- On submit, POSTs to `/onboard` and redirects to `/dashboard` on success.
- A clear note explains "We use a single service account to write to your calendar — proper Google sign-in is coming soon." Tone follows `BRANDING.md`.

**Files:**
- `apps/web/app/components/onboarding/StepCalendarHoursPricing.vue`

**Depends on:** M4-FE-02, M4-BE-01.

**Refs:** `CLAUDE.md` §apps/web — Pages. `RULES.md` §Integrations — Calendar credentials. `BRANDING.md` §Voice and tone.

**Estimate:** 5h.

### M4-FE-04 — Onboarding flow polish (validation, save-as-you-go, progress)

**Goal:** The first 5 minutes of being a customer feel competent and warm.

**Acceptance criteria:**
- Every required field validated before "Next" is enabled.
- Form state saved on every blur (localStorage or `/onboarding/draft`).
- Progress bar animated between steps.
- Copy reviewed against `BRANDING.md` and any AI-isms removed.

**Files:** touches step components.

**Depends on:** M4-FE-01, M4-FE-02, M4-FE-03.

**Refs:** `BRANDING.md` §Voice and tone.

**Estimate:** 4h.

### M4-FE-05 — Settings page editable

**Goal:** Dave can change anything from onboarding without re-doing onboarding.

**Acceptance criteria:**
- `/dashboard/settings` renders the same fields as onboarding but pre-populated from `/business/{id}`.
- Save button PATCHes the business doc and shows a toast on success.

**Files:**
- `apps/web/app/pages/dashboard/settings.vue` (extend M3-FE-03)

**Depends on:** M4-BE-02.

**Refs:** `CLAUDE.md` §apps/web — Pages.

**Estimate:** 4h.

### M4-FE-06 — Job search UI

**Goal:** The Elastic demo moment. Plain-English search bar that just works.

**Acceptance criteria:**
- `/dashboard/jobs` has a prominent search bar at the top.
- Typing posts to `/jobs/search` with debounce.
- Results render as `JobCard`s ranked by relevance.
- Empty/loading/error states handled.
- "Cleared" state shows the upcoming-jobs list (default from M2-FE-03).

**Files:**
- `apps/web/app/pages/dashboard/jobs/index.vue` (extend)

**Depends on:** M2-FE-03, M4-BE-03.

**Refs:** `CLAUDE.md` §Hackathon submission checklist.

**Estimate:** 5h.

### M4-FE-07 — Mobile responsive pass

**Goal:** Dave reads the dashboard in his van. The phone view has to work.

**Acceptance criteria:**
- Every dashboard page renders without horizontal scroll at 360px width.
- Side nav collapses to a bottom bar or drawer on small screens.
- Tap targets are at least 44px tall.
- Tested in Chrome devtools mobile mode and on a real iOS Safari if available.

**Files:** touches every page.

**Depends on:** M2-FE-04, M4-FE-05, M4-FE-06.

**Refs:** `BRANDING.md` §Audience — Dave reads the dashboard in his van.

**Estimate:** 5h.

---

## M5 — Polish (due 2026-06-08)

Goal: the product is ready to submit. Everything works under stress, looks good, and the Elastic demo lands. No Dynatrace work in this phase — we cut it.

### Progress

**BE (You):**
- [ ] M5-BE-01 — Error handling pass across every external call
- [ ] M5-BE-02 — Multi-tenancy security review
- [ ] M5-BE-03 — Load test — 5 concurrent WhatsApp conversations

**FE (Dil):**
- [ ] M5-FE-01 — Landing page (`/`) on-brand
- [ ] M5-FE-02 — Visual polish pass (typography, spacing, micro-interactions)
- [ ] M5-FE-03 — 404 + error pages on-brand
- [ ] M5-FE-04 — Accessibility pass

### M5-BE-01 — Error handling pass across every external call

**Goal:** No exception escapes without context. Conversations don't die silently when ElevenLabs hiccups.

**Acceptance criteria:**
- Every call to Elastic, Calendar, Twilio, ElevenLabs, 360dialog, Firebase is in a `try/except` that re-raises with context via `from err`.
- Errors that affect a conversation write a `status: "error"` field + an `error: {code, message, at}` map to the conversation Firestore doc.
- No bare `except Exception:` exists anywhere in `apps/api/app/`.
- Self-review documented in PR.

**Files:** touches `integrations/*.py`, `agent/tools.py`, `channels/*.py`.

**Depends on:** M2, M3 (if not cut), M4.

**Refs:** `RULES.md` §Errors.

**Estimate:** 5h.

### M5-BE-02 — Multi-tenancy security review

**Goal:** Try to break the tenant boundary. If it bends, fix it before judges find it.

**Acceptance criteria:**
- A scripted test attempts: read Pete's data with Dave's token via every protected endpoint; webhook with Pete's `business_id` in body; phone-number lookup spoofing.
- Every attempt fails with `403`/`404` and no data leak.
- Findings + fixes documented in `docs/security-review.md`.

**Files:**
- `apps/api/tests/test_tenancy_e2e.py`
- `docs/security-review.md`

**Depends on:** all M1–M4 BE work.

**Refs:** `CLAUDE.md` §Multi-tenancy — Checklist. `RULES.md` §Multi-tenancy.

**Estimate:** 6h.

### M5-BE-03 — Load test — 5 concurrent WhatsApp conversations

**Goal:** Five plumbers, five customers, no crossed wires. Verifies tenancy under load.

**Acceptance criteria:**
- Test script fires 5 parallel WhatsApp webhook calls from 5 different `business_id`s.
- Each booking lands in the right calendar and the right Firestore tenant.
- No cross-contamination observed in Elastic queries or dashboard feeds.

**Files:**
- `apps/api/tests/load_test.py`

**Depends on:** M5-BE-02.

**Refs:** `CLAUDE.md` §Multi-tenancy.

**Estimate:** 4h.

### M5-FE-01 — Landing page (`/`) on-brand

**Goal:** First impression for hackathon judges and any organic visitors.

**Acceptance criteria:**
- Hero: "Never miss another call." Sub-headline emphasising the time-and-money value prop, not technology.
- 3 value props with abstract illustration placeholders (per `BRANDING.md` §Illustration style).
- CTA to onboarding.
- "Powered by [Platform]" footer with the name placeholder.
- No "AI" mentions anywhere.

**Files:**
- `apps/web/app/pages/index.vue`

**Depends on:** M1-FE-04, M1-FE-05.

**Refs:** `BRANDING.md` (entirely).

**Estimate:** 6h.

### M5-FE-02 — Visual polish pass

**Goal:** The dashboard goes from "functional" to "feels like a real product".

**Acceptance criteria:**
- Typography hierarchy reviewed across every page against the type scale in `BRANDING.md`.
- Spacing rhythm consistent (4/8/16/24/32px scale).
- Hover states on every interactive element.
- Coral accent used sparingly (CTAs, notification badges) per the colour principles.
- No pure black / pure white anywhere.

**Files:** touches components broadly.

**Depends on:** M2, M4 FE.

**Refs:** `BRANDING.md` §Visual identity, §Colour principles.

**Estimate:** 6h.

### M5-FE-03 — 404 + error pages on-brand

**Goal:** Even the dead ends feel warm.

**Acceptance criteria:**
- `error.vue` at the Nuxt root handles all unhandled errors with on-brand copy.
- 404 copy: warm, no "AI", under 30 words, has a way back home.
- 500 copy: "Something went wrong on our end..." per `BRANDING.md` §Copy examples.

**Files:**
- `apps/web/app/error.vue`

**Depends on:** M1-FE-04.

**Refs:** `BRANDING.md` §Copy examples.

**Estimate:** 2h.

### M5-FE-04 — Accessibility pass

**Goal:** Keyboard-only navigation works. Screen readers don't trip. Contrast holds.

**Acceptance criteria:**
- Tab through every page — focus order makes sense, focus rings visible against the brand palette.
- Every form field has a label.
- ARIA labels on icon-only buttons.
- Contrast checked: body text on Warm Off-White meets WCAG AA.
- Lighthouse accessibility score ≥ 90 on `/dashboard` and `/`.

**Files:** touches components broadly.

**Depends on:** M5-FE-02.

**Refs:** `BRANDING.md` §Visual identity.

**Estimate:** 5h.

---

## M6 — Submission (due 2026-06-11)

Goal: deployed, recorded, submitted. Single track: **Elastic**.

### Progress

- [ ] M6-SH-01 — Deploy `apps/api` to Cloud Run production
- [ ] M6-SH-02 — Deploy `apps/web` (target TBD — Firebase Hosting / Cloud Run / Vercel)
- [ ] M6-SH-03 — Production smoke test
- [ ] M6-SH-04 — Record 3-minute demo video
- [ ] M6-SH-05 — Rewrite `README.md` as the Orchestra / Rosa intro
- [ ] M6-SH-06 — Submit to Elastic partner track
- [ ] M6-SH-07 — Final repo sweep — no secrets, README current, license correct

### M6-SH-01 — Deploy `apps/api` to Cloud Run production

**Owner:** BE (You).

**Goal:** A real production URL serving Rosa with real secrets. Also the moment we provision the prod tenant credentials we deferred in M0.

**Acceptance criteria:**
- A `orchestra-prod` GCP project + Firebase project exist alongside `orchestra-dev`.
- A prod Twilio number purchased (separate from the dev number).
- All prod-tier credentials stored in Secret Manager under `orchestra-prod`.
- Cloud Run service `rosa-api-prod` deployed in `europe-west2` against `orchestra-prod`.
- Env vars sourced from Secret Manager (no plaintext).
- Custom domain (`api.<orchestra-domain>` or a Cloud Run default URL — domain decision in M6-SH-05).
- 360dialog and Twilio webhooks updated to point at the production URL.

**Files:** Cloud Run + DNS config — no code.

**Depends on:** M5 BE complete.

**Refs:** `CLAUDE.md` §Tech stack.

**Estimate:** 6h (includes prod tenant provisioning).

### M6-SH-02 — Deploy `apps/web` to Cloud Run

**Owner:** FE (Dil).

**Goal:** A real production URL hosting the dashboard.

**Acceptance criteria:**
- Nuxt 3 production build containerised (`apps/web/Dockerfile`).
- Cloud Run service `rosa-web-prod` deployed in `europe-west2`.
- Public env vars (`FIREBASE_*`, `API_BASE_URL`) injected via Cloud Run config; sensitive vars from Secret Manager.
- Custom domain configured if available.
- Connects to the production Firebase project and the M6-SH-01 API.
- Same region as the API to keep latency low for the demo.

**Files:**
- `apps/web/Dockerfile`
- `apps/web/.dockerignore`

**Depends on:** M5 FE complete, M6-SH-01.

**Refs:** `CLAUDE.md` §Tech stack — Hosting on Cloud Run.

**Estimate:** 5h.

### M6-SH-03 — Production smoke test

**Owner:** Shared.

**Goal:** Verify everything works in prod before we record the demo.

**Acceptance criteria:**
- Send a real WhatsApp from your own phone — Rosa books a slot.
- Ring the Twilio number (if M3 shipped) — Rosa books a slot.
- Dashboard updates live.
- Job search returns sensible results.
- No errors in Cloud Run logs.

**Files:** none — verification.

**Depends on:** M6-SH-01, M6-SH-02.

**Refs:** `CLAUDE.md` §Hackathon submission checklist.

**Estimate:** 3h.

### M6-SH-04 — Record 3-minute demo video

**Owner:** Shared.

**Goal:** The submission video. This is what the judges actually watch.

**Acceptance criteria:**
- Under 3 minutes.
- Shows: (1) Dave's onboarding (under 30s), (2) a customer WhatsApping in and getting booked, (3) the dashboard updating live, (4) Dave searching jobs in plain English — Elastic showcased explicitly.
- (Optional) phone call demo if M3 shipped.
- Voiceover follows `BRANDING.md` voice — warm, no "AI", contractions.
- Hosted on YouTube or Loom, public link.

**Files:** none — external artefact.

**Depends on:** M6-SH-03.

**Refs:** `CLAUDE.md` §Hackathon submission checklist. `BRANDING.md` §Voice and tone.

**Estimate:** 5h.

### M6-SH-05 — Rewrite `README.md` as the Orchestra / Rosa intro

**Owner:** BE (You).

**Goal:** Replace the Nuxt-starter boilerplate. Judges will read this.

**Acceptance criteria:**
- Title is "Rosa" or "Orchestra" (decision pending — see Open questions).
- Hero copy from `BRANDING.md`.
- Architecture diagram (mermaid).
- Quick-start for local dev.
- Demo link (M6-SH-04).
- Hackathon track: Elastic.
- Links to `CLAUDE.md`, `RULES.md`, `BRANDING.md`, `CONTRIBUTING.md`, `PLAN.md`.

**Files:**
- `README.md`

**Depends on:** M6-SH-04.

**Refs:** `BRANDING.md`, `CLAUDE.md`.

**Estimate:** 3h.

### M6-SH-06 — Submit to Elastic partner track

**Owner:** BE (You).

**Goal:** The whole point.

**Acceptance criteria:**
- Submission form completed.
- Repo URL, demo video URL, written description provided.
- Submitted at least 24 hours before the 2026-06-11 deadline.

**Files:** none.

**Depends on:** M6-SH-04, M6-SH-05.

**Refs:** `CLAUDE.md` §Hackathon submission checklist.

**Estimate:** 2h.

### M6-SH-07 — Final repo sweep

**Owner:** Shared.

**Goal:** Nothing embarrassing in the public repo.

**Acceptance criteria:**
- `git log -p` searched for `.env`, API keys, tokens — none present.
- All open PRs merged or closed.
- All M1–M6 milestone issues closed or moved to `post-hackathon`.
- LICENSE correct (Isaac Dolphin 2026).
- No `[Platform]` placeholders left in user-facing copy (or a clear note that the name is TBD).

**Files:** none — audit.

**Depends on:** M6-SH-06.

**Refs:** `RULES.md` §Universal — "Secrets never appear in code."

**Estimate:** 2h.

---

## Critical path and parallelism notes

- **M0 blocks everything BE.** Without credentials, M1-BE can't start meaningfully. Do M0 first; don't try to parallelise.
- **M1 FE and M1 BE run in parallel** once M0-INF-02 is done. Dil reads Firestore via VueFire directly — he doesn't need your endpoints to build the app shell.
- **M2 BE has a long internal sequence** (M2-BE-01 → 02 → ... → 12) because the tools depend on each other. M2 FE can start as soon as M2-BE-09 (`log_conversation`) writes real Firestore docs.
- **M3 can run in parallel with M4** if BE/FE capacity allows. If not, do M3 first since its cut decision affects M4/M5 scope.
- **M5 BE is largely cleanup** — can be done in the gaps while waiting on M4 FE.
- **M6 is mostly serial.** Deploy → smoke test → record → submit. Don't try to record the demo before the smoke test passes.

---

## Open questions

### Resolved

- ~~**Deploy target for `apps/web`?**~~ → **Cloud Run** in `europe-west2`, matching the API. Nuxt SSR in a container.
- ~~**Dev environment strategy?**~~ → **Dev tenant** for the build (separate Firebase project + Twilio number; shared Elastic deployment with `dev-` index prefix). Prod tenant provisioning rolled into M6-SH-01.
- ~~**Google Calendar OAuth vs service-account in M4-FE-03?**~~ → **Calendar ID paste + share-with-service-account.** Two-step inline guide in onboarding. Full OAuth is post-hackathon.

### Still open

1. **Dil's GitHub handle?** Needed to assign FE issues when filing.
2. **Platform name** — skipped for now per your call. `BRANDING.md` keeps the `[Platform]` placeholder until we decide.
