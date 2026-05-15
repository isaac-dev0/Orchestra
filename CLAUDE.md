# CLAUDE.md — Rosa Project Bible

This file is read by AI coding assistants (Claude, Gemini CLI, Copilot) to understand
the project before touching any code. Read this fully before making any changes.

---

## Working rules — read before every change

- **Always consult `RULES.md`** before making any code change. It is the source of truth
  for how work gets done in this repo. If a rule there conflicts with anything in this file,
  RULES.md wins for process; CLAUDE.md wins for architecture.
- **Always consult `BRANDING.md`** whenever changes touch user-facing surfaces — Nuxt pages
  and components, copy, voice/tone of Rosa's responses, prompts, marketing text, colours,
  typography, logos, or any visual asset. If the change is purely backend plumbing with no
  user-visible output, BRANDING.md can be skipped.
- **Always ask clarifying questions before implementing.** If any part of the request is
  ambiguous — scope, file location, naming, behaviour on edge cases, which of two valid
  approaches to take — pause and ask. Do not guess. One round of questions up front is
  cheaper than a wrong implementation. Only skip the questions if the request is genuinely
  unambiguous (e.g. "fix this typo on line 42").

---

## What we're building

**Rosa** is an AI receptionist for plumbers. She answers WhatsApp messages and phone calls,
qualifies jobs, books appointments into Google Calendar, remembers every customer, and
escalates emergencies to the plumber.

Rosa is the first product of a wider **AI staff agency** (name TBD) — businesses
rent agents that think, remember, and act like real members of staff. The wider
roster comes later. Right now: Rosa, plumbers, ship it.

(For positioning, voice, and customer-facing framing, see `BRANDING.md`. We are
a staffing agency that happens to run on software, not an "AI platform".)

Rosa is being submitted to the **Google Cloud Rapid Agent Hackathon** (deadline June 11, 2026)
under the **Elastic** and **Dynatrace** partner tracks.

---

## Monorepo structure (Turborepo)

```
/
├── apps/
│   ├── api/          # FastAPI — Rosa's backend, agent entrypoint, webhooks
│   └── web/          # Nuxt 3 — Dave's dashboard, onboarding form
├── packages/
│   └── shared/       # Shared types, constants (add as needed)
├── CLAUDE.md         # This file
├── branding.md       # Brand decisions
└── turbo.json
```

---

## Tech stack — exactly this, nothing else

| Layer | Technology | Why |
|---|---|---|
| Agent brain | Google ADK + Gemini 2.0 Flash → Agent Engine | Required for hackathon |
| Inbound phone | Twilio Voice + STT | Answers calls, speech → text |
| Voice output | ElevenLabs TTS | Natural voice for phone calls |
| Inbound WhatsApp | 360dialog webhook | Customers text Dave's number |
| Calendar | Google Calendar Python SDK | Direct, no middleware |
| Memory + search | Elasticsearch via Elastic MCP server | Customer history, job log, semantic search |
| Observability | Dynatrace via OpenTelemetry (OTLP) | Traces, token spend, latency |
| Frontend | Nuxt 3 + Nuxt UI + Tailwind | Dave's dashboard + onboarding |
| Auth + accounts | Firebase Auth | Dave's login, Google OAuth, session management |
| Business data | Firestore | Per-business config, real-time conversation feed |
| Hosting | GCP Cloud Run + Agent Engine | Scale to zero, parallel calls |
| Secrets | GCP Secret Manager | All API keys |

### What we are NOT using (and why)

- **n8n / Zapier / Make** — not needed yet. Three integrations, all have Python SDKs.
  Add when marketplace customers bring their own tools. Not before.
- **LangChain / LlamaIndex** — ADK is sufficient. Don't add framework complexity.
- **Separate Express/Node backend** — FastAPI handles everything server-side.
- **Stripe** — post-hackathon. Not needed for the demo.
- **Supabase** — replaced by Firebase. Everything stays in GCP. Don't reintroduce it.
- **Docker Compose locally** — keep it simple. Run services individually.

---

## apps/api — FastAPI service

### Purpose
- Receives inbound messages (WhatsApp webhook, Twilio call webhook)
- Loads the plumber's business config from Elastic
- Runs Rosa's ADK agent
- Returns responses back to the right channel
- Exposes onboarding endpoint called by Nuxt

