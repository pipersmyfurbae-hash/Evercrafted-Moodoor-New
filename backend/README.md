# Backend — Empathy Engine

Sprint 0 scaffolding. No pipeline logic yet; the modules are empty packages
with their sprint ownership and AI/deterministic boundary recorded in each
`__init__.py`.

## Running it

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'

# Postgres connection string — never commit one.
export DATABASE_URL="postgresql+psycopg://user:pass@host:5432/dbname"

.venv/bin/alembic upgrade head
.venv/bin/pytest
.venv/bin/uvicorn backend.api.main:app --reload
```

Tests that need a database skip when `DATABASE_URL` is unset. The three drift
tripwires do not — they run anywhere.

## Layout

```
backend/
  config.py          policy constants — banned florals, score gate, review emotions
  schemas/           shared contracts (Pydantic). Not a module; modules may import it.
  modules/           the 10 pipeline modules. None may import another.
  orchestrator/      the only place modules are sequenced. Wired in Sprint 1.
  api/               FastAPI app. Pipeline routes pending the CLAUDE.md contract table.
  db/                models, session, Alembic migrations
  data/              vendored floral-canon.json snapshot
  tests/
    tripwires/       the three drift guards — run these on every sprint's output
    contract/        module boundaries, schema rules, migration parity
    integration/     full pipeline runs (Sprint 1 onward)
    fixtures/        golden briefs. Every SKU here is real.
```

## The drift tripwires

From CLAUDE.md, "Preventing Drift" item 5. Each has been verified to fail when
its rule is violated — a tripwire that cannot fail guards nothing.

| Tripwire | Rule | File |
|---|---|---|
| No LLM SDK in placement or scoring | 1 | `tests/tripwires/test_no_anthropic_sdk.py` |
| Every SKU resolves against the canon | 2 | `tests/tripwires/test_sku_resolution.py` |
| Same seed, byte-identical output | 6 | `tests/tripwires/test_deterministic_seed.py` |

`tests/contract/test_module_isolation.py` supports the first: if modules could
import each other, placement could reach an LLM one hop away and the static
scan would still pass.

## The vendored canon — refresh process

`backend/data/floral-canon.json` is a snapshot. Upstream
(`evercrafted-floral-canon/references/floral-canon.json`) stays authoritative;
the snapshot exists so the SKU tripwire runs in CI with no skills directory
mounted. `test_vendored_snapshot_matches_upstream` fails whenever the two
differ and upstream is reachable, so drift surfaces on the next test run
rather than whenever someone notices.

To refresh:

```bash
python scripts/refresh_canon.py            # report the diff, change nothing
python scripts/refresh_canon.py --apply    # update the snapshot
pytest backend/tests/tripwires             # confirm nothing broke
```

The report names every SKU added and removed and every species change. If the
count moved, it tells you which constant in
`tests/tripwires/test_sku_resolution.py` to update — those counts are pinned on
purpose, so a change in manually-maintained stock has to be acknowledged rather
than absorbed silently.

**A removed SKU is the case that hurts.** A blueprint already sold may
reference it, and Rule 2 forbids silent substitution, so the script warns
loudly instead of treating it as a count change. Those designs need a decision,
not an auto-fix.

## What the canon actually contains

Worth knowing before Sprint 3, because the headline number is misleading:

| | |
|---|---|
| Rows in the file | 546 |
| **Distinct SKUs** | **471** |
| SKUs appearing twice | 75 |

`total_skus_in_inventory: 546` counts rows, not SKUs — so CLAUDE.md's "546 real
SKUs" overstates buyable inventory by 16%. Any COGS or "how much do we stock"
figure taken from the declared number is wrong by that much.

The 75 duplicates are benign in the way that matters: **product name and price
never disagree**, so deduplicating by SKU never drops a real stem. They do
disagree on classification — 43 carry two colour names (`Magenta Pink` vs
`Vibrant Fuchsia`), 28 carry two roles (a peony tagged both `filler` and
`focal`).

That is a live hazard for Sprint 3, whose three-phase algorithm keys on exactly
colour and role. The loader resolves it by taking the first row deterministically
so the ambiguity can never surface as non-reproducible output under Rule 6 — but
first-wins is arbitrary, not a judgment that the first annotation is right.
`canon.annotation_conflicts("primary_role")` lists them for whoever resolves it.

## Two things to know before Sprint 4 and Sprint 5

**Placement is a stub.** `modules/placement` has a real seeded RNG
(mulberry32) but its geometry is a placeholder, and every position it returns
is marked `stub=True`. `test_placement_output_is_still_marked_a_stub` fails the
moment real geometry lands — deliberately, as a prompt to re-check the
determinism guarantees against the real engine. Implement R1–R18 from the
reference files directly, never from a summary.

**The banned-floral lift is not fully propagated.** Cherry blossom and pussy
willow are allowed; `floral-canon.json` records the lift and both are live in
the canon. 17 skill files still assert the old ban. Two have teeth:
`blueprint-scoring-repair-engine` D6 docks 5 of 120 points for their presence
(inside the ≥80 packaging gate), and `wreath-genome-system/references/
breeding.md` strips them from any child genome. Both need reconciling before
Sprint 5 implements scoring and genome.
