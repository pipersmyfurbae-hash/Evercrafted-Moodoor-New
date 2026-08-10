# Pre-CLAUDE.md planning documents — superseded, not current spec

**Nothing in this folder is ground truth. `/CLAUDE.md` governs.**

These files were uploaded to the repo *after* CLAUDE.md but represent an
earlier, rougher planning pass. Later upload date, earlier substance — which is
exactly the trap: a future session finding them in the repo root could
reasonably assume "newer file = newer spec" and build against them.

They are kept rather than deleted because parts remain useful as history, and
because three pieces were worth preserving — market positioning, scope
discipline, and forbidden terminology — which have been folded into CLAUDE.md
directly rather than left here to rot.

## Why they were archived

**Silent on both business-critical rules.** No mention of the grief/memorial
`pending_review` gate (CLAUDE.md Rule 8) or real-SKU-only floral sourcing
(Rule 2). A session following these would ship a pipeline that auto-delivers
memorial blueprints and invents floral names — the two failures the current
rules exist to prevent.

**Self-contradicting drafts.** Two pairs of files disagree with each other:

| Pair | Disagreement |
|---|---|
| `03_EVERCRAFTED_MVP_SCOPE.md` vs `03_EVERCRAFTED_MVP_SCOPE copy.md` | 120 differing lines |
| `71_DATABASE_TABLE_DEFINITIONS.sql` vs `71_DATABASE_TABLE_DEFINITIONS.sql copy` | 178 differing lines |

Neither pair is marked as the authoritative one.

**Conflicting architecture.** A different DB schema, different API route names,
and a different sprint plan than the ones actually in progress. The live API
contract is the 7-endpoint table in CLAUDE.md; the live schema is
`backend/db/models.py` plus its Alembic migration.

**`blueprint_store.py` does not run.** Line 6 is
`from models.blueprint import Blueprint, BlueprintCreateInput`, and no `models`
package exists anywhere in the repo — it fails immediately with
`ModuleNotFoundError: No module named 'models'`. It is a fragment of a design
that was never completed. Wiring it in would be a regression: it is an
in-memory dict store, while Sprint 0 already delivers a real Postgres schema
with migrations and constraints.

## If you are a Claude Code session reading this

You have found the wrong folder. Read `/CLAUDE.md`, then
`/empathyenginemasterroadmap.md` for the sprint plan. Ground truth for
implementation detail lives in the Evercrafted skill reference files listed in
CLAUDE.md's table, not here.