### Key files (build in this order)
```
apps/api/
├── main.py                  # FastAPI app, routes
├── agent/
│   ├── rosa.py              # ADK LlmAgent definition
│   ├── prompts.py           # System prompt template + builder
│   └── tools.py             # FunctionTools: calendar, elastic, escalate
├── channels/
│   ├── whatsapp.py          # 360dialog webhook handler
│   └── phone.py             # Twilio + ElevenLabs call handler
├── integrations/
│   ├── calendar.py          # Google Calendar SDK wrapper
│   ├── elastic.py           # Elasticsearch client + query helpers
│   └── firebase.py          # Firebase Admin SDK — auth verification, Firestore writes
├── config/
│   ├── settings.py          # Pydantic settings from env vars
│   └── elastic_setup.py     # One-time index creation script
├── requirements.txt
├── Dockerfile
└── .env.example
```

### Routes
```
GET  /health                  # Health check
POST /webhook/whatsapp        # 360dialog inbound message
POST /webhook/call/inbound    # Twilio inbound call (returns TwiML)
POST /webhook/call/transcribe # Twilio transcription → Rosa → ElevenLabs
POST /onboard                 # Called by Nuxt onboarding form
GET  /business/{business_id}  # Load business config (internal)
```

### Environment variables (all required)
```bash
GCP_PROJECT_ID=
GCP_REGION=europe-west2

GEMINI_MODEL=gemini-2.0-flash

ELASTIC_MCP_URL=
ELASTIC_API_KEY=
ELASTIC_CLOUD_ID=            

DYNATRACE_ENDPOINT=         
DYNATRACE_API_TOKEN=

TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=        

WHATSAPP_API_KEY=
WHATSAPP_PHONE_NUMBER_ID=

GOOGLE_CALENDAR_ID=          
GOOGLE_SERVICE_ACCOUNT_JSON= 

FIREBASE_PROJECT_ID=                
GOOGLE_APPLICATION_CREDENTIALS=      
```

### Rosa's ADK agent — key design decisions

**System prompt is per-customer.** Rosa's prompt is a template with `{placeholders}` filled
from each plumber's Elastic config doc at runtime. Same agent code, different personality
per customer.

**Two-tier Gemini calls:**
- Intent classification: Gemini Flash (fast, cheap) — "is this an emergency?"
- Full Rosa response: Gemini Flash (still fast enough for phone calls)

**Memory is Elastic, not ADK's built-in Memory Bank.** We bypass Agent Engine's memory
deliberately — Elastic gives us searchable, auditable, hackathon-demo-able history.
This is an intentional architectural choice, mention it in the demo.

**Phone call constraint:** Rosa must respond in under 3 seconds on a live call.
Keep tool calls lean. Don't chain more than 2 tools on a phone response.

**Escalation is always safe.** When Rosa is unsure, she escalates. Never guess on:
- Gas smells / suspected leaks → tell customer to call 0800 111 999 first
- Flooding / burst pipes → escalate immediately
- Complaints about past work → escalate immediately

---

## apps/web — Nuxt 3 dashboard

### Purpose
Dave's interface. He sees every conversation Rosa has had, every booking made,
and can configure Rosa or jump into a conversation.

### Key pages (build in this order)
```
apps/web/
├── pages/
│   ├── index.vue            # Landing / marketing page
│   ├── onboarding/
│   │   └── index.vue        # Setup form (step 1 of product)
│   ├── dashboard/
│   │   ├── index.vue        # Overview: today's bookings, recent convos
│   │   ├── conversations/
│   │   │   └── index.vue    # Full conversation log
│   │   └── jobs/
│   │       └── index.vue    # Job log with Elastic search
│   └── settings/
│       └── index.vue        # Business config, WhatsApp, calendar
├── components/
│   ├── ConversationFeed.vue  # Real-time conversation list
│   ├── JobCard.vue           # Single booking card
│   └── OnboardingForm.vue    # Multi-step onboarding
├── composables/
│   └── useRosa.ts            # API calls to FastAPI
└── nuxt.config.ts
```

### Nuxt config requirements
```ts
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@nuxt/ui', 'nuxt-vuefire'],
  vuefire: {
    auth: { enabled: true },
    config: {
      apiKey: process.env.FIREBASE_API_KEY,
      authDomain: process.env.FIREBASE_AUTH_DOMAIN,
      projectId: process.env.FIREBASE_PROJECT_ID,
    }
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.API_BASE_URL  // FastAPI URL
    }
  }
})
```

### Data flow
- Onboarding form → POST to FastAPI `/onboard` → seeds Elastic + writes Firestore business doc
- Dashboard data → Nuxt composables → Firestore direct (for real-time) + FastAPI (for Elastic queries)
- Real-time conversation updates → Firestore `onSnapshot` on `/businesses/{id}/conversations`
- Auth → Firebase Auth (Google OAuth — one click for Dave, no password to forget)

---

## Multi-tenancy — the rules

