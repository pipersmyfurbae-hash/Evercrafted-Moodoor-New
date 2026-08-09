"""Modules must not import each other.

CLAUDE.md, "Repo Structure": each module folder is independently testable;
a module never imports another module; all sequencing goes through
/orchestrator.

This is load-bearing rather than tidy. The no-LLM tripwire checks placement
and scoring for LLM imports -- if placement could import composition, and
composition imported the Anthropic SDK, the tripwire's static scan would
pass while an LLM sat one hop away from the geometry. Module isolation is
what keeps that check meaningful.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from backend.config import BACKEND_ROOT

MODULES_ROOT = BACKEND_ROOT / "modules"

EXPECTED_MODULES = frozenset(
    {
        "intake",
        "emotion",
        "floral_selection",
        "placement",
        "composition",
        "scoring",
        "story",
        "genome",
        "build_instructions",
        "marketplace",
    }
)


def _module_names() -> list[str]:
    return sorted(
        p.name
        for p in MODULES_ROOT.iterdir()
        if p.is_dir() and not p.name.startswith("_")
    )


def test_every_expected_module_exists() -> None:
    found = set(_module_names())
    assert found == EXPECTED_MODULES, (
        f"module set drifted from CLAUDE.md's structure.\n"
        f"  missing: {sorted(EXPECTED_MODULES - found)}\n"
        f"  unexpected: {sorted(found - EXPECTED_MODULES)}"
    )


@pytest.mark.parametrize("module_name", sorted(EXPECTED_MODULES))
def test_module_is_importable_in_isolation(module_name: str) -> None:
    __import__(f"backend.modules.{module_name}")


@pytest.mark.parametrize("module_name", sorted(EXPECTED_MODULES))
def test_module_does_not_import_a_sibling(module_name: str) -> None:
    offenders: list[str] = []

    for path in sorted((MODULES_ROOT / module_name).rglob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                targets = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                # Relative imports stay inside the module; only absolute
                # ones can reach a sibling.
                targets = [node.module] if node.module and node.level == 0 else []
            else:
                continue

            for dotted in targets:
                if not dotted or not dotted.startswith("backend.modules."):
                    continue
                sibling = dotted.split(".")[2]
                if sibling != module_name:
                    rel = path.relative_to(BACKEND_ROOT.parent)
                    offenders.append(f"{rel}:{node.lineno} imports {dotted}")

    assert not offenders, (
        f"backend/modules/{module_name} imports a sibling module:\n  "
        + "\n  ".join(offenders)
        + "\n\nModules are independently testable and never import each "
        "other. Sequencing belongs in backend/orchestrator."
    )


def test_orchestrator_is_the_only_sequencer() -> None:
    """The orchestrator may import modules; nothing else outside them may.

    api/ and db/ included: a route that reaches straight into a module
    bypasses the one place the pipeline order is visible.
    """
    allowed_roots = {"orchestrator", "tests"}
    offenders: list[str] = []

    for path in sorted(BACKEND_ROOT.rglob("*.py")):
        rel = path.relative_to(BACKEND_ROOT)
        top = rel.parts[0]
        if top in allowed_roots or top == "modules":
            continue
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            names = (
                [a.name for a in node.names]
                if isinstance(node, ast.Import)
                else [node.module]
                if isinstance(node, ast.ImportFrom) and node.module and node.level == 0
                else []
            )
            for dotted in names:
                if dotted and dotted.startswith("backend.modules."):
                    offenders.append(f"backend/{rel}:{node.lineno} imports {dotted}")

    assert not offenders, (
        "code outside backend/orchestrator imports a pipeline module "
        "directly:\n  " + "\n  ".join(offenders)
    )
