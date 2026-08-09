"""TRIPWIRE (a): no AI in the deterministic modules.

CLAUDE.md Rule 1 -- no LLM call may ever output coordinates, angles, or
radii. Placement geometry and quality scoring must be deterministic code.

Checked two ways, because either alone is escapable:
  - statically, by parsing the AST, which catches an import that is written
    but never executed
  - dynamically, by importing the module in a clean interpreter and looking
    at sys.modules, which catches an import reached through a helper the
    static scan did not follow
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

from backend.config import BACKEND_ROOT

# Modules that must never reach an LLM.
DETERMINISTIC_MODULES = ("placement", "scoring")

# Import roots that indicate an LLM client. `anthropic` is the SDK named in
# the tech stack; the others are here so that quietly swapping providers
# fails this test too, rather than sliding past a check that only knew one
# vendor's name.
FORBIDDEN_IMPORT_ROOTS = frozenset(
    {"anthropic", "openai", "google.generativeai", "cohere", "mistralai", "litellm"}
)


def _python_files(module_name: str) -> list[Path]:
    module_dir = BACKEND_ROOT / "modules" / module_name
    assert module_dir.is_dir(), f"module directory missing: {module_dir}"
    return sorted(module_dir.rglob("*.py"))


def _imported_roots(source: str, filename: str) -> set[str]:
    tree = ast.parse(source, filename=filename)
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                roots.add(node.module)
    return roots


def _violates(dotted: str) -> bool:
    parts = dotted.split(".")
    return any(
        ".".join(parts[: i + 1]) in FORBIDDEN_IMPORT_ROOTS for i in range(len(parts))
    )


@pytest.mark.parametrize("module_name", DETERMINISTIC_MODULES)
def test_no_llm_sdk_imported_statically(module_name: str) -> None:
    offenders: list[str] = []
    for path in _python_files(module_name):
        for dotted in _imported_roots(path.read_text(), str(path)):
            if _violates(dotted):
                offenders.append(f"{path.relative_to(BACKEND_ROOT.parent)}: {dotted}")

    assert not offenders, (
        f"backend/modules/{module_name} imports an LLM SDK:\n  "
        + "\n  ".join(offenders)
        + "\n\nCLAUDE.md Rule 1: placement and scoring are deterministic. "
        "Geometry and quality gating never come from a model."
    )


@pytest.mark.parametrize("module_name", DETERMINISTIC_MODULES)
def test_no_llm_sdk_present_after_import(module_name: str) -> None:
    """Import the module in a clean interpreter and inspect sys.modules.

    Catches an SDK pulled in transitively -- through a shared helper, a
    plugin registry, or a conditional import the AST scan cannot follow.
    """
    probe = (
        "import sys, json;"
        f"import backend.modules.{module_name};"
        "print(json.dumps(sorted(m for m in sys.modules "
        f"if m.split('.')[0] in {sorted(FORBIDDEN_IMPORT_ROOTS)!r})))"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        cwd=BACKEND_ROOT.parent,
    )
    assert result.returncode == 0, (
        f"could not import backend.modules.{module_name}:\n{result.stderr}"
    )
    leaked = result.stdout.strip()
    assert leaked == "[]", (
        f"importing backend.modules.{module_name} loaded an LLM SDK: {leaked}\n"
        "It reached one indirectly. CLAUDE.md Rule 1."
    )
