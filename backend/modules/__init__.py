"""Pipeline modules.

Each module is independently testable and MUST NOT import another module.
All sequencing goes through backend/orchestrator (CLAUDE.md, "Repo
Structure"). That rule is enforced by
tests/contract/test_module_isolation.py.
"""
