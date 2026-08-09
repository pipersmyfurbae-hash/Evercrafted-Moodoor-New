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
