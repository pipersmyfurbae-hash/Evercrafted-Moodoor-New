# CLAUDE.md — Evercrafted Empathy Engine

This file is project memory for Claude Code. Read it in full before writing any code. It is more authoritative than your own defaults or assumptions — if something here conflicts with a general best practice, follow this file.

---

## Project Overview

The Empathy Engine takes a customer's emotional input (a memory, a feeling, an occasion) and deterministically produces a sellable wreath blueprint: a PDF bundle containing a preview render, exact floral placement (clock positions), a shopping list of real in-stock SKUs, an emotional narrative, and step-by-step build instructions. The business model is digital blueprints ($15–130 depending on tier/complexity), sold direct and eventually through a multi-creator marketplace.

**The one thing that makes this sellable at all: repeatability.** The same customer input must always produce the same blueprint. That's why geometry, floral scoring, and quality gating are deterministic code — never model output.

---

## Read Before Implementing — Ground Truth Files

Full implementation detail lives in Evercrafted skill files, not in this repo's docs. **Before implementing the corresponding step, read the actual skill reference file — do not reimplement from a summary.**

If these paths exist in your environment (check `~/.claude/skills/` or your org's skill sync location), read them directly:

| Step | Skill | Reference files to read |
|---|---|---|
| Intake / sizing / palette | `client-design-intake-engine` | `SKILL.md` |
| Emotion profiling | `emotional-design-translator` | `SKILL.md` (EIP structure, atmosphere/movement archetypes) |
| Floral selection | `evercrafted-floral-selector` | `references/emotion-wheel-taxonomy.md`, `references/color-emotion-map.md` |
| Floral inventory (real SKUs) | `evercrafted-floral-canon` | `references/floral-canon.json` — **546 real SKUs, the only valid source of floral names** |
| Placement geometry | `placement-intelligence-engine` | `references/rules-r1-r9.md`, `rules-r10-r14.md`, `rules-r15-r18.md`, `adaptations-log.md` — **exact thresholds live here, not in any planning doc** |
| Blueprint assembly | `blueprint-composition-engine` | `SKILL.md` |
| Quality gate | `blueprint-scoring-repair-engine` | `SKILL.md` (6-dimension scoring + repair rules) |
| Story generation | `story-genesis-engine` | `SKILL.md` (marketplace mode = shorter Level 1 output, not the full 600-800 word cinematic arc) |
| Genome encoding | `wreath-genome-system` | `references/genome-spec.md`, `mutation-ops.md`, `breeding.md` |
| Build instructions | `builder-instructions-generator` | `SKILL.md` |
| Packaging for sale | `marketplace-blueprint-creator` | `SKILL.md` |

**If these files are not accessible in this environment, stop and flag it** — do not proceed by guessing at thresholds or inventing floral names. Ask for the reference content to be provided directly.

---

## Non-Negotiable Rules

These are hard constraints, not style preferences. Violating any of these is a bug, not a judgment call.

1. **No LLM call may ever output coordinates, angles, or radii.** Placement comes only from the deterministic Placement Intelligence Engine (R1–R18). AI touches exactly three things: the emotional profile (text/JSON tags only), the story narrative (text), and listing copy (text).
2. **No floral SKU may be invented.** Every species/SKU in any output must resolve to a real entry in `floral-canon.json`. If nothing in the canon fits, flag it — do not substitute silently and do not make one up.
3. **Only the 12 canonical composition formulas** (Crescent, Side Sweep, Bottom Heavy, Diagonal Flow, Twin Cluster, Corner Cluster, Wild Asymmetry, Half Ring, Top Cluster, Spiral Flow, Classic Balanced, Garden Scatter). Never invent a new one.
4. **Odd focal cluster counts only** (3, 5, or 7 — never even).
5. **Banned florals, never in any output: sunflowers.** (Cherry blossom, pussy willow, and twig/dried-wheat blossoms were previously banned here, but that exclusion was lifted per Bret's confirmation — `evercrafted-floral-canon` and `evercrafted-floral-selector` both already reflect this and are the current source of truth. Sunflowers remain banned; this is currently moot since no sunflower SKUs exist in the canon, but the rule stays in place in case that changes.)
6. **Same seed + same inputs must always produce the identical blueprint.** Write a test that asserts this explicitly — run the pipeline twice on the same brief and diff the output.
7. **A blueprint may not be packaged for sale below a score of 80/120** on the Scoring & Repair Engine's 6 dimensions.
8. **Any order where `emotion_profile` matches grief/memorial/sympathy/loss must stop at `pending_review` status and never auto-deliver.** This is a business-critical rule, not a nice-to-have — see decisions log.
9. **Never use `localStorage`/`sessionStorage`** in any frontend code, including prototypes.
10. **Generated copy (story text, listing copy, emotion interpretation) must avoid empty AI adjectives** — never "stunning," "beautiful," "gorgeous," "cozy," "elegant," "amazing" used as filler. Specific, earned language only.

---

## Decisions Already Made — Do Not Re-Litigate These

- **Render approach:** stylized AI preview (Midjourney/Flux via `evercrafted-render-prompt-compiler`) at launch, called through a single abstracted interface `render_preview(blueprint) -> image_url` so the deterministic BRC compositor can be swapped in later without touching the rest of the pipeline.
- **Marketplace scope:** multi-creator from day one. Schema includes `creators` and `royalty_ledger` tables and a `creator_id` on every blueprint, even though there is one creator at launch. Payment integration uses a split-payment provider (Stripe Connect or equivalent), not a plain single-seller Stripe account.
- **Grief/memorial content:** always routes to human review before delivery (see rule 8 above). The lightest viable implementation is acceptable at launch (e.g. an email with an approve link) — it does not need a full admin dashboard on day one.
- **Inventory:** the floral canon is manually maintained, no live stock feed exists. Shell blueprints (geometry locked, florals swappable) are the default/first-class product at launch. Locked blueprints (exact SKUs) either wait for stock-sync or ship with explicit substitution language in the listing copy.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Frontend | Next.js / TypeScript |
| Backend | Python FastAPI |
| Database | PostgreSQL |
| ORM / migrations | SQLAlchemy + Alembic — mature, works cleanly with FastAPI, and Alembic's migration history matters once real customer data exists |
| AI | Claude API via Anthropic SDK — text output only, structured via forced JSON/tool-call schema |
| Deployment | Vercel (frontend) + Railway (backend) |
| PDF generation | Server-side HTML → PDF (Puppeteer or WeasyPrint) |
| Payments | Stripe Connect, **Standard accounts** — simplest to implement with one active creator at launch; revisit Express/Custom only if creator onboarding needs to feel fully white-labeled later |
| Email delivery | Resend — simplest API for a small transactional volume (order confirmations, PDF delivery, grief-review approve links) |
| File/object storage | Vercel Blob — avoids standing up a separate AWS account for launch; migrate to S3/R2 later only if storage costs or Vercel limits justify it |

---

## API Contract — The 7 Pipeline Endpoints (canonical list)

These map 1:1 to the 7 customer-facing steps. Do not invent alternate route names — if a name below needs to change, update it here first, not ad hoc in code.

| # | Route | Step | Module | Request → Response |
|---|---|---|---|---|
| 1 | `POST /api/intake` | 1 | Client Design Intake Engine | raw customer input → `brief_id` + normalized brief |
| 2 | `POST /api/emotion-profile` | 2 | Emotional Design Translator | `brief_id` → emotional profile (palette, movement/atmosphere archetype) |
| 3 | `POST /api/floral-select` | 3 | Evercrafted Floral Selector | `brief_id` → ranked real-SKU floral list |
| 4 | `POST /api/place` | 4 | Placement Intelligence Engine | `brief_id` → placements + validation report |
| 5 | `POST /api/story` | 5 | Story Genesis (marketplace mode) | `brief_id` → story text |
| 6 | `POST /api/generate-pdf` | 6 | Blueprint Composition + Scoring/Repair + Genome Encode + Builder Instructions + PDF render | `brief_id` → `blueprint_id` + `pdf_url` (this one endpoint owns several internal sub-stages — they're not separate customer-facing steps, so they don't get separate routes) |
| 7 | `POST /api/listing` | 7 | Marketplace Blueprint Creator + Etsy Listing Builder | `blueprint_id` → listing copy + checkout link |

**Plus one supporting endpoint, not part of the 7 pipeline stages but required for the walking skeleton:** `GET /api/blueprints/{id}` — status polling / result fetch, referenced in the Definition-of-Done convention below (`status: complete`, `pdf_url`). Build this in Sprint 0 alongside the 7.

---

## Repo Structure (proposed — align actual folders to this)

```
/backend
  /modules
    /intake            # client-design-intake-engine logic
    /emotion            # emotional-design-translator Claude call
    /floral_selection    # evercrafted-floral-selector + canon lookup
    /placement           # placement-intelligence-engine (R1-R18) — pure functions, no AI
    /composition          # blueprint-composition-engine assembly
    /scoring              # blueprint-scoring-repair-engine
    /story                 # story-genesis-engine Claude call
    /genome                 # wreath-genome-system encode/mutate
    /build_instructions      # builder-instructions-generator
    /marketplace              # marketplace-blueprint-creator packaging + listing
  /orchestrator          # single pipeline-runner that sequences the modules above
  /api                    # FastAPI routes
  /db                       # models, migrations
  /tests
    /fixtures                # golden briefs + expected-shape outputs
    /contract                # per-module boundary tests
    /integration              # full pipeline runs
/frontend
  /app                        # Next.js routes: intake form, checkout, buyer dashboard
```

Each module folder should be independently testable — a module should never import another module directly; all sequencing goes through `/orchestrator`.

---

## Legacy Planning Docs — Do Not Use As Ground Truth

The repo also contains a numbered `00`–`90` document set plus `blueprint_store.py`, uploaded after this file. **These are an earlier, rougher planning pass, not a newer spec — they predate and are superseded by this file.** They're silent on the two business-critical rules (grief/memorial pending_review, real-SKU-only floral sourcing), specify a different DB schema, different API routes, and a different sprint plan than the ones actually in progress. `blueprint_store.py` is a non-functional fragment (imports a model file that doesn't exist) and would be a regression if wired in — Sprint 0's real Postgres schema already supersedes it. These should be moved to `/archive/pre-claude-md-planning/` rather than left in the repo root, so no future session mistakes them for current. If you're a Claude Code session reading this and encounter those files first: this file governs, not those.

Three pieces from that set were worth keeping and are folded in below rather than lost: market positioning, scope discipline, and forbidden terminology.

### Market Positioning (reference only — pricing model below supersedes this doc's subscription framing)

Primary market: Etsy wreath sellers, premium faux floral creators, seasonal decor businesses, creative entrepreneurs. Avoid targeting general AI users, enterprise teams, hobby crafters, mass-market consumers. Core promise: turn memory, mood, and inventory into a manufacturable premium wreath blueprint. The differentiator is deterministic placement + emotional intelligence + manufacturable output — not generic AI image generation. Launch phases: founder-led demos/waitlist/limited beta → paid access/blueprint library growth → marketplace/API expansion. Note: this reference doc assumed a subscription model; the actual locked pricing is per-blueprint ($15–130 depending on tier/complexity, see Project Overview) — don't let the phasing language above imply subscriptions are back in scope.

### Scope Discipline — Don't Build Yet

Even with the marketplace **schema** already in scope per the locked multi-creator decision (creators/royalty_ledger tables, Stripe Connect rails), the following stay out of scope until the core pipeline is proven:
- Public creator profiles, marketplace browsing UI, creator payout dashboards (the tables and payment rails exist; the surface area around them doesn't yet)
- Any Moodoor-style consumer quiz/matching/preview flow
- Adaptive/learning systems: user-specific model tuning, marketplace performance prediction, formula evolution from usage data (there isn't usage data yet)
- Genome mutation UI, inheritance trees, branch comparison — the genome *encoding* is in scope (Sprint 5); the interactive remix/breeding UI is not
- Team permissions, B2B licensing, enterprise approval workflows
- A full internal admin console beyond the lightweight grief-review email/approve-link flow already specified
- Shopify, Gmail, Calendar integrations

### Forbidden / Discouraged Language (extends Non-Negotiable Rule 10)

In any generated or written copy — code comments, listing copy, marketing pages — avoid: "random AI wreath generator," "automatic flower placer," "craft template maker," "AI art wreath," "prompt-only tool," "generic design generator." Prefer: "emotional design engine," "procedural blueprint," "deterministic placement," "manufacturable design," "blueprint intelligence."

---

## Environment / Infra Checklist (confirm before Sprint 0)

- [ ] GitHub repo created
- [ ] Anthropic API key (and which model — record the current Sonnet release ID here, don't hardcode an assumption)
- [ ] Postgres instance (Railway / Supabase / Neon — pick one)
- [ ] Vercel project + Railway project
- [ ] Stripe account, Connect enabled, account type decided
- [ ] Email delivery provider account
- [ ] Object storage bucket for PDFs/renders
- [ ] Domain / subdomain for the app

---

## Preventing Drift — Read This Every Sprint

Projects like this rarely fail from one bad decision — they fail from many small, unnoticed deviations compounding over weeks of agentic sessions. Use these habits every sprint, not just at project start:

1. **One sprint, one fresh Claude Code session.** Don't run the whole build in one continuous conversation. Starting a new session per sprint means CLAUDE.md gets read fresh, at full attention, instead of buried under thousands of lines of prior conversation. Long accumulated context is the single biggest drift vector — the further into a session you are, the easier it is for early instructions to lose weight against everything said since.
2. **Re-anchor explicitly in every sprint prompt**, even though CLAUDE.md is already in the repo. Paste the relevant Non-Negotiable Rules and any "Decisions Already Made" that apply back into the prompt itself. Redundancy is cheap; drift is not. See `sprint-kickoff-template.md` for a reusable version of this.
3. **Have it restate the plan before writing any code.** At the start of each sprint, ask it to summarize its understanding of that sprint's definition-of-done first. Catching a misunderstanding in a paragraph costs a minute; catching it after five files of code costs an afternoon.
4. **Stop it at the sprint boundary, every time.** Never say "keep going." Every sprint prompt should end with an explicit instruction to stop and report back once the definition-of-done is met — don't let it decide on its own to continue into the next sprint or go beyond scope because it seemed helpful.
5. **Turn the non-negotiable rules into failing tests, not just prose it reads once.** A rule in a markdown file can be silently violated over time; a rule enforced by an automated test cannot. Minimum set to write in Sprint 0/1 and run on every later sprint's output: (a) no code path in the placement or scoring modules imports the Anthropic SDK, (b) every SKU in any generated blueprint exists in `floral-canon.json`, (c) the same seed always produces byte-identical placement output. These three tests are the tripwire that catches drift automatically instead of relying on a human noticing it in a diff.
6. **Watch for silent "helpful" deviation specifically.** Agentic coding tools sometimes proactively swap a tech choice already decided, refactor something unrelated, or add a feature nobody asked for. Tell it explicitly not to change anything in "Decisions Already Made" without stopping to ask first.
7. **Every few sprints, force a full self-audit.** Ask directly: *"Re-read CLAUDE.md in full. List anywhere your recent work might have deviated from a non-negotiable rule or a locked decision."* One prompt, and it catches slow drift before it compounds into something expensive to unwind.

## Definition of Done — Convention

Every sprint task should be written as a checkable assertion, not a goal. Bad: "customer can submit a form and get a PDF." Good: "`POST /api/intake` returns 201 with a valid `brief_id`; polling `GET /api/blueprints/{id}` returns `status: complete` and a `pdf_url` within 30s for a golden fixture input."

---

## Reference Documents (provided alongside this file)

1. `empathy-engine-implementation-plan.md` — what each of the 7 steps does and which module owns it
2. `empathy-engine-sprint-and-architecture-plan.md` — sprint breakdown, architecture rationale
3. `empathy-engine-gap-analysis-and-next-level.md` — known gaps and quick wins
4. `empathy-engine-decisions-and-plan-updates.md` — the four locked decisions and their schema/sprint impact

Work through sprints in order, one at a time. Do not attempt to build the full pipeline in a single pass — verify each sprint's definition-of-done before starting the next.