Rosa serves multiple plumbing businesses simultaneously. Dave's data must never
be visible to Pete. These rules are non-negotiable and must be applied everywhere.

### The golden rule
**Every data operation is scoped to a `business_id`. Always. No exceptions.**

`business_id` is the Firebase Auth UID of the business owner. It is set at signup
and never changes. It is the single source of truth for tenancy.

### How tenancy works per layer

**Firebase Auth**
- One account per plumbing business (not per end-customer)
- Dave logs into the Nuxt dashboard with his Google account
- Firebase Auth UID becomes his `business_id` for everything

**Firestore — tenant isolation is structural**
```
/businesses/{business_id}/                  ← Dave can only read his own document
    config          (document)              ← business name, pricing, service area etc.
    conversations/  (collection)            ← every Rosa conversation
        {conversation_id}  (document)
    jobs/           (collection)            ← every booking Rosa made
        {job_id}    (document)
    customers/      (collection)            ← per-customer memory Rosa has built up
        {customer_phone}  (document)
```

Firestore Security Rules enforce this at the database level:
```javascript
// firestore.rules — Dave literally cannot read Pete's data
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /businesses/{businessId}/{document=**} {
      allow read, write: if request.auth != null
                         && request.auth.uid == businessId;
    }
  }
}
```

**Elasticsearch — tenant isolation is enforced in code**

Firestore handles auth natively. Elastic doesn't. So every single Elastic query
MUST go through the `build_query()` helper in `integrations/elastic.py`.
This function hardcodes the `business_id` filter — it cannot be bypassed.

```python
# integrations/elastic.py
# NEVER query Elastic directly. Always use this.
def build_query(business_id: str, query: dict) -> dict:
    """
    Wraps any Elastic query with a mandatory business_id filter.
    This is the multi-tenancy enforcement layer for Elasticsearch.
    If you are writing a raw ES query anywhere else, you are doing it wrong.
    """
    return {
        "query": {
            "bool": {
                "must": [query],
                "filter": [{"term": {"business_id": business_id}}]
            }
        }
    }
```

**FastAPI — business_id comes from the verified Firebase token**

The API never trusts a `business_id` passed in the request body.
It always extracts it from the verified Firebase ID token in the Authorization header.

```python
# Every protected route does this — never trust client-provided business_id
async def get_current_business(
    authorization: str = Header(...),
    firebase_admin = Depends(get_firebase_admin)
) -> str:
    token = authorization.replace("Bearer ", "")
    decoded = firebase_admin.auth.verify_id_token(token)
    return decoded["uid"]  # This is the business_id. Authoritative.
```

**Twilio webhook — business_id comes from the called phone number**

When a customer rings, Twilio tells us which number they called (`To` field).
That number maps to a `business_id` in Firestore. Look it up, never trust the caller.

```python
# channels/phone.py
async def resolve_business_from_twilio(to_number: str) -> str:
    # Firestore: /phone_numbers/{to_number} → { business_id: "..." }
    doc = await firestore.collection("phone_numbers").document(to_number).get()
    if not doc.exists:
        raise HTTPException(404, f"No business registered for {to_number}")
    return doc.to_dict()["business_id"]
```

**360dialog WhatsApp webhook — same pattern**

The WhatsApp phone number ID maps to a `business_id` in Firestore.
Seeded at onboarding. Never trust anything the webhook body claims about identity.

### Onboarding creates the tenant

When Dave completes the onboarding form, this happens atomically:

```
1. Firebase Auth creates Dave's account → generates business_id (UID)
2. Firestore: /businesses/{business_id}/config document created
3. Firestore: /phone_numbers/{twilio_number} → { business_id } mapping created
4. Firestore: /whatsapp_numbers/{wa_number_id} → { business_id } mapping created
5. Elastic: business config doc written to rosa-customers index
6. Rosa is live for Dave's customers
```

### What "Rosa for Dave" looks like at runtime

```
Customer rings +447700 000001 (Dave's Twilio number)
  → Twilio webhook fires
  → FastAPI looks up +447700 000001 in Firestore → business_id = "daves-plumbing-uid"
  → Loads /businesses/daves-plumbing-uid/config from Firestore
  → Builds Rosa's system prompt with Dave's business details
  → All Elastic queries filtered to business_id = "daves-plumbing-uid"
  → Booking written to /businesses/daves-plumbing-uid/jobs/
  → Dave sees it instantly in his dashboard via onSnapshot
  → Pete sees nothing. His data is in /businesses/petes-plumbing-uid/
```

### Checklist — before shipping any new feature

