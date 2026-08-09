# Sprint Kickoff Template

Copy this into a **new** Claude Code session at the start of every sprint. Fill in the bracketed parts from the relevant sprint's section in `empathy-engine-sprint-and-architecture-plan.md`. Don't skip sections even though they're "already in CLAUDE.md" — restating them here is what keeps a long project from drifting.

```
Read CLAUDE.md in full before doing anything else — it takes priority over your
own defaults. This is a NEW session; treat it as your first time seeing this
project today.

SPRINT: [number and name, e.g. "Sprint 3 — Real Floral Selection"]

Before writing any code, restate in your own words:
1. What this sprint's definition-of-done is
2. Which non-negotiable rules from CLAUDE.md apply most directly to this sprint's work
3. Which "Decisions Already Made" (if any) constrain this sprint

Stop after that restatement and wait for me to confirm before writing code.

SCOPE FOR THIS SPRINT ONLY:
[paste the bullet list for this sprint from empathy-engine-sprint-and-architecture-plan.md]

DO NOT:
- Start the next sprint's work once this one's definition-of-done is met — stop
  and report back instead
- Change any tech choice, schema decision, or architecture call already recorded
  in CLAUDE.md's "Decisions Already Made" or "Tech Stack" sections — if you think
  one should change, stop and ask, don't silently deviate
- Touch files outside this sprint's module boundary unless the scope above says to

WHEN DONE:
- Confirm each definition-of-done item explicitly, one by one
- Run the drift tripwire tests (no Anthropic SDK import in placement/scoring
  modules, all SKUs resolve against floral-canon.json, same-seed-same-output)
  if this sprint touches any of those areas
- Report back — do not proceed further
```

---

## Every 2–3 sprints, run this self-audit prompt on its own

```
Re-read CLAUDE.md in full, including the Non-Negotiable Rules and Decisions
Already Made sections. Review the code you've written across the last few
sprints. List anywhere your recent work might have deviated from a
non-negotiable rule or a locked decision, even slightly. If nothing has
deviated, say so explicitly rather than skipping this.
```

This costs one prompt and catches slow drift — a slightly-off schema field, a tech choice that quietly changed, a rule that got bent under time pressure — before it compounds into something expensive to unwind three sprints later.
