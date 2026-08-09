# Empathy Engine — Master Roadmap & Checklist

The single source of truth tying together every document produced so far. This is the plain-text, editable version — check items off directly in this file as you go, or use the companion interactive tracker (`empathy-engine-build-tracker.html`) for a visual version with progress bars.

---

## Phase 0 — Legal & Business Foundations

- [ ] Trademark/name-availability check: "Evercrafted," "Empathy Engine," "Wreath Genome System"
- [ ] Terms of Service (`evercrafted-terms-of-service.md`) reviewed by a licensed attorney
- [ ] Privacy Policy (`evercrafted-privacy-policy.md`) reviewed by a licensed attorney
- [ ] Refund Policy (`evercrafted-refund-policy.md`) reviewed by a licensed attorney
- [ ] Business entity structure confirmed (LLC, sole prop, etc.)
- [ ] Sales tax / digital goods tax handling confirmed for your state
- [ ] Creator Agreement drafted — needed before opening the marketplace to other designers, not needed for launch

## Phase 1 — Infrastructure & Environment Setup

- [ ] GitHub repository created
- [ ] Postgres instance provisioned (Railway)
- [ ] Vercel project + Railway project created
- [ ] Stripe account, Connect enabled, Standard accounts configured
- [ ] Resend account for transactional email
- [ ] Vercel Blob storage bucket configured
- [ ] Confirmed Claude Code's environment can read the Evercrafted skill reference files (placement-intelligence-engine, evercrafted-floral-canon, wreath-genome-system) — or exported them if not
- [ ] Domain/subdomain configured

## Phase 2 — Sprint 0: Foundations *(Claude Code)*

- [ ] Repo scaffolded per CLAUDE.md structure
- [ ] Postgres schema created, including `creators` and `royalty_ledger` tables
- [ ] Blueprint JSON schema defined as versioned Pydantic models
- [ ] OpenAPI contract stub produced for all 7 pipeline endpoints
- [ ] Drift tripwire tests written: no Anthropic SDK in placement/scoring modules, all SKUs resolve against the floral canon, same-seed-same-output
- [ ] Reviewed by Bret before Design work begins wiring to it

## Phase 3 — Design Exploratory Pass *(Claude Design, parallel to Sprint 0)*

- [ ] Brand system applied (palette, typography, asymmetric layout)
- [ ] Intake flow concept (Step 1 emotional capture)
- [ ] Blueprint viewer / reveal screen concept
- [ ] Landing/marketing page concept
- [ ] Concepts updated against the real API contract once Sprint 0 lands
- [ ] Handoff bundle produced for Claude Code

## Phase 4 — Sprint 1: Walking Skeleton *(Claude Code)*

- [ ] Intake form live using Design's handoff screens
- [ ] Stubbed emotion profile wired
- [ ] Stubbed floral list wired
- [ ] Stubbed placement (static Crescent template) wired
- [ ] Fake blueprint JSON assembled end-to-end
- [ ] Basic PDF renders successfully
- [ ] Full deploy verified: form submission → DB → PDF, in production environment

## Phase 5 — Sprint 2: Real Intake + Emotion Translation

- [ ] Client Design Intake Engine logic implemented (brief normalization, sizing/stem scaling, 60/30/10 palette)
- [ ] Emotional Design Translator Claude API call implemented and tested
- [ ] Stub from Sprint 1 fully replaced

## Phase 6 — Sprint 3: Real Floral Selection

- [ ] 546-SKU Floral Canon loaded into Postgres
- [ ] Three-phase selection algorithm implemented (emotion candidates → color filter → fallback → season/intensity)
- [ ] Fallback logic tested against edge cases
- [ ] Output validated: every recommended floral resolves to a real SKU

## Phase 7 — Sprint 4: Placement Engine *(highest risk — give this extra time if needed)*

- [ ] R1–R18 rules implemented from the actual reference files, not from summary
- [ ] Seeded RNG (mulberry32) implemented and verified repeatable
- [ ] Coverage classes, bloom nesting, footprint spacing implemented
- [ ] Validation report (pass/warn/flag) implemented
- [ ] Same-seed-same-output drift test passes

## Phase 8 — Sprint 5: Assembly, Scoring, Story, Genome

- [ ] Blueprint Composition Engine assembles real blueprint JSON
- [ ] Scoring & Repair Engine enforces the ≥80 gate with auto-repair
- [ ] Story Genesis (marketplace-length mode) Claude call implemented
- [ ] Wreath Genome System encoding implemented
- [ ] Builder Instructions Generator implemented

## Phase 9 — Sprint 6a: Packaging + Creator/Payment Rails

- [ ] Marketplace Blueprint Creator packaging implemented (Shell type prioritized)
- [ ] Full PDF bundle finalized (preview, blueprint, genome, placement guide, story, instructions, ingredient list)
- [ ] Stripe Connect split-payment flow wired
- [ ] Creator + royalty ledger functional end-to-end

## Phase 10 — Sprint 6b: Delivery + Grief Review Queue

- [ ] Order status state machine implemented: generated → pending_review → approved → delivered
- [ ] Grief/memorial/sympathy/loss auto-detection routes to review queue
- [ ] Lightweight review notification (email + approve link) implemented
- [ ] Etsy Listing Builder output wired, if selling there
- [ ] Full checkout → delivery flow tested end-to-end

## Phase 11 — Sprint 7: QA, Regression & Soft Launch

- [ ] 15–20 golden fixture briefs (spanning grief, joy, peace, celebration) run through the full pipeline
- [ ] Contract tests passing at every module boundary
- [ ] Rate limiting / abuse protection live on the intake endpoint
- [ ] Manual concierge review active for the first batch of real orders
- [ ] North-star metrics defined and instrumented (conversion rate, refund-rate ceiling, CAC/LTV targets)
- [ ] Soft launch to a small list

## Phase 12 — Pre-Launch Validation *(can start anytime — earlier is better)*

- [ ] 5–10 real people tested on the Step 1 intake questions
- [ ] Feedback incorporated into intake copy/flow before it's fully built out

## Ongoing — Drift Prevention Discipline (every sprint, not a one-time task)

- [ ] Use `sprint-kickoff-template.md` to open every new Claude Code session
- [ ] Stop and review at every sprint boundary before allowing continuation
- [ ] Run the self-audit prompt every 2–3 sprints
- [ ] Personally read the diff at each sprint boundary, especially near the non-negotiable rules