- [ ] Does it extract `business_id` from Firebase token (API) or Firestore phone lookup (webhooks)?
- [ ] Does every Elastic query go through `build_query(business_id, ...)`?
- [ ] Does every Firestore read/write use `/businesses/{business_id}/...`?
- [ ] Are Firestore Security Rules still enforcing tenant isolation?
- [ ] Could a crafted request from Pete access Dave's data? If yes, fix it first.

---



Three indices. Run `python -m config.elastic_setup` once to create them.

| Index | Purpose |
|---|---|
| `rosa-conversations` | Every message in/out, full audit trail |
| `rosa-jobs` | Every booking: customer, address, job type, slot, status |
| `rosa-customers` | Per-customer memory + plumber business configs |

Business configs are stored in `rosa-customers` as docs with `doc_type: "business_config"`.
Customer memory docs have `doc_type: "customer"`. Filter by `doc_type` in all queries.

---

## Phone call flow (important — read before touching phone.py)

```
1. Customer rings Twilio number
2. Twilio webhook → POST /webhook/call/inbound
3. FastAPI returns TwiML: <Gather input="speech" action="/webhook/call/transcribe">
4. Customer speaks
5. Twilio STT → POST /webhook/call/transcribe with transcription
6. FastAPI → Rosa agent (same as WhatsApp, channel="phone")
7. Rosa responds with text
8. FastAPI → ElevenLabs API → audio bytes
9. FastAPI streams audio back to Twilio
10. Twilio plays audio to caller
11. Loop back to step 3 until conversation ends
```

Rosa's agent code is **channel-agnostic**. The channel ("whatsapp" or "phone") is
passed as metadata. Same memory, same tools, same booking logic.

**Phone-specific constraints:**
- Response must be under 200 words (it gets read aloud)
- No markdown, no bullet points, no lists in phone responses
- Strip all formatting before sending to ElevenLabs
- Include `channel="phone"` in the Rosa call so she adjusts her style

---

## Dynatrace instrumentation

Every FastAPI route and every agent tool call is instrumented with OTel spans.
The span naming convention is:

```
rosa.handle_whatsapp      # inbound WhatsApp message
rosa.handle_call          # inbound phone call
rosa.agent.run            # ADK agent execution
tool.get_customer_memory  # Elastic customer lookup
tool.get_available_slots  # Calendar availability check
tool.book_calendar_slot   # Calendar booking write
tool.send_whatsapp_reply  # 360dialog outbound
tool.elevenlabs_tts       # ElevenLabs synthesis
tool.escalate_to_plumber  # Escalation notification
```

Custom attributes on every span:
- `business_id` — which plumber
- `channel` — whatsapp | phone
- `conversation_id`
- `customer_is_returning` — bool

---

## Hackathon submission checklist

- [ ] Rosa answers a WhatsApp message end-to-end
- [ ] Rosa answers a phone call end-to-end with ElevenLabs voice
- [ ] Rosa books a job into Google Calendar
- [ ] Rosa recalls a returning customer from Elastic
- [ ] Dave can search jobs in plain English via Elastic
- [ ] Dynatrace dashboard shows live traces during demo
- [ ] Nuxt dashboard shows conversation feed and bookings
- [ ] Deployed to GCP (Cloud Run + Agent Engine)
- [ ] Public GitHub repo with this README
- [ ] 3-minute demo video recorded
- [ ] Submitted to both Elastic and Dynatrace tracks by June 11

---

## Code style

- **Python:** ruff for linting, black for formatting, type hints everywhere
- **TypeScript/Vue:** ESLint + Prettier, `<script setup lang="ts">` in all components
- **No any types** in TypeScript without a comment explaining why
- **Async everywhere** in Python — all IO is async/await
- **Environment variables** — never hardcode, always via `settings.py` or `runtimeConfig`
- **Error handling** — every external call (Elastic, Calendar, Twilio, ElevenLabs, Firebase) in try/except
  with OTel span exception recording
- **firebase-admin** for Python (server-side). **nuxt-vuefire** for Nuxt (client-side). Never mix them.

## Git conventions

```
feat: add twilio phone handler
fix: elastic memory query returning empty on new customer
chore: add dynatrace span to calendar tool
docs: update CLAUDE.md with phone flow
```

Branch naming: `feat/phone-handler`, `fix/elastic-memory`, `chore/otel-spans`

---

## What NOT to build right now

If you're about to build something not in this file, stop and check.

- n8n or any workflow builder
- Stripe billing
- Multi-agent routing (Mark, Daisy, John etc.)
- Support for non-plumber verticals
- Mobile app
- SMS (WhatsApp + phone is enough)
- Custom CRM integration
- Agent Studio / visual builder (use ADK code-first only)

These are real plans. They come after the hackathon. Not now.